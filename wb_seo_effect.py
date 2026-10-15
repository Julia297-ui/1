#!/usr/bin/env python3
"""Оценка эффекта SEO-изменений карточек Wildberries: неделя до и неделя после.

Токен берётся из переменной окружения WB_API_TOKEN (категории «Аналитика»).
Группы карточек и даты изменений — в seo/effect_groups.json.

Снять исходные данные:   python3 wb_seo_effect.py snapshot 2026-10-08 2026-10-14 seo/baseline.json
Сравнить с исходными:     python3 wb_seo_effect.py compare 2026-10-15 2026-10-21 seo/baseline.json
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://seller-analytics-api.wildberries.ru"
GROUPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seo", "effect_groups.json")


def post(path, body, token):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode(),
                                 headers={"Authorization": token, "Content-Type": "application/json"})
    for _ in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(65)
    raise RuntimeError("WB API: слишком много запросов")


def funnel(ids, start, end, token):
    out = {}
    for i in range(0, len(ids), 20):
        d = post("/api/analytics/v3/sales-funnel/products",
                 {"selectedPeriod": {"start": start, "end": end}, "nmIds": ids[i:i + 20], "limit": 20, "offset": 0}, token)
        for p in d["data"]["products"]:
            st = p["statistic"]["selected"]
            out[str(p["product"]["nmId"])] = {"open": st["openCount"], "cart": st["cartCount"],
                                              "orders": st["orderCount"], "sum": st["orderSum"]}
        time.sleep(21)
    return out


def queries(ids, start, end, token):
    out = {}
    for i in range(0, len(ids), 50):
        d = post("/api/v2/search-report/product/search-texts",
                 {"currentPeriod": {"start": start, "end": end}, "nmIds": ids[i:i + 50], "topOrderBy": "openCard",
                  "includeSubstitutedSKUs": True, "includeSearchTexts": True,
                  "orderBy": {"field": "openCard", "mode": "desc"}, "limit": 100}, token)
        for it in d["data"]["items"]:
            q = out.setdefault(it["text"], {"freq": 0, "open": 0, "orders": 0, "pos": None})
            q["freq"] = max(q["freq"], it["frequency"]["current"])
            q["open"] += it["openCard"]["current"]
            q["orders"] += it["orders"]["current"]
            p = it["medianPosition"]["current"]
            if p and (q["pos"] is None or p < q["pos"]):
                q["pos"] = p
        time.sleep(21)
    return out


def collect(start, end, token):
    groups = json.load(open(GROUPS))
    res = {"period": [start, end], "groups": {}}
    for name, g in groups.items():
        ids = g["nmIds"]
        res["groups"][name] = {"funnel": funnel(ids, start, end, token), "queries": queries(ids, start, end, token)}
    return res


def pct(new, old):
    return f"{(new - old) / old * 100:+.0f}%" if old else ("—" if not new else "new")


def compare(before, after):
    groups = json.load(open(GROUPS))
    print(f"# Эффект изменений: {before['period'][0]}…{before['period'][1]} → {after['period'][0]}…{after['period'][1]}\n")
    for name, g in groups.items():
        b, a = before["groups"][name], after["groups"][name]
        tot = lambda f, k: sum(v[k] for v in f.values())
        print(f"## {name} (изменено {g['changed']})\n")
        print("| Показатель | До | После | Изменение |\n|---|---|---|---|")
        for k, title in (("open", "Переходы в карточку"), ("cart", "Корзины"), ("orders", "Заказы"), ("sum", "Сумма заказов, ₽")):
            x, y = tot(b["funnel"], k), tot(a["funnel"], k)
            print(f"| {title} | {x} | {y} | {pct(y, x)} |")
        ob, oa = tot(b["funnel"], "open"), tot(a["funnel"], "open")
        cb = tot(b["funnel"], "cart") / ob * 100 if ob else 0
        ca = tot(a["funnel"], "cart") / oa * 100 if oa else 0
        print(f"| Конверсия в корзину | {cb:.1f}% | {ca:.1f}% | {ca - cb:+.1f} п.п. |\n")
        top = sorted(set(b["queries"]) | set(a["queries"]),
                     key=lambda t: -max(b["queries"].get(t, {}).get("freq", 0), a["queries"].get(t, {}).get("freq", 0)))[:15]
        print("| Запрос | Частота | Позиция до | Позиция после | Переходы до → после |\n|---|---|---|---|---|")
        for t in top:
            qb, qa = b["queries"].get(t, {}), a["queries"].get(t, {})
            print(f"| {t} | {max(qb.get('freq', 0), qa.get('freq', 0))} | {qb.get('pos') or '—'} | {qa.get('pos') or '—'} "
                  f"| {qb.get('open', 0)} → {qa.get('open', 0)} |")
        print()


def main():
    token = os.environ.get("WB_API_TOKEN")
    if not token or len(sys.argv) != 5 or sys.argv[1] not in ("snapshot", "compare"):
        sys.exit(__doc__)
    mode, start, end, path = sys.argv[1:]
    data = collect(start, end, token)
    if mode == "snapshot":
        json.dump(data, open(path, "w"), ensure_ascii=False, indent=1)
        print(f"Сохранено: {path}")
    else:
        compare(json.load(open(path)), data)


if __name__ == "__main__":
    main()
