#!/usr/bin/env python3
"""Отчёт об остатках Wildberries.

Склады WB — Analytics API (warehouse_remains), метод асинхронный:
создаём задание -> ждём статус done -> скачиваем отчёт.
Склады продавца (FBS) — Marketplace API: список складов /api/v3/warehouses,
остатки по баркодам POST /api/v3/stocks/{warehouseId}.
Дополнительно подтягиваются заказы за последние 30 дней (Statistics API):
по ним считается спрос за 7 дней и собираются баркоды для запроса FBS-остатков.

Токен берётся из переменной окружения WB_API_TOKEN
(категории «Аналитика», «Маркетплейс» и «Статистика»).
Запуск: python3 wb_stocks_report.py [--csv stocks.csv]
"""
import csv
import json
import os
import sys
import time
import urllib.request
from collections import Counter
from datetime import date, timedelta

ANALYTICS = "https://seller-analytics-api.wildberries.ru/api/v1/warehouse_remains"
MARKETPLACE = "https://marketplace-api.wildberries.ru/api/v3"
ORDERS = "https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={d}"

# Служебные строки отчёта, которые не являются складами
NOT_WAREHOUSE = ("В пути до получателей", "В пути возвраты на склад WB", "Всего находится на складах")


def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": token})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def post(url, token, body):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": token, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def fetch_fbs(token, barcodes):
    """Остатки на складах продавца: {barcode: {имя склада: количество}}."""
    result = {}
    for wh in get(f"{MARKETPLACE}/warehouses", token):
        for i in range(0, len(barcodes), 1000):  # не больше 1000 баркодов за запрос
            chunk = barcodes[i:i + 1000]
            for st in post(f"{MARKETPLACE}/stocks/{wh['id']}", token, {"skus": chunk}).get("stocks", []):
                result.setdefault(st["sku"], {})[wh["name"]] = st["amount"]
    return result


def fetch_remains(token):
    params = "groupByNm=true&groupBySa=true&groupBySize=true&groupByBarcode=true"
    task_id = get(f"{ANALYTICS}?{params}", token)["data"]["taskId"]
    for _ in range(60):  # до ~5 минут, лимит статуса — 1 запрос в 5 секунд
        time.sleep(5)
        status = get(f"{ANALYTICS}/tasks/{task_id}/status", token)["data"]["status"]
        if status == "done":
            return get(f"{ANALYTICS}/tasks/{task_id}/download", token)
        if status in ("canceled", "purge"):
            sys.exit(f"Задание {task_id} завершилось со статусом {status}")
    sys.exit(f"Отчёт {task_id} не готов за 5 минут")


def main():
    token = os.environ.get("WB_API_TOKEN")
    if not token:
        sys.exit("Не задана переменная окружения WB_API_TOKEN")
    csv_path = sys.argv[sys.argv.index("--csv") + 1] if "--csv" in sys.argv else None

    remains = fetch_remains(token)

    month_ago = (date.today() - timedelta(days=30)).isoformat()
    since = (date.today() - timedelta(days=7)).isoformat()
    all_orders = get(ORDERS.format(d=month_ago), token)
    orders = Counter(
        o["barcode"] for o in all_orders
        if o.get("date", "")[:10] >= since and not o.get("isCancel")
    )
    info = {}  # карточки товаров, которых нет в отчёте складов WB (только FBS)
    for o in all_orders:
        info.setdefault(o["barcode"], o)
    barcodes = sorted({it.get("barcode") for it in remains if it.get("barcode")} | set(info))
    fbs = fetch_fbs(token, barcodes)

    known = {it.get("barcode") for it in remains}
    remains = remains + [
        {"vendorCode": o.get("supplierArticle", ""), "nmId": o.get("nmId"), "techSize": o.get("techSize", ""),
         "barcode": bc, "subjectName": o.get("subject", ""), "warehouses": []}
        for bc, o in info.items() if bc not in known and bc in fbs
    ]

    rows = []
    for it in remains:
        wh = {w["warehouseName"]: w["quantity"] for w in it.get("warehouses", [])}
        on_wh = wh.get("Всего находится на складах", sum(q for n, q in wh.items() if n not in NOT_WAREHOUSE))
        fbs_wh = fbs.get(it.get("barcode"), {})
        on_fbs = sum(fbs_wh.values())
        sold7 = orders.get(it.get("barcode"), 0)
        rows.append({
            "vendorCode": it.get("vendorCode", ""),
            "nmId": it.get("nmId"),
            "size": it.get("techSize", ""),
            "barcode": it.get("barcode", ""),
            "subject": it.get("subjectName", ""),
            "stockWB": on_wh,
            "stockFBS": on_fbs,
            "stock": on_wh + on_fbs,
            "toClient": wh.get("В пути до получателей", 0),
            "returning": wh.get("В пути возвраты на склад WB", 0),
            "orders7d": sold7,
            "daysLeft": round((on_wh + on_fbs) / (sold7 / 7), 1) if sold7 else None,
            "warehouses": "; ".join(f"{n}: {q}" for n, q in wh.items() if n not in NOT_WAREHOUSE and q),
            "warehousesFBS": "; ".join(f"{n}: {q}" for n, q in fbs_wh.items() if q),
        })

    total_wb = sum(r["stockWB"] for r in rows)
    total_fbs = sum(r["stockFBS"] for r in rows)
    zero = [r for r in rows if r["stock"] == 0]
    zero_sold = [r for r in zero if r["orders7d"]]
    low = sorted((r for r in rows if r["daysLeft"] is not None and 0 < r["daysLeft"] < 14), key=lambda r: r["daysLeft"])

    print(f"# Остатки WB на {date.today()}\n")
    print(f"Позиций (баркодов):      {len(rows)}")
    print(f"На складах WB:           {total_wb} шт")
    print(f"На складах продавца:     {total_fbs} шт")
    print(f"Нулевой остаток:         {len(zero)} баркодов, из них с заказами за 7 дней: {len(zero_sold)}")

    print("\n## Закончились, но есть спрос (заказы за 7 дней)")
    for r in sorted(zero_sold, key=lambda r: -r["orders7d"])[:30]:
        print(f"  {r['vendorCode']:<35} {r['size']:<6} заказов {r['orders7d']:>3}")

    print("\n## Хватит меньше чем на 14 дней")
    for r in low[:30]:
        print(f"  {r['vendorCode']:<35} {r['size']:<6} WB {r['stockWB']:>4}  FBS {r['stockFBS']:>4}  заказов/7д {r['orders7d']:>3}  дней {r['daysLeft']}")

    print("\n## Остаток по складам")
    by_wh = Counter()
    for it in remains:
        for w in it.get("warehouses", []):
            if w["warehouseName"] not in NOT_WAREHOUSE:
                by_wh[w["warehouseName"]] += w["quantity"]
    for f in fbs.values():
        for name, q in f.items():
            by_wh[f"{name} (FBS)"] += q
    for name, q in by_wh.most_common(20):
        print(f"  {name:<35} {q}")

    if csv_path:
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter=";")
            w.writeheader()
            w.writerows(rows)
        print(f"\nПолная таблица сохранена в {csv_path}")


if __name__ == "__main__":
    main()
