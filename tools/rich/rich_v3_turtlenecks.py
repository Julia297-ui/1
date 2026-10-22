"""Общий рич «Водолазки» в стандарте v3 (8 моделей, 56 карточек). Хелперы — из rich_template_v3_nightgowns.py.
Запуск: python3 rich_v3_turtlenecks.py <папка_фото> <папка_вывода> <Montserrat-VF.ttf> <любой_шрифт>"""
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(here, "rich_template_v3_nightgowns.py"), encoding="utf-8").read()
exec(t[:t.index("# 01 Основная информация")])
C = {"сиреневый": 175321556, "белый": 168072545, "голубоймеланж": 180096198, "звёзды_малыш": 175334024,
     "горох_малыш": 175334027, "кн2_голубой": 180107365, "р1_голубой": 168088463, "звёзды": 175321555}


def save(c, n, name):
    c.resize((800, 500), Image.LANCZOS).save(os.path.join(OUT, f"водолазки_{n}_{name}.jpg"), quality=93, subsampling=0)
    print("saved", n, name)


def title2(d, x, y, a, b, size, maxw):
    s = size
    while max(d.textlength(a, font=head(s)), d.textlength(b, font=head(s))) > maxw: s -= 2
    d.text((x, y), a, font=head(s), fill=INK)
    d.text((x, y + s * 1.15), b, font=head(s), fill=PINK)
    return y + s * 2.3


def s1():
    c, d = new("Основная информация", "01")
    d.text((M, 150), "T O T E M F O X", font=body(600, 26), fill=GREY)
    s = 80
    while d.textlength("ВОДОЛАЗКА", font=head(s)) > 620: s -= 2
    for i, (tx, col) in enumerate([("НЕВЕРОЯТНО", INK), ("МЯГКАЯ", INK), ("ВОДОЛАЗКА", PINK)]):
        d.text((M, 205 + i * s * 1.15), tx, font=head(s), fill=col)
    y = 205 + 3 * s * 1.15
    y = para(d, (M, y + 30), "Тепло, комфорт и стиль — с нежным воротником-стойкой", body(500, 34), 600) + 40
    heart(d, M + 26, y + 26, 52, PINK)
    d.text((M + 76, y), "Любовь с первого", font=body(500, 34), fill=INK)
    d.text((M + 76, y + 42), "прикосновения", font=body(500, 34), fill=INK)
    shots = [("сиреневый", 6, 0.3), ("белый", 12, 0.3), ("звёзды", 7, 0.3)]
    x0, gap = 720, 18
    cw = (W - M - x0 - 2 * gap) // 3
    for i, (k, n, fy) in enumerate(shots):
        paste(c, crop(P(k, n), cw, H - 110 - M, fy=fy, z=1.1), (x0 + i * (cw + gap), 110))
    save(c, 1, "основная_информация")


def s2():
    c, d = new("Преимущества", "02")
    gap = 22; top = 96
    cw = (W - 2 * M - 2 * gap) // 3; ch = (H - top - M - gap) // 2
    tiles = [("t", BLUE, "Мягкая внутри", "приятна к коже весь день"),
             ("p", ("белый", 7, 0.5, 0.45)),
             ("t", PINK, "Элегантная снаружи", "аккуратный вид в саду и школе"),
             ("p", ("сиреневый", 10, 0.5, 0.5)),
             ("t", PINK, "Тепло и комфорт", "согревает в прохладные дни"),
             ("p", ("кн2_голубой", 12, 0.5, 0.45))]
    for i, tl in enumerate(tiles):
        x = M + (i % 3) * (cw + gap); y = top + (i // 3) * (ch + gap)
        if tl[0] == "t":
            d.rounded_rectangle([x, y, x + cw, y + ch], 26, fill=tl[1])
            para(d, (x + 34, y + 36), tl[2], body(700, 40), cw - 68, WHITE, 1.15)
            para(d, (x + 34, y + ch - 130), tl[3], body(500, 30), cw - 68, WHITE, 1.25)
        else:
            k, n, fx, fy = tl[1]
            paste(c, crop(P(k, n), cw, ch, fx, fy), (x, y), 26)
    save(c, 2, "преимущества")


def s3():
    c, d = new("Ткань", "03")
    pw = 660
    paste(c, crop(P("белый", 10), pw, H - 96 - M, fy=0.5), (W - M - pw, 96), 26)
    badges = [(BLUE, "хлопок с эластаном"), (PINK, "дышащий трикотаж"), (BLUE, "износостойкий")]
    y = 200
    for i, (col, tx) in enumerate(badges):
        f = body(500, 46); bw = d.textlength(tx, font=f) + 150; x = M + (i % 2) * 60
        d.rounded_rectangle([x, y, x + bw, y + 116], 18, fill=col)
        sparkle(d, x + 56, y + 46, 26); sparkle(d, x + 34, y + 80, 12)
        d.text((x + 100, y + 58), tx, font=f, fill=WHITE, anchor="lm"); y += 160
    para(d, (M, y + 30), "Очень эластичный и приятный к телу трикотаж — практичный на каждый день", body(500, 32), W - M - pw - M - 60, GREY)
    save(c, 3, "ткань")


def s4():
    c, d = new("Посадка", "04")
    title2(d, M, 90, "КОМФОРТНАЯ", "ПОСАДКА", 60, 900)
    items = [("белый", 7, "Нежный воротник", "мягкая стойка не давит"), ("сиреневый", 10, "Удлинённые манжеты", "не задираются в движении"),
             ("кн2_голубой", 7, "Эластичный крой", "не стесняет, легко надевать"), ("звёзды", 9, "Удобный крой", "не натирает весь день")]
    gap = 22; top = 300; cw = (W - 2 * M - 3 * gap) // 4; ph = 440
    for i, (k, n, t1, t2) in enumerate(items):
        x = M + i * (cw + gap)
        d.rounded_rectangle([x, top, x + cw, H - M], 26, fill=WHITE)
        paste(c, crop(P(k, n), cw - 20, ph, fy=0.45), (x + 10, top + 10), 20)
        s = 30
        while d.textlength(t1, font=body(700, s)) > cw - 40: s -= 1
        d.text((x + 24, top + ph + 34), t1, font=body(700, s), fill=INK)
        para(d, (x + 24, top + ph + 80), t2, body(500, 26), cw - 48, GREY)
    save(c, 4, "посадка")


def s5():
    c, d = new("Как носить", "05")
    pw = 420
    paste(c, crop(P("сиреневый", 11), pw, H - 96 - M, fy=0.4), (M, 96), 26)
    paste(c, crop(P("звёзды", 6), pw, H - 96 - M, fy=0.4), (W - M - pw, 96), 26)
    x0 = M + pw + 50; w = W - 2 * M - 2 * pw - 100
    y = title2(d, x0, 150, "ДЛЯ СТИЛЬНОГО", "ОБРАЗА", 52, w)
    y += 30
    for tx in ["На занятия в школу и сад", "Для прогулок с родителями", "Под пиджак или кардиган", "Для уютных домашних вечеров"]:
        n = len(wrap(d, tx, body(600, 30), w - 90)); hh = 50 + n * 39
        d.rounded_rectangle([x0, y, x0 + w, y + hh], 22, fill=WHITE)
        d.ellipse([x0 + 26, y + hh / 2 - 10, x0 + 46, y + hh / 2 + 10], fill=PINK)
        para(d, (x0 + 66, y + 25), tx, body(600, 30), w - 90)
        y += hh + 16
    save(c, 5, "как_носить")


def s6():
    c, d = new("Уход", "06")
    pw = 560
    paste(c, crop(P("белый", 11), pw, H - 96 - M, fy=0.35), (M, 96), 26)
    x = M + pw + 90
    title2(d, x, 120, "ПРОСТОЙ", "УХОД", 84, W - M - x)
    y = 340
    for tx in ["Деликатная стирка или режим «Детская одежда», не выше 40 °C",
               "Отжим на средних оборотах — 600–800",
               "Сушить естественно, в тени, не на батарее"]:
        d.ellipse([x, y + 12, x + 12, y + 24], fill=INK)
        y = para(d, (x + 30, y), tx, body(600, 30), W - M - x - 30) + 26
    heart(d, x + 30, y + 70, 56, PINK)
    para(d, (x + 82, y + 40), "Сохраняет форму и цвет после стирок", body(500, 34), W - M - x - 90)
    save(c, 6, "уход")


for f in (s1, s2, s3, s4, s5, s6):
    f()
