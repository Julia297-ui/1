#!/usr/bin/env python3
"""Отчёт об остатках Wildberries через новый метод Analytics API (warehouse_remains).

Метод асинхронный: создаём задание -> ждём статус done -> скачиваем отчёт.
Дополнительно подтягиваются заказы за последние 7 дней (Statistics API),
чтобы посчитать, на сколько дней хватит остатка.

Токен берётся из переменной окружения WB_API_TOKEN (категории «Аналитика» и «Статистика»).
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
ORDERS = "https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={d}"

# Служебные строки отчёта, которые не являются складами
NOT_WAREHOUSE = ("В пути до получателей", "В пути возвраты на склад WB", "Всего находится на складах")


def get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": token})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


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

    since = (date.today() - timedelta(days=7)).isoformat()
    orders = Counter(
        o["barcode"] for o in get(ORDERS.format(d=since), token)
        if o.get("date", "")[:10] >= since and not o.get("isCancel")
    )

    rows = []
    for it in remains:
        wh = {w["warehouseName"]: w["quantity"] for w in it.get("warehouses", [])}
        on_wh = wh.get("Всего находится на складах", sum(q for n, q in wh.items() if n not in NOT_WAREHOUSE))
        sold7 = orders.get(it.get("barcode"), 0)
        rows.append({
            "vendorCode": it.get("vendorCode", ""),
            "nmId": it.get("nmId"),
            "size": it.get("techSize", ""),
            "barcode": it.get("barcode", ""),
            "subject": it.get("subjectName", ""),
            "stock": on_wh,
            "toClient": wh.get("В пути до получателей", 0),
            "returning": wh.get("В пути возвраты на склад WB", 0),
            "orders7d": sold7,
            "daysLeft": round(on_wh / (sold7 / 7), 1) if sold7 else None,
            "warehouses": "; ".join(f"{n}: {q}" for n, q in wh.items() if n not in NOT_WAREHOUSE and q),
        })

    total = sum(r["stock"] for r in rows)
    zero = [r for r in rows if r["stock"] == 0]
    zero_sold = [r for r in zero if r["orders7d"]]
    low = sorted((r for r in rows if r["daysLeft"] is not None and 0 < r["daysLeft"] < 14), key=lambda r: r["daysLeft"])

    print(f"# Остатки WB на {date.today()}\n")
    print(f"Позиций (баркодов):      {len(rows)}")
    print(f"Всего на складах WB:     {total} шт")
    print(f"Нулевой остаток:         {len(zero)} баркодов, из них с заказами за 7 дней: {len(zero_sold)}")

    print("\n## Закончились, но есть спрос (заказы за 7 дней)")
    for r in sorted(zero_sold, key=lambda r: -r["orders7d"])[:30]:
        print(f"  {r['vendorCode']:<35} {r['size']:<6} заказов {r['orders7d']:>3}")

    print("\n## Хватит меньше чем на 14 дней")
    for r in low[:30]:
        print(f"  {r['vendorCode']:<35} {r['size']:<6} остаток {r['stock']:>4}  заказов/7д {r['orders7d']:>3}  дней {r['daysLeft']}")

    print("\n## Остаток по складам")
    by_wh = Counter()
    for it in remains:
        for w in it.get("warehouses", []):
            if w["warehouseName"] not in NOT_WAREHOUSE:
                by_wh[w["warehouseName"]] += w["quantity"]
    for name, q in by_wh.most_common(15):
        print(f"  {name:<35} {q}")

    if csv_path:
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter=";")
            w.writeheader()
            w.writerows(rows)
        print(f"\nПолная таблица сохранена в {csv_path}")


if __name__ == "__main__":
    main()
