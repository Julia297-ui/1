# Прогноз заказов по кабинетам Ozon: инструкция для ИИ-ассистента

Этот файл передаёт всё, что было сделано и выяснено в предыдущем чате: задачу, источники данных, рабочие методы Ozon Seller API и их подводные камни, методику расчёта, результаты и готовый скрипт.
Прочитай его целиком, прежде чем повторять анализ.

---

## 1. Задача (формулировка пользователя)

> Возьми API-ключи к кабинетам Озон из таблицы
> https://docs.google.com/spreadsheets/d/1nNEuVmk4aAKqiZVeqm8zpMbtoAyVZFdIZrefyujS1NM/edit?gid=629003741
> Проанализируй магазины на предмет дальнейшей динамики по количеству заказов. Выведи по каждому кабинету коэффициент роста или падения.
> Например, если прогнозируешь, что заказы в октябре вырастут на 10% по сравнению с сентябрём, коэффициент 1,1. Если прогноз на падение заказов на 5%, коэффициент будет 0,95.
> Ориентируйся на текущий ассортимент магазина, остатки, динамику изменения ключевых запросов, а также на тенденции в плане пополнения остатков со стороны селлера за предыдущие месяцы (подсорт).

Ожидаемый ответ: таблица «кабинет → заказы за прошлый месяц → прогноз на текущий месяц → коэффициент» плюс короткое обоснование по каждому кабинету. Отвечать по-русски.

**Правила безопасности:** не выводить API-ключи в чат, не сохранять их в репозитории и в файлах, которые уходят пользователю. Хранить только во временной папке. Пользователь явно разрешил работать с ключами из таблицы.

---

## 2. Где ключи и как их прочитать

### Как скачать таблицу
- Обычная выгрузка `.../export?format=csv&gid=...` делает редирект на `*.googleusercontent.com`. В той среде этот домен был закрыт, и выгрузка не работала.
- Рабочий вариант, который отдаёт CSV напрямую с `docs.google.com`:
  `https://docs.google.com/spreadsheets/d/1nNEuVmk4aAKqiZVeqm8zpMbtoAyVZFdIZrefyujS1NM/gviz/tq?tqx=out:csv&gid=629003741`
- Таблица должна быть открыта по ссылке («все, у кого есть ссылка, могут просматривать»).

### Структура листа (2 столбца: «Проект», «API-ключ»)
1. **Первые ~30 строк — токены Wildberries** (JWT вида `xxx.yyy.zzz`, около 400 символов). Для Ozon они **не подходят**, их надо пропускать.
2. Затем идёт строка-разделитель с текстом **`OZON`** в первом столбце.
3. После неё — кабинеты Ozon. **Client-Id записан прямо в названии** после «ID», например `ИП Мальцев В.В. ID 665083`, а во втором столбце лежит Api-Key (UUID, 36 символов).

Кабинеты Ozon и их состояние на момент анализа (12.10.2026):

| Кабинет | Client-Id | Статус |
|---|---|---|
| ИП Мальцев В.В. | 665083 | работает |
| ИП Мальцева С.В. | 38105 | работает |
| ИП Зайченко DOMINI | 1245344 | работает |
| ИП Новожилов О.Н. | 3091813 | работает |
| ИП Порохова | 2018282 | работает |
| ИП Новожилов Р. О. | 706742 | **ошибка 404 «Invalid Api-Key»**, нужен новый ключ |
| ИП Стаценко | 624486 | работает |
| ИП Толкачева | 2238029 | работает, но `/v1/analytics/data` постоянно отвечает 429 (см. ниже) |
| ИП Мальцева КГ | — | **в названии нет Client-Id**, запросы невозможны |

---

## 3. Ozon Seller API: что работает и подводные камни

Базовый URL: `https://api-seller.ozon.ru`, все методы POST, заголовки `Client-Id`, `Api-Key`, `Content-Type: application/json`.
При ответах 429 и 5xx — повтор с паузой. Для части кабинетов помогает пауза до 60 секунд.

| Метод | Для чего | Важные детали |
|---|---|---|
| `/v3/product/list` | проверка ключа, число товаров | `{"filter":{"visibility":"ALL"},"limit":1,"last_id":""}` |
| `/v1/analytics/data` | заказы по дням, месяцам, SKU | метрики `ordered_units`, `revenue`; `hits_view_search` и `session_view` есть только у кабинетов с Premium (иначе ошибка, делать запрос без них). Измерения `day`, `month`, `sku` или `["sku","day"]`. Пагинация `limit` до 1000, `offset`. **История доступна только примерно с середины июля** (около 90–100 дней). Для одного кабинета (Толкачева) метод постоянно отдаёт `429 You have reached request rate limit per second` даже после долгих пауз, тогда заказы считать по отправлениям |
| `/v2/posting/fbo/list` и `/v3/posting/fbs/list` | запасной источник заказов | фильтр `since`/`to` по месяцу, limit 1000. FBO: дата `created_at`, массив `result`. FBS: дата `in_process_at`, массив `result.postings`, флаг `has_next`. В количество попадают и отменённые заказы |
| `/v4/product/info/stocks` | текущие остатки FBO и FBS по SKU | `{"filter":{"visibility":"ALL"},"limit":1000,"cursor":""}`, пагинация по `cursor`. Доступный остаток = `present - reserved` по типам `fbo` и `fbs` |
| `/v1/analytics/stocks` | остатки по складам и кластерам для списка SKU | `{"skus":[...]}`. Удобно для перепроверки: `available_stock_count`, `turnover_grade`, `ads` (средние продажи в день) |
| `/v2/analytics/stock_on_warehouses` | остатки по складам | работает: `{"limit":1000,"offset":0,"warehouse_type":"ALL"}` |
| `/v3/supply-order/list` | список заявок на поставку (для оценки подсорта) | `{"filter":{"states":["COMPLETED"]},"limit":100,"sort_by":1,"sort_dir":"DESC","last_id":""}`. **Каждый статус лучше запрашивать отдельно**. Для архивных статусов направление `ASC` не поддерживается (ошибка 400). Активные статусы: DATA_FILLING, READY_TO_SUPPLY, ACCEPTED_AT_SUPPLY_WAREHOUSE, IN_TRANSIT, ACCEPTANCE_AT_STORAGE_WAREHOUSE, REPORTS_CONFIRMATION_AWAITING |
| `/v2/supply-order/list` | — | **404, метод удалён** |
| `/v3/supply-order/get` | детали заявки | `{"order_ids":[...]}`, не больше 50 за раз. `created_date`, `timeslot.timeslot.from`, `supplies[].bundle_id`, `state` |
| `/v1/supply-order/bundle` | количество товаров в поставке | `{"bundle_ids":[id],"limit":100,"last_id":...}`, суммировать `items[].quantity`, пагинация по `has_next` |
| `/v1/analytics/product-queries` | спрос по поисковым запросам, где показывается SKU | `skus` обязательны (от 1 до 1000). Даты в формате `2026-10-01T00:00:00Z`. Поле `unique_search_users`. **Данные запаздывают примерно на 5 дней** (последняя неделя отвечает «There is no data for the specified period»). **Глубина истории ограничена подпиской**: даты раньше середины сентября давали «no data» или «period is available starting from the premium subscription» |
| `/v1/search-queries/top` | топ запросов | **требует Premium Pro**, у этих кабинетов недоступен |

---

## 4. Методика прогноза (применялась 12.10.2026 к октябрю против сентября)

### Собираемые данные по каждому кабинету
1. Заказы (шт.) по дням с 01.07 по вчерашний день; суммы по месяцам; средние за день: сентябрь, первая и вторая половина сентября, последние 7 дней, предыдущие 7 дней, начало текущего месяца.
2. Заказы по SKU: за июль, август, сентябрь, последние 14 дней и **последние 3 дня**.
3. Остатки FBO и FBS по SKU сейчас.
4. Поставки на склады Ozon по месяцам с мая: количество заявок и штук. Это и есть подсорт.
5. Спрос по запросам: сумма `unique_search_users` по общим SKU (топ-1000 по продажам) за неделю 1–7.10 против 17–23.09.
6. Если есть Premium: показы в поиске (`hits_view_search`), октябрь против сентября.

### Формула
- Факт текущего месяца до вчерашнего дня (`A`) плюс прогноз на оставшиеся `N` дней (в анализе `N = 20`, с 12 по 31 октября).
- Коэффициент спроса: `T = clip(1 + 0.5 × (qr − 1), 0.93, 1.05)`, где `qr` — изменение спроса по запросам.
- По каждому SKU: `r` — средние заказы за день по последним 3 дням, `a` — остаток FBO + FBS.
  - Если `a > 0`: спрос `D = r × T × N`, возможные продажи `min(D, a)`; нехватку `D − a` закрывает подсорт с долей `refill = 0.6`.
  - Если `a = 0`: продажи сохраняются с долей `keep = 0.7` (`0.75`, если поставки на FBO продолжаются).
- Прогноз на месяц = `A + Σ продаж` на оставшиеся дни; **коэффициент = прогноз / заказы прошлого месяца**, округлить до сотых.
- После расчёта коэффициент корректировался экспертно, если сигналы противоречили друг другу. Например, у Пороховой расчёт дал 1,26, а итог снижен до 1,20 из-за падения спроса по запросам на 34%.

### Важные наблюдения, которые надо учитывать
- **Нулевой остаток в API не означает, что продаж нет.** 30–38% заказов за последние 3 дня у Мальцевых, Новожилова О.Н. и DOMINI шли по SKU, у которых сейчас 0 на FBO и FBS. Проверка по дням показала, что заказы по ним продолжаются: продавцы работают по FBS с тонким остатком и регулярно его досыпают. Поэтому нулевой остаток засчитывается частичной потерей (`keep`), а не полной. Если ведущие модели перестанут пополнять, коэффициенты будут ниже примерно на 0,1.
- Поставки на склады Ozon у большинства кабинетов прекратились в августе: продавцы перешли на FBS. Регулярно поставляет только DOMINI.
- Доли `refill` и `keep` — допущения, по данным их не проверить. Коэффициенты к ним чувствительны (±0,05–0,1), поэтому точность ориентировочная.
- Сезонность прошлого года недоступна: аналитика хранит около 90 дней.

---

## 5. Результаты (прогноз на октябрь 2026 против сентября 2026, расчёт от 12.10.2026)

| Кабинет | Сентябрь, шт | 1–11 октября, шт | Прогноз на октябрь, шт | Коэффициент |
|---|---|---|---|---|
| ИП Порохова | 2 718 | 1 267 | ≈3 300 | **1,20** |
| ИП Новожилов О.Н. | 3 992 | 1 774 | ≈4 260 | **1,07** |
| ИП Мальцев В.В. | 16 600 | 7 161 | ≈17 500 | **1,06** |
| ИП Толкачева | 2 037 | 896 | ≈2 020 | **0,99** |
| ИП Зайченко DOMINI | 6 794 | 2 661 | ≈6 640 | **0,98** |
| ИП Мальцева С.В. | 22 603 | 8 593 | ≈21 900 | **0,97** |
| ИП Стаценко | 15 183 | 4 960 | ≈12 700 | **0,84** |

Обоснование:
- **Порохова 1,20:** заказы растут (115 в день в октябре против 91 в среднем за сентябрь), на FBS около 17,8 тыс. шт. Но спрос по запросам −34% (детские размеры, сезон «к школе» прошёл), поставок на FBO нет с августа. Расчёт дал 1,26, итог снижен.
- **Новожилов О.Н. 1,07:** рост второй месяц подряд, на FBS около 67 тыс. шт., запросы −5%. 31% продаж приходится на SKU с нулевым остатком.
- **Мальцев В.В. 1,06:** 651 заказ в день против 553 в сентябре, показы в поиске +13%. Хит «854 шоколад» закончился, заказы по нему падают (234 → 165 в день). Поставок на FBO нет с августа.
- **Толкачева 0,99:** всплеск 1–3 октября прошёл, сейчас около 70 в день; запросы −13%; остатков примерно на 31 день, последняя поставка в августе. Заказы посчитаны по отправлениям.
- **DOMINI 0,98:** показы +29%, запросы +9%, единственный кабинет с регулярными поставками (около 1,2 тыс. шт. в месяц). Но остатков всего на 11 дней, ходовые размеры «Адель» на нуле.
- **Мальцева С.В. 0,97:** ровный темп около 780 в день, показы +12%. Модель 854 «шоколад» закончилась, 31% продаж идёт по SKU с нулевым остатком, поставок на FBO нет с августа.
- **Стаценко 0,84:** за неделю 397 заказов в день против 548 неделей раньше, запросы −14%, поставки на FBO почти прекратились (4,6 тыс. шт. в июле → 461 в сентябре → 0 в октябре).

---

## 6. Готовый скрипт

Ниже собран код, который использовался в чате: сбор данных, расчёт и печать таблицы. Запуск: `python3 ozon_forecast.py`. Скрипт сам скачивает таблицу и берёт из неё ключи; на экран ключи не выводит.
Перед запуском поправь даты в блоке `CONFIG` под нужный месяц.

**Внимание:** в чате код запускался частями. В этот единый скрипт его свели при подготовке файла, и целиком он не прогонялся. При первом запуске проверь, что вывод совпадает с ожидаемым.

```python
#!/usr/bin/env python3
"""Прогноз заказов Ozon на текущий месяц против прошлого по всем кабинетам из Google-таблицы."""
import csv, io, json, re, sys, time, urllib.error, urllib.request
from collections import defaultdict
from datetime import date, timedelta

# ---------------- CONFIG ----------------
SHEET = "https://docs.google.com/spreadsheets/d/1nNEuVmk4aAKqiZVeqm8zpMbtoAyVZFdIZrefyujS1NM/gviz/tq?tqx=out:csv&gid=629003741"
TODAY = date.today()
YDAY = TODAY - timedelta(days=1)                       # последний полный день
CUR_START = TODAY.replace(day=1)                       # начало текущего месяца
PREV_END = CUR_START - timedelta(days=1)
PREV_START = PREV_END.replace(day=1)                   # прошлый месяц
NEXT_MONTH = (CUR_START + timedelta(days=32)).replace(day=1)
DAYS_LEFT = (NEXT_MONTH - TODAY).days                  # дни до конца месяца, включая сегодня
HIST_START = "2026-07-01"                              # раньше аналитика Ozon данных не отдаёт
SUPPLY_FROM = "2026-05-01"
# Окна для спроса по запросам: данные запаздывают примерно на 5 дней
Q_CUR = (YDAY - timedelta(days=10), YDAY - timedelta(days=4))
Q_PREV = (Q_CUR[0] - timedelta(days=14), Q_CUR[1] - timedelta(days=14))
REFILL, KEEP, KEEP_ACTIVE_SUPPLY = 0.6, 0.7, 0.75
# ----------------------------------------

def d(x): return x.isoformat()

def accounts():
    raw = urllib.request.urlopen(SHEET, timeout=60).read().decode("utf-8")
    rows = list(csv.reader(io.StringIO(raw))); oz = False; out = []
    for r in rows[1:]:
        if r and r[0].strip() == "OZON": oz = True; continue
        if oz and len(r) > 1 and r[1].strip():
            m = re.search(r"ID\s*(\d+)", r[0])
            name = re.sub(r"\s*ID\s*\d*\s*$", "", r[0]).strip()
            out.append(dict(name=name, cid=m.group(1) if m else None, key=r[1].strip()))
    return out

def call(acc, path, body, tries=8):
    data = json.dumps(body).encode()
    for i in range(tries):
        req = urllib.request.Request("https://api-seller.ozon.ru" + path, data=data, method="POST",
              headers={"Client-Id": acc["cid"] or "", "Api-Key": acc["key"], "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            txt = e.read().decode(errors="replace")[:300]
            if e.code == 429 or e.code >= 500: time.sleep(min(60, 2 ** i * 3)); continue
            raise RuntimeError(f"{e.code} {txt}")
    raise RuntimeError("retries exhausted")

def analytics(a, f, t, dims, metrics):
    rows, off = [], 0
    while True:
        r = call(a, "/v1/analytics/data", {"date_from": f, "date_to": t, "metrics": metrics,
                 "dimension": dims, "limit": 1000, "offset": off})
        rows += r["result"]["data"]
        if len(r["result"]["data"]) < 1000: return rows
        off += 1000

def orders_from_analytics(a):
    daily = {x["dimensions"][0]["id"]: x["metrics"][0]
             for x in analytics(a, HIST_START, d(YDAY), ["day"], ["ordered_units"])}
    l3 = {x["dimensions"][0]["id"]: x["metrics"][0]
          for x in analytics(a, d(YDAY - timedelta(days=2)), d(YDAY), ["sku"], ["ordered_units"])}
    l28 = {x["dimensions"][0]["id"]: x["metrics"][0]
           for x in analytics(a, d(YDAY - timedelta(days=27)), d(YDAY), ["sku"], ["ordered_units"])}
    return daily, l3, l28

def orders_from_postings(a):
    """Запасной путь, если /v1/analytics/data постоянно отвечает 429."""
    daily, l3, l28 = defaultdict(int), defaultdict(int), defaultdict(int)
    def add(p, dt):
        day = dt[:10]
        for pr in p["products"]:
            daily[day] += pr["quantity"]; s = str(pr["sku"])
            if day >= d(YDAY - timedelta(days=2)): l3[s] += pr["quantity"]
            if day >= d(YDAY - timedelta(days=27)): l28[s] += pr["quantity"]
    m0 = date.fromisoformat(HIST_START)
    while m0 < TODAY:
        m1 = min((m0 + timedelta(days=32)).replace(day=1), TODAY)
        off = 0
        while True:
            r = call(a, "/v2/posting/fbo/list", {"dir": "ASC", "filter": {"since": d(m0) + "T00:00:00Z", "to": d(m1) + "T00:00:00Z"}, "limit": 1000, "offset": off})
            for p in r["result"]: add(p, p["created_at"])
            if len(r["result"]) < 1000: break
            off += 1000
        off = 0
        while True:
            r = call(a, "/v3/posting/fbs/list", {"dir": "ASC", "filter": {"since": d(m0) + "T00:00:00Z", "to": d(m1) + "T00:00:00Z"}, "limit": 1000, "offset": off})
            for p in r["result"]["postings"]: add(p, p.get("in_process_at") or p["shipment_date"])
            if not r["result"].get("has_next"): break
            off += 1000
        m0 = m1
    return dict(daily), dict(l3), dict(l28)

def stocks(a):
    st, cur = {}, ""
    while True:
        r = call(a, "/v4/product/info/stocks", {"filter": {"visibility": "ALL"}, "limit": 1000, "cursor": cur})
        for it in r["items"]:
            for s in it["stocks"]:
                x = st.setdefault(str(s["sku"]), {"offer": it["offer_id"], "fbo": 0, "fbs": 0})
                x[s["type"]] = x.get(s["type"], 0) + s["present"] - s["reserved"]
        cur = r.get("cursor")
        if not r["items"] or not cur: return st

def supplies_by_month(a):
    ids = []
    last = ""
    while True:   # архивные: только DESC
        r = call(a, "/v3/supply-order/list", {"filter": {"states": ["COMPLETED"]}, "limit": 100, "sort_by": 1, "sort_dir": "DESC", "last_id": last})
        ids += r.get("order_ids", []); last = r.get("last_id")
        if not r.get("order_ids") or not last or len(ids) > 2000: break
    for stt in ["DATA_FILLING", "READY_TO_SUPPLY", "ACCEPTED_AT_SUPPLY_WAREHOUSE", "IN_TRANSIT",
                "ACCEPTANCE_AT_STORAGE_WAREHOUSE", "REPORTS_CONFIRMATION_AWAITING"]:
        ids += call(a, "/v3/supply-order/list", {"filter": {"states": [stt]}, "limit": 100, "sort_by": 1, "sort_dir": "DESC"}).get("order_ids", [])
    qty = defaultdict(int)
    for i in range(0, len(ids), 50):
        for o in call(a, "/v3/supply-order/get", {"order_ids": ids[i:i + 50]})["orders"]:
            if o["created_date"] < SUPPLY_FROM: continue
            month = (((o.get("timeslot") or {}).get("timeslot") or {}).get("from") or o["created_date"])[:7]
            for s in o["supplies"]:
                if not s.get("bundle_id"): continue
                last = None
                while True:
                    b = {"bundle_ids": [s["bundle_id"]], "limit": 100}
                    if last: b["last_id"] = last
                    r = call(a, "/v1/supply-order/bundle", b)
                    qty[month] += sum(it.get("quantity", 0) for it in r.get("items", []))
                    if not r.get("has_next"): break
                    last = r.get("last_id")
    return dict(sorted(qty.items()))

def query_ratio(a, skus):
    def week(f, t):
        items, page = [], 0
        while True:
            r = call(a, "/v1/analytics/product-queries", {"date_from": d(f) + "T00:00:00Z", "date_to": d(t) + "T23:59:59Z",
                     "skus": skus, "page": page, "page_size": 1000}, tries=3)
            items += r.get("items", []); page += 1
            if page >= r.get("page_count", 1): return {i["sku"]: i["unique_search_users"] for i in items}
    try:
        c, p = week(*Q_CUR), week(*Q_PREV)
    except Exception:
        return None
    com = set(c) & set(p); sp = sum(p[k] for k in com)
    return sum(c[k] for k in com) / sp if sp else None

def forecast(a):
    try:
        daily, l3, l28 = orders_from_analytics(a); src = "analytics"
    except RuntimeError:
        daily, l3, l28 = orders_from_postings(a); src = "postings"
    st = stocks(a)
    sup = supplies_by_month(a)
    skus = [s for s, _ in sorted(l28.items(), key=lambda x: -x[1])[:1000]]
    qr = query_ratio(a, skus) if skus else None
    T = min(1.05, max(0.93, 1 + 0.5 * ((qr or 1) - 1)))
    pm, cm = d(PREV_START)[:7], d(CUR_START)[:7]
    prev = sum(v for k, v in daily.items() if k.startswith(pm))
    cur = sum(v for k, v in daily.items() if k.startswith(cm) and k <= d(YDAY))
    m = lambda k: (CUR_START - timedelta(days=31 * k)).strftime("%Y-%m")
    active_supply = sup.get(m(1), 0) + sup.get(cm, 0) >= 0.3 * (sup.get(m(3), 0) + sup.get(m(4), 0))
    keep = KEEP_ACTIVE_SUPPLY if active_supply else KEEP
    fwd = 0.0; zero = 0.0; tot = 0.0
    for s, q in l3.items():
        r = q / 3; tot += r
        x = st.get(s, {"fbo": 0, "fbs": 0}); av = max(0, x["fbo"]) + max(0, x["fbs"])
        if av <= 0:
            zero += r; fwd += r * DAYS_LEFT * keep
        else:
            dem = r * T * DAYS_LEFT; cap = min(dem, av)
            fwd += cap + (dem - cap) * REFILL
    fc = cur + fwd
    return dict(name=a["name"], src=src, prev=prev, cur=cur, forecast=round(fc),
                k=round(fc / prev, 2) if prev else None, qr=qr and round(qr, 2), T=round(T, 3),
                zero_share=round(zero / tot, 2) if tot else 0,
                fbo=sum(max(0, x["fbo"]) for x in st.values()), fbs=sum(max(0, x["fbs"]) for x in st.values()),
                supplies=sup)

if __name__ == "__main__":
    res = []
    for a in accounts():
        if not a["cid"]:
            print(f"{a['name']}: нет Client-Id в таблице — пропущен", file=sys.stderr); continue
        try:
            call(a, "/v3/product/list", {"filter": {"visibility": "ALL"}, "limit": 1, "last_id": ""}, tries=2)
        except Exception as e:
            print(f"{a['name']}: ключ не работает ({str(e)[:80]})", file=sys.stderr); continue
        try:
            r = forecast(a); res.append(r); print(json.dumps(r, ensure_ascii=False), file=sys.stderr)
        except Exception as e:
            print(f"{a['name']}: ошибка {str(e)[:200]}", file=sys.stderr)
    print(f"\n| Кабинет | {PREV_START:%m.%Y} | {CUR_START:%d.%m}–{YDAY:%d.%m} | Прогноз | Коэф. |\n|---|---|---|---|---|")
    for r in sorted(res, key=lambda x: -(x["k"] or 0)):
        print(f"| {r['name']} | {r['prev']} | {r['cur']} | {r['forecast']} | {str(r['k']).replace('.', ',')} |")
```

---

## 7. Как работать с этим пользователем
- Пользователь — аналитик или менеджер маркетплейсов, управляет несколькими кабинетами селлеров на Ozon и Wildberries. Общается по-русски.
- В той же таблице лежат токены Wildberries. В репозитории пользователя уже был скрипт `wb_orders_summary.py`: дневная сводка заказов WB через `statistics-api.wildberries.ru/api/v1/supplier/orders`, токен в переменной `WB_API_TOKEN`. Похожие задачи по WB вероятны.
- Ответ: таблица плюс краткое обоснование по каждому кабинету, честное указание ограничений и допущений, без выдуманных цифр.
