"""Рич-контент 231Л3F, 800×500 (рисуем 1600×1000). Хелперы и стиль — из make_rich_wide.py."""
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
wide = open(os.path.join(here, "make_rich_wide_v3.py"), encoding="utf-8").read()
wide = wide[:wide.index("def block_cover")].replace("__file__", repr(os.path.join(here, "make_rich_wide_v3.py")))
exec(wide)

AGES_SCHOOL = {134: "8–9 л", 140: "9–10 л", 146: "10–11 л", 152: "11–12 л", 158: "12–13 л", 164: "13–14 л"}
PREFIX = "231Л3F"
LABEL_OVERRIDE.update({"01": "Основная информация", "02": "Воротник", "03": "Состав", "04": "С чем носить", "05": "Расцветки", "06": "Размер"})


def zoom(im, z, fx, fy):
    w, h = im.width / z, im.height / z
    x = min(max(im.width * fx - w / 2, 0), im.width - w)
    y = min(max(im.height * fy - h / 2, 0), im.height - h)
    return im.crop((round(x), round(y), round(x + w), round(y + h)))


def ph(p, w, h, z=1.0, fx=0.5, fy=0.5):
    im = photo(p)
    if z > 1:
        im = zoom(im, z, fx, fy)
        return cover(im, w, h, (0.5, 0.5))
    return cover(im, w, h, (fx, fy))


def checks(d, x, y, items, size=36, step=78, width=600):
    for t in items:
        d.ellipse([x, y, x + 52, y + 52], fill=ACCENT)
        d.line([(x + 13, y + 28), (x + 23, y + 38), (x + 40, y + 17)], fill=WHITE, width=6, joint="curve")
        d.text((x + 74, y + 26), t, font=fit(d, t, 600, size, width - 74), fill=INK, anchor="lm")
        y += step
    return y


def out(c, n, name):
    save(c, f"{PREFIX}_{n}_{name}.jpg")


# 1. Обложка
def b1():
    c, d = new()
    tf = font(600, 84)
    for i, t in enumerate(["ШКОЛЬНАЯ", "ВОДОЛАЗКА", "ЛАПША"]):
        d.text((M, 160 + i * 102), t, font=tf, fill=ACCENT if i == 2 else INK)
    d.text((M, 540), "база на весь учебный год", font=font(500, 40), fill=MUTED)
    pill(d, (M, 640), "134–164 см", font(800, 54), pad=(40, 22))
    d.text((M, BOT - 30), "T O T E M F O X", font=font(700, 26), fill=INK)
    shots = [("colors/белый_04", 0.3), ("colors/т.синий_05", 0.3), ("colors/розовый_05", 0.3)]
    x0, gap = 720, 24
    cw = (W - M - x0 - 2 * gap) // 3
    for i, (p, fy) in enumerate(shots):
        paste_round(c, ph(p, cw, H - 2 * M, fy=fy), (x0 + i * (cw + gap), M))
    out(c, 1, "обложка")


# 2. Ворот
def b2():
    c, d = new()
    header(d, "Невысокая стойка — не давит", "Для тех, кто не любит плотное высокое горло")
    brand(d)
    pw, gap = 360, 24
    paste_round(c, ph("ph_white/белый_15", pw, BOT - TOP, fy=0.35), (M, TOP))
    paste_round(c, ph("ph_white/розовый_14", pw, BOT - TOP, fy=0.35), (M + pw + gap, TOP))
    x = M + 2 * (pw + gap) + 16
    tw = W - M - x
    y = checks(d, x, TOP + 20, ["Невысокий воротник-стойка", "Аккуратно прикрывает шею",
                                "Без плотного высокого горла", "Мягкий эластичный рубчик"], size=36, step=86, width=tw)
    box = [x, y + 30, W - M, BOT]
    card(c, box, r=30)
    q = "Не любите высокое горло? Стойка закрывает шею, но не упирается в подбородок"
    for k, ln in enumerate(wrap(d, q, font(600, 34), tw - 72)):
        d.text((x + 36, box[1] + 40 + k * 46), ln, font=font(600, 34), fill=INK)
    out(c, 2, "невысокая_стойка")


# 3. Состав
def b3():
    c, d = new()
    header(d, "Мягкий рубчик лапша", "Из чего сшита и за что отвечает каждое волокно")
    brand(d)
    pw = 470
    paste_round(c, ph("ph_white/розовый_16", pw, BOT - TOP, fy=0.45), (W - M - pw, TOP))
    rows = [(25, "вискоза", "мягкость, приятная к телу"),
            (70, "полиэстер", "износостойкость, держит форму"),
            (5, "эластан", "тянется, не стесняет движений")]
    x, tw = M, W - 2 * M - pw - 48
    y = TOP + 10
    for pct_, name, desc in rows:
        card(c, [x, y, x + tw, y + 196], r=30)
        d.text((x + 36, y + 30), f"{pct_}%", font=font(800, 64), fill=ACCENT)
        d.text((x + 230, y + 38), name, font=font(800, 40), fill=INK)
        d.text((x + 230, y + 92), desc, font=fit(d, desc, 500, 32, tw - 260), fill=MUTED)
        by = y + 150
        d.rounded_rectangle([x + 36, by, x + tw - 36, by + 16], 8, fill=SOFT)
        d.rounded_rectangle([x + 36, by, x + 36 + max(16, (tw - 72) * pct_ / 100), by + 16], 8, fill=ACCENT)
        y += 196 + 28
    out(c, 3, "состав")


# 4. С чем носить
def b4():
    c, d = new()
    header(d, "Под форму и не только", "Базовая вещь для школы и на каждый день")
    brand(d)
    pw = 330
    paste_round(c, ph("ph_white/белый_09", pw, BOT - TOP, fy=0.45), (M, TOP))
    paste_round(c, ph("ph/т.синий_13", pw, BOT - TOP, fy=0.45), (W - M - pw, TOP))
    x0 = M + pw + 32
    x1 = W - M - pw - 32
    cw = (x1 - x0 - 24) // 2
    items = ["под сарафан", "под жилет", "под пиджак", "с брюками", "с юбкой", "с джинсами"]
    rh, rg = 104, 22
    for i, t in enumerate(items):
        x = x0 + (i % 2) * (cw + 24)
        y = TOP + (i // 2) * (rh + rg)
        card(c, [x, y, x + cw, y + rh], r=26)
        d.ellipse([x + 26, y + 30, x + 70, y + 74], fill=ACCENT)
        d.line([(x + 37, y + 53), (x + 45, y + 61), (x + 59, y + 44)], fill=WHITE, width=5, joint="curve")
        d.text((x + 92, y + rh / 2), t, font=fit(d, t, 700, 36, cw - 110), fill=INK, anchor="mm" if False else "lm")
    y = TOP + 3 * (rh + rg) + 20
    box = [x0, y, x1, BOT]
    d.rounded_rectangle(box, 30, fill=BLUE2)
    d.text((x0 + 36, y + 34), "Подходит для", font=font(600, 30), fill=WHITE)
    occ = ["школа", "театр", "выступление", "праздник", "каждый день"]
    f = font(700, 30)
    xx, yy = x0 + 36, y + 90
    for t in occ:
        w_ = d.textlength(t, font=f) + 44
        if xx + w_ > x1 - 30:
            xx, yy = x0 + 36, yy + 66
        pill(d, (xx, yy), t, f, fill=WHITE, color=INK, pad=(22, 10))
        xx += w_ + 14
    out(c, 4, "с_чем_носить")


# 5. Палитра
def b5():
    c, d = new()
    header(d, "10 цветов — на всю неделю", "Соберите несколько оттенков под разные дни")
    brand(d)
    groups = [("Для дресс-кода", [("colors/белый_04", 1.0, 0.2, "белый"), ("colors/т.синий_05", 1.0, 0.2, "тёмно-синий"),
                                  ("colors/т.серый_04", 2.6, 0.24, "тёмно-серый"), ("colors/св.бежевый_04", 1.0, 0.2, "светло-бежевый")]),
              ("Для праздников и прогулок", [("colors/бордовый_05", 1.0, 0.2, "бордовый"), ("colors/брусничный_04", 1.0, 0.2, "брусничный"),
                                             ("colors/розовый_05", 1.0, 0.2, "розовый"), ("colors/сиреневый_04", 1.0, 0.2, "сиреневый"),
                                             ("colors/зеленый_06", 1.0, 0.2, "зелёный"), ("colors/бежевый_04", 1.0, 0.2, "бежевый")])]
    gap = 16
    tw = (W - 2 * M - 5 * gap) // 6
    y = TOP - 24
    for gname, items in groups:
        pill(d, (M, y), gname, font(700, 28), fill=BLUE2, color=WHITE, pad=(22, 8))
        y += 62
        phh = 222
        for i, (p, z, fy, lab) in enumerate(items):
            x = M + i * (tw + gap)
            card(c, [x, y, x + tw, y + phh + 58], r=24)
            paste_round(c, ph(p, tw - 12, phh, z=z, fy=fy), (x + 6, y + 6), r=20, shadow=False)
            d.text((x + tw / 2, y + phh + 32), lab, font=fit(d, lab, 700, 28, tw - 16), fill=INK, anchor="mm")
        y += phh + 58 + 28
    out(c, 5, "10_цветов")


# 6. Размер
def b6():
    c, d = new()
    header(d, "Как выбрать размер", "Размер = рост ребёнка в сантиметрах")
    brand(d)
    sizes = [134, 140, 146, 152, 158, 164]
    table = [("Возраст*", [AGES_SCHOOL[s] for s in sizes]), ("Рост, см", [f"{s - 5}–{s}" for s in sizes])]
    tw_, lab_w = 1060, 290
    col_w = (tw_ - 50 - lab_w) / len(sizes)
    head_h, rh = 84, 76
    top = TOP - 20
    box_h = head_h + len(table) * rh + 20
    card(c, [M, top, M + tw_, top + box_h], r=30)
    d.rounded_rectangle([M, top, M + tw_, top + head_h], 30, fill=BLUE2)
    d.rectangle([M, top + head_h - 30, M + tw_, top + head_h], fill=BLUE2)
    d.text((M + 30, top + head_h / 2), "Размер", font=font(700, 36), fill=WHITE, anchor="lm")
    for j, s in enumerate(sizes):
        d.text((M + 25 + lab_w + col_w * (j + 0.5), top + head_h / 2), str(s), font=font(800, 42), fill=WHITE, anchor="mm")
    for i, (name, vals) in enumerate(table):
        y = top + head_h + 10 + i * rh
        if i % 2 == 1:
            d.rounded_rectangle([M + 12, y, M + tw_ - 12, y + rh], 18, fill=(246, 247, 252))
        d.text((M + 30, y + rh / 2), name, font=font(600, 32), fill=INK, anchor="lm")
        for j, v in enumerate(vals):
            d.text((M + 25 + lab_w + col_w * (j + 0.5), y + rh / 2), v, font=font(600, 26) if i == 0 else font(700, 25),
                   fill=MUTED if i == 0 else INK, anchor="mm")
    y = top + box_h + 28
    card(c, [M, y, M + tw_, y + 150], r=30)
    d.text((M + 36, y + 30), "На фото", font=font(700, 30), fill=ACCENT)
    d.text((M + 36, y + 80), "рост 145 см · размер 140 · ОГ 66 · ОТ 60 · ОБ 70", font=fit(d, "рост 145 см · размер 140 · ОГ 66 · ОТ 60 · ОБ 70", 600, 34, tw_ - 72), fill=INK)
    y += 150 + 24
    tip = [M, y, M + tw_, BOT - 40]
    d.rounded_rectangle(tip, 30, fill=ACCENT)
    d.text((tip[0] + 44, (tip[1] + tip[3]) / 2), "!", font=font(800, 56), fill=WHITE, anchor="mm")
    lines = wrap(d, "Модель облегающая: если ребёнок между размерами или плотного телосложения — берите больший",
                 font(700, 32), tw_ - 120)
    ty = (tip[1] + tip[3]) / 2 - len(lines) * 21
    for k, ln in enumerate(lines):
        d.text((tip[0] + 88, ty + k * 42), ln, font=font(700, 32), fill=WHITE)
    d.text((M, BOT - 30), "* возраст ориентировочный", font=font(500, 24), fill=MUTED)
    px = M + tw_ + 32
    paste_round(c, ph("ph/т.синий_04", W - M - px, BOT - top, fy=0.4), (px, top))
    out(c, 6, "размер")


for f in (b1, b2, b3, b4, b5, b6):
    f()
