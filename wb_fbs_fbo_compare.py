#!/usr/bin/env python3
"""Сравнение FBS и FBO (FBW) по детализации финансовых отчётов Wildberries.

Источник: POST https://finance-api.wildberries.ru/api/finance/v1/sales-reports/detailed
(замена устаревшего /api/v5/supplier/reportDetailByPeriod). Нужен токен категории «Финансы»
в переменной окружения WB_API_TOKEN.

Запуск:
    python3 wb_fbs_fbo_compare.py 2026-10-19 2026-11-04          # загрузить из API
    python3 wb_fbs_fbo_compare.py --file rows.json                # из сохранённой выгрузки
    python3 wb_fbs_fbo_compare.py 2026-10-19 2026-11-04 --save rows.json

Как определяется формат: строки «Продажа»/«Возврат» в отчёте не содержат deliveryMethod,
он есть только у строк логистики. Поэтому каждая строка привязывается к формату через srid
(идентификатор заказа), затем по officeName «Склад поставщика…» (= FBS), затем через shkId.
Если заказ не дошёл до логистики, формат определяется по смыслу операции: хранение и
расхождения при приёмке на складе WB — FBO, штрафы за срок передачи / «Штраф МП» — FBS.
Удержания (WB Продвижение и т.п.) не зависят от формата и идут в «не распределено».
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict

URL = "https://finance-api.wildberries.ru/api/finance/v1/sales-reports/detailed"
FMT = ("FBO", "FBS", "—")  # «—» = не удалось привязать


def fetch(date_from, date_to, token):
    rows, rrd = [], 0
    while True:
        body = json.dumps({"dateFrom": date_from, "dateTo": date_to,
                           "limit": 100000, "rrdId": rrd}).encode()
        req = urllib.request.Request(URL, data=body, method="POST", headers={
            "Authorization": token, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.load(r) if r.status == 200 else []
        except urllib.error.HTTPError as e:
            if e.code == 429:  # лимит ~1 запрос в минуту
                time.sleep(65)
                continue
            raise
        if not data:
            return rows
        rows += data
        rrd = data[-1]["rrdId"]
        if len(data) < 100000:
            return rows
        time.sleep(62)


def f(x):
    try:
        return float(x or 0)
    except (TypeError, ValueError):
        return 0.0


def family(method):
    m = (method or "").split(",")[0].strip()
    return {"FBW": "FBO", "FBO": "FBO", "FBS": "FBS"}.get(m, "")


def classify(rows):
    by_srid, by_shk = defaultdict(set), defaultdict(set)
    for r in rows:
        fam = family(r.get("deliveryMethod"))
        if fam:
            if r.get("srid"):
                by_srid[r["srid"]].add(fam)
            if r.get("shkId"):
                by_shk[r["shkId"]].add(fam)
    for r in rows:
        op, reason = r.get("sellerOperName", ""), r.get("bonusTypeName", "") or ""
        fam = family(r.get("deliveryMethod"))
        if op == "Удержание":
            fam = ""  # WB Продвижение и пр. — не зависят от формата
        elif not fam:
            cand = by_srid.get(r.get("srid")) if r.get("srid") else None
            if not cand and (r.get("officeName") or "").startswith("Склад поставщика"):
                cand = {"FBS"}  # отгрузка со склада продавца
            if not cand and r.get("shkId"):
                cand = by_shk.get(r["shkId"])
            cand = cand or set()
            fam = next(iter(cand)) if len(cand) == 1 else ""
        if not fam:  # заказ не доехал до логистики — определяем по смыслу операции
            if op == "Хранение" or "после приемки на складе WB" in reason:
                fam = "FBO"
            elif op == "Штраф" and ("срока передачи товара" in reason or "Штраф МП" in reason):
                fam = "FBS"
        r["_fmt"] = fam or "—"


def aggregate(rows):
    a = {k: defaultdict(float) for k in FMT}
    for r in rows:
        d, op = a[r["_fmt"]], r.get("sellerOperName", "")
        sign = {"Продажа": 1, "Возврат": -1}.get(r.get("docTypeName"), 0)
        if op in ("Продажа", "Возврат"):
            s = 1 if op == "Продажа" else -1
            d["sales_qty" if s > 0 else "ret_qty"] += r.get("quantity", 0)
            d["revenue"] += s * f(r["retailPriceWithDisc"])      # цена продавца со скидкой
            d["buyer_paid"] += s * f(r["retailAmount"])           # оплатил покупатель (после СПП)
            d["for_pay"] += s * f(r["forPay"])                    # к перечислению
            d["acquiring"] += s * f(r["acquiringFee"])
            d["tariff_x_rev"] += s * f(r["commissionPercent"]) * f(r["retailPriceWithDisc"])
        else:
            d["other_for_pay"] += f(r.get("forPay"))  # добровольные компенсации, корр. эквайринга
            d["acquiring"] += f(r.get("acquiringFee")) if op == "Корректировка эквайринга" else 0
        d["logistics"] += f(r.get("deliveryService"))
        d["deliveries"] += r.get("deliveryAmount", 0) or 0
        d["returns_logistics"] += r.get("returnAmount", 0) or 0
        d["rebill"] += f(r.get("rebillLogisticCost"))
        if op.startswith("Возмещение за выдачу и возврат"):
            d["pvz"] += f(r.get("ppvzReward"))
        d["penalty"] += f(r.get("penalty"))
        d["storage"] += f(r.get("paidStorage"))
        d["acceptance"] += f(r.get("paidAcceptance"))
        d["deduction"] += f(r.get("deduction"))
        sgn = -1 if sign < 0 else 1  # по возвратам баллы и компенсации сторнируются
        d["loyalty"] += sgn * (f(r.get("cashbackAmount")) + f(r.get("cashbackCommissionChange")))
        d["loyalty_comp"] += sgn * f(r.get("cashbackDiscount"))  # компенсация скидки — доход
        d["additional"] += f(r.get("additionalPayment"))
    for d in a.values():
        d["commission"] = d["revenue"] - d["for_pay"]               # комиссия WB + эквайринг
        d["expenses"] = (d["logistics"] + d["rebill"] + d["pvz"] + d["penalty"] + d["storage"]
                         + d["acceptance"] + d["deduction"] + d["loyalty"])
        d["net"] = (d["for_pay"] + d["other_for_pay"] + d["additional"] + d["loyalty_comp"]
                    - d["expenses"])
    return a


def sku_matched(rows):
    """Комиссия по артикулам, которые продавались в обоих форматах — честное сравнение тарифа."""
    s = defaultdict(lambda: {k: [0.0, 0.0, 0] for k in ("FBO", "FBS")})
    for r in rows:
        if r.get("sellerOperName") == "Продажа" and r["_fmt"] in ("FBO", "FBS"):
            x = s[r.get("nmId")][r["_fmt"]]
            x[0] += f(r["retailPriceWithDisc"])
            x[1] += f(r["forPay"])
            x[2] += 1
    both = {k: v for k, v in s.items() if v["FBO"][2] and v["FBS"][2]}
    out = {}
    for fmt in ("FBO", "FBS"):
        rev = sum(v[fmt][0] for v in both.values())
        fp = sum(v[fmt][1] for v in both.values())
        out[fmt] = (rev, fp, sum(v[fmt][2] for v in both.values()))
    return len(both), out


def rub(x):
    return f"{x:,.0f} ₽".replace(",", " ")


def pct(a, b):
    return f"{100 * a / b:.1f}%" if b else "—"


def report(rows):
    classify(rows)
    a = aggregate(rows)
    reports = sorted({(r["reportId"], r["dateFrom"], r["dateTo"]) for r in rows},
                     key=lambda x: (x[1], x[0]))
    print("# Сравнение FBS и FBO по финансовым отчётам WB\n")
    print(f"Период отчётов: {reports[0][1]} — {max(x[2] for x in reports)}, "
          f"отчётов: {len(reports)}, строк: {len(rows)}\n")
    o, s, u = a["FBO"], a["FBS"], a["—"]
    lines = [
        ("Продажи, шт", lambda d: f"{d['sales_qty']:.0f}"),
        ("Возвраты, шт", lambda d: f"{d['ret_qty']:.0f}"),
        ("Доля продаж (шт)", lambda d: pct(d["sales_qty"], o["sales_qty"] + s["sales_qty"])),
        ("Выручка (цена продавца со скидкой)", lambda d: rub(d["revenue"])),
        ("Средняя цена продажи", lambda d: rub(d["revenue"] / max(d["sales_qty"] - d["ret_qty"], 1))),
        ("Тарифная комиссия (средневзв.)", lambda d: f"{d['tariff_x_rev'] / d['revenue']:.1f}%" if d["revenue"] else "—"),
        ("Комиссия WB + эквайринг, ₽", lambda d: rub(d["commission"])),
        ("Комиссия WB + эквайринг, % выручки", lambda d: pct(d["commission"], d["revenue"])),
        ("  в т.ч. эквайринг", lambda d: rub(d["acquiring"])),
        ("К перечислению за товар", lambda d: rub(d["for_pay"])),
        ("Логистика", lambda d: rub(d["logistics"])),
        ("Логистика на 1 продажу", lambda d: rub(d["logistics"] / d["sales_qty"]) if d["sales_qty"] else "—"),
        ("Возмещение издержек по перемещению", lambda d: rub(d["rebill"])),
        ("Возмещение за выдачу/возврат на ПВЗ", lambda d: rub(d["pvz"])),
        ("Штрафы", lambda d: rub(d["penalty"])),
        ("Хранение", lambda d: rub(d["storage"])),
        ("Удержания (WB Продвижение и пр.)", lambda d: rub(d["deduction"])),
        ("Лояльность (баллы, участие)", lambda d: rub(d["loyalty"])),
        ("Все удержания WB, % выручки", lambda d: pct(d["commission"] + d["expenses"], d["revenue"])),
        ("Итого к получению", lambda d: rub(d["net"])),
        ("Итого к получению, % выручки", lambda d: pct(d["net"], d["revenue"])),
        ("Итого без штрафов, % выручки", lambda d: pct(d["net"] + d["penalty"], d["revenue"])),
        ("Итого на 1 проданную шт", lambda d: rub(d["net"] / max(d["sales_qty"] - d["ret_qty"], 1)) if d["sales_qty"] else "—"),
    ]
    print(f"| Показатель | FBO (FBW) | FBS | Не распределено |\n|---|---:|---:|---:|")
    for name, fn in lines:
        print(f"| {name} | {fn(o)} | {fn(s)} | {fn(u) if u['revenue'] or 'шт' not in name else '—'} |")

    n, m = sku_matched(rows)
    print(f"\n## Одни и те же артикулы в обоих форматах ({n} nmId)\n")
    print("| | FBO | FBS |\n|---|---:|---:|")
    print(f"| Продажи, шт | {m['FBO'][2]} | {m['FBS'][2]} |")
    print(f"| Средняя цена | {rub(m['FBO'][0] / max(m['FBO'][2], 1))} | {rub(m['FBS'][0] / max(m['FBS'][2], 1))} |")
    print(f"| Комиссия WB + эквайринг | {pct(m['FBO'][0] - m['FBO'][1], m['FBO'][0])} | {pct(m['FBS'][0] - m['FBS'][1], m['FBS'][0])} |")
    return a


def main():
    p = argparse.ArgumentParser()
    p.add_argument("date_from", nargs="?")
    p.add_argument("date_to", nargs="?")
    p.add_argument("--file")
    p.add_argument("--save")
    args = p.parse_args()
    if args.file:
        rows = []
        paths = [args.file] if os.path.isfile(args.file) else sorted(
            os.path.join(args.file, x) for x in os.listdir(args.file) if x.endswith(".json"))
        for path in paths:
            with open(path, encoding="utf-8") as fh:
                rows += json.load(fh)
    else:
        token = os.environ.get("WB_API_TOKEN")
        if not token or not (args.date_from and args.date_to):
            sys.exit("Нужны WB_API_TOKEN и даты: wb_fbs_fbo_compare.py YYYY-MM-DD YYYY-MM-DD")
        rows = fetch(args.date_from, args.date_to, token)
        if args.save:
            with open(args.save, "w", encoding="utf-8") as fh:
                json.dump(rows, fh, ensure_ascii=False)
    if not rows:
        sys.exit("За период нет строк отчёта")
    report(rows)


if __name__ == "__main__":
    main()
