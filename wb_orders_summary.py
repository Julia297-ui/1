#!/usr/bin/env python3
"""Сводка по заказам Wildberries за день (по умолчанию — вчера).

Токен берётся из переменной окружения WB_API_TOKEN (категория «Статистика»).
Запуск: python3 wb_orders_summary.py [YYYY-MM-DD]
"""
import json
import os
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import date, timedelta

URL = "https://statistics-api.wildberries.ru/api/v1/supplier/orders?dateFrom={d}&flag=1"


def fetch(day, token):
    req = urllib.request.Request(URL.format(d=day), headers={"Authorization": token})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def rub(x):
    return f"{x:,.0f} ₽".replace(",", " ")


def main():
    token = os.environ.get("WB_API_TOKEN")
    if not token:
        sys.exit("Не задана переменная окружения WB_API_TOKEN")
    day = sys.argv[1] if len(sys.argv) > 1 else (date.today() - timedelta(days=1)).isoformat()
    orders = [o for o in fetch(day, token) if o.get("date", "").startswith(day)]

    active = [o for o in orders if not o.get("isCancel")]
    cancelled = [o for o in orders if o.get("isCancel")]
    revenue = sum(o.get("priceWithDisc", 0) for o in active)
    paid = sum(o.get("finishedPrice", 0) for o in active)

    print(f"# Сводка по заказам WB за {day}\n")
    print(f"Заказов всего:        {len(orders)}")
    print(f"  из них отменено:    {len(cancelled)}")
    print(f"Сумма (цена со скидкой продавца): {rub(revenue)}")
    print(f"Оплачено покупателями:            {rub(paid)}")
    if active:
        print(f"Средний чек:                      {rub(revenue / len(active))}")

    by_item = defaultdict(lambda: [0, 0.0, ""])
    for o in active:
        k = o.get("supplierArticle") or str(o.get("nmId"))
        by_item[k][0] += 1
        by_item[k][1] += o.get("priceWithDisc", 0)
        by_item[k][2] = o.get("subject", "")
    print("\n## Топ-10 артикулов")
    for art, (n, s, subj) in sorted(by_item.items(), key=lambda x: -x[1][1])[:10]:
        print(f"  {art:<25} {subj:<20} {n:>4} шт  {rub(s)}")

    for title, key in (("Склады", "warehouseName"), ("Регионы", "regionName")):
        print(f"\n## {title}")
        for name, n in Counter(o.get(key) or "—" for o in active).most_common(10):
            print(f"  {name:<30} {n}")


if __name__ == "__main__":
    main()
