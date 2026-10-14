#!/usr/bin/env python3
"""Расчёт поставки на «Склад WB» (FBO) по остаткам и заказам Wildberries.

Токен берётся из переменной окружения WB_API_TOKEN
(категории «Аналитика», «Статистика», «Контент»).

Запуск: python3 wb_supply_plan.py [--lead 10] [--cover 30] [--safety 7]
                                  [--window 14] [--lag 10] [--out plan.csv]

Логика (по каждому размеру):
  v      — заказы FBO в день за последние --window дней (включая отказы:
           товар уходит со склада в момент заказа);
  b      — процент выкупа артикула по «созревшим» заказам (старше --lag дней);
  H      — горизонт = срок доставки поставки (--lead) + период покрытия (--cover);
  расход = v·H, возвраты будущих заказов = v·(H − lag)·(1 − b);
  уже едет обратно = «едут от клиента» + «едут к клиенту»·(1 − b);
  страховой запас  = v·b·--safety;
  к поставке = расход − будущие возвраты + страховой − остаток − едет обратно.
"""
import argparse
import csv
import json
import math
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date, timedelta

STOCKS_URL = "https://seller-analytics-api.wildberries.ru/api/analytics/v1/stocks-report/wb-warehouses"
ORDERS_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={d}&flag=0"
CARDS_URL = "https://content-api.wildberries.ru/content/v2/get/cards/list"


def call(url, token, body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": token, "Content-Type": "application/json"}
    for _ in range(5):
        req = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get("X-Ratelimit-Retry") or 60) + 1)
    sys.exit(f"Превышен лимит запросов: {url}")


def fetch_stocks(token):
    items, offset = [], 0
    while True:
        page = call(STOCKS_URL, token, {"limit": 1000, "offset": offset})["data"]["items"]
        items += page
        if len(page) < 1000:
            return items
        offset += 1000


def fetch_cards(token):
    cards, cursor = [], {"limit": 100}
    while True:
        resp = call(CARDS_URL, token, {"settings": {"cursor": cursor, "filter": {"withPhoto": -1}}})
        cards += resp["cards"]
        if len(resp["cards"]) < 100:
            return cards
        cursor = {"limit": 100, "updatedAt": resp["cursor"]["updatedAt"], "nmID": resp["cursor"]["nmID"]}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--lead", type=int, default=10, help="дней до приёмки поставки на складе")
    p.add_argument("--cover", type=int, default=30, help="на сколько дней продаж везём")
    p.add_argument("--safety", type=int, default=7, help="страховой запас, дней чистых продаж")
    p.add_argument("--window", type=int, default=14, help="окно расчёта скорости заказов, дней")
    p.add_argument("--lag", type=int, default=10, help="дней до возврата невыкупа на склад")
    p.add_argument("--out", default=f"supply_plan_{date.today().isoformat()}.csv")
    a = p.parse_args()

    token = os.environ.get("WB_API_TOKEN")
    if not token:
        sys.exit("Не задана переменная окружения WB_API_TOKEN")

    today = date.today()
    stocks = [s for s in fetch_stocks(token) if s["warehouseName"] == "Склад WB"]
    cards = fetch_cards(token)
    orders = call(ORDERS_URL.format(d=(today - timedelta(days=60)).isoformat()), token)
    orders = [o for o in orders if o.get("warehouseType") == "Склад WB"]

    # chrtId <-> баркод/размер из карточек
    size_by_chrt, chrt_by_barcode, name_by_nm = {}, {}, {}
    for c in cards:
        name_by_nm[c["nmID"]] = (c.get("vendorCode", ""), c.get("subjectName", ""))
        for s in c.get("sizes", []):
            size_by_chrt[s["chrtID"]] = s.get("techSize") or s.get("wbSize") or ""
            for sku in s.get("skus", []):
                chrt_by_barcode[sku] = s["chrtID"]

    # процент выкупа по созревшим заказам с подтяжкой к среднему при малой выборке
    since_v = (today - timedelta(days=a.window)).isoformat()
    lo, hi = (today - timedelta(days=45)).isoformat(), (today - timedelta(days=a.lag)).isoformat()
    mature = defaultdict(lambda: [0, 0])
    velocity = defaultdict(int)
    for o in orders:
        d = o["date"][:10]
        name_by_nm.setdefault(o["nmId"], (o.get("supplierArticle", ""), o.get("subject", "")))
        if lo <= d < hi:
            mature[o["nmId"]][0] += 1
            mature[o["nmId"]][1] += 0 if o["isCancel"] else 1
        if d >= since_v and d < today.isoformat():
            chrt = chrt_by_barcode.get(o.get("barcode"))
            key = (o["nmId"], chrt) if chrt else (o["nmId"], "size:" + o.get("techSize", ""))
            velocity[key] += 1
    tot_n = sum(n for n, _ in mature.values()) or 1
    b_avg = sum(k for _, k in mature.values()) / tot_n
    prior = 20
    buyout = {nm: (k + prior * b_avg) / (n + prior) for nm, (n, k) in mature.items()}

    stock_by_key = {(s["nmId"], s["chrtId"]): s for s in stocks}
    keys = set(stock_by_key) | set(velocity)
    H = a.lead + a.cover
    rows = []
    for key in keys:
        nm, chrt = key
        s = stock_by_key.get(key, {})
        qty, to_cl, from_cl = s.get("quantity", 0), s.get("inWayToClient", 0), s.get("inWayFromClient", 0)
        v = velocity.get(key, 0) / a.window
        b = buyout.get(nm, b_avg)
        back_now = from_cl + to_cl * (1 - b)
        need = v * H - v * max(H - a.lag, 0) * (1 - b) + v * b * a.safety - qty - back_now
        net = v * b
        cover_days = (qty + back_now) / net if net else None
        size = size_by_chrt.get(chrt, "") if isinstance(chrt, int) else chrt[5:]
        art, subj = name_by_nm.get(nm, ("", ""))
        rows.append({
            "Артикул продавца": art, "Предмет": subj, "nmId": nm, "Размер": size,
            "Остаток Склад WB": qty, "Едут к клиенту": to_cl, "Едут от клиента": from_cl,
            "Заказов/день": round(v, 2), "Выкуп %": round(b * 100),
            "Хватит дней": round(cover_days) if cover_days is not None else "",
            "К поставке": max(0, math.ceil(need)),
        })
    rows.sort(key=lambda r: (r["Артикул продавца"], r["nmId"], str(r["Размер"])))

    with open(a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter=";")
        w.writeheader()
        w.writerows(rows)

    total = sum(r["К поставке"] for r in rows)
    print(f"# План поставки на Склад WB от {today}\n")
    print(f"Горизонт: {a.lead} дн. доставка + {a.cover} дн. продаж, страховой {a.safety} дн., "
          f"скорость за {a.window} дн., средний выкуп {b_avg:.0%}")
    print(f"Остаток на Склад WB: {sum(s['quantity'] for s in stocks)} шт, "
          f"едут к клиенту: {sum(s['inWayToClient'] for s in stocks)}, "
          f"от клиента: {sum(s['inWayFromClient'] for s in stocks)}")
    print(f"Итого к поставке: {total} шт\n")
    by_art = defaultdict(lambda: [0, 0, 0.0])
    for r in rows:
        x = by_art[r["Артикул продавца"] or str(r["nmId"])]
        x[0] += r["К поставке"]
        x[1] += r["Остаток Склад WB"]
        x[2] += r["Заказов/день"]
    print(f"{'Артикул':<40} {'остаток':>8} {'заказ/дн':>9} {'к поставке':>11}")
    for art, (need, qty, v) in sorted(by_art.items(), key=lambda x: -x[1][0]):
        if need:
            print(f"{art[:40]:<40} {qty:>8} {v:>9.1f} {need:>11}")
    print(f"\nДетально по размерам: {a.out}")


if __name__ == "__main__":
    main()
