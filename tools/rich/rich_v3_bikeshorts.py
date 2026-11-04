"""Рич «Велосипедки» в стандарте v3. Хелперы — из rich_template_v3_nightgowns.py.
Запуск: python3 rich_v3_bikeshorts.py <папка_фото> <папка_вывода> <Montserrat-VF.ttf> <любой_шрифт> [black|print]
black — однотонные чёрные 311ФЛ2F (детские 110–140) и 311ФЛ2(2)F (подростковые 146–164), хлопок 92% / эластан 8%;
print — велосипедки с принтом 311НАБ1F (98–140), кулирка с набивным рисунком, хлопок 95% / лайкра 5%.
Фото: <nmID>_<NN>.jpg (как в карточке WB)."""
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(here, "rich_template_v3_nightgowns.py"), encoding="utf-8").read()
exec(t[:t.index("# 01 Основная информация")])
BLACK = (sys.argv[5] if len(sys.argv) > 5 else "black") == "black"
C = {"дет": 254017094, "подр": 446602065,
     "бабочки": 2026847795, "бирюзовый": 2026847796, "буквы": 2026847797, "звезды": 2026847798,
     "сердечки+звезды": 2026847799, "цв.сердечки": 2026847800}


def save(c, n, name):
    c.resize((800, 500), Image.LANCZOS).save(os.path.join(OUT, f"велосипедки_{n}_{name}.jpg"), quality=93, subsampling=0)
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
    s = 84
    rows = [("ВЕЛОСИПЕДКИ", INK), ("ДЛЯ СПОРТА", INK), ("И КАЖДОГО ДНЯ" if BLACK else "С ЯРКИМ ПРИНТОМ", PINK)]
    while max(d.textlength(r[0], font=head(s)) for r in rows) > 600: s -= 2
    for i, (tx, col) in enumerate(rows):
        d.text((M, 205 + i * s * 1.15), tx, font=head(s), fill=col)
    y = 205 + 3 * s * 1.15
    sub = ("Мягкий хлопковый трикотаж — для физкультуры, танцев и под платье" if BLACK else
           "Хлопковый трикотаж с весёлыми принтами — для физкультуры, прогулок и дома")
    y = para(d, (M, y + 30), sub, body(500, 34), 600) + 40
    heart(d, M + 26, y + 26, 52, PINK)
    d.text((M + 76, y), "Размеры", font=body(500, 34), fill=INK)
    d.text((M + 76, y + 42), "от 110 до 164" if BLACK else "от 98 до 140", font=body(500, 34), fill=INK)
    shots = ([("дет", 8, 0.5, 0.35, 1.0), ("дет", 11, 0.5, 0.55, 1.0), ("дет", 14, 0.5, 0.35, 1.0)] if BLACK else
             [("буквы", 8, 0.5, 0.35, 1.0), ("бирюзовый", 9, 0.5, 0.4, 1.0), ("звезды", 5, 0.5, 0.4, 1.0)])
    x0, gap = 720, 18
    cw = (W - M - x0 - 2 * gap) // 3
    for i, (k, n, fx, fy, z) in enumerate(shots):
        paste(c, crop(P(k, n), cw, H - 110 - M, fx=fx, fy=fy, z=z), (x0 + i * (cw + gap), 110))
    save(c, 1, "основная_информация")


def s2():
    c, d = new("Преимущества", "02")
    gap = 22; top = 96
    cw = (W - 2 * M - 2 * gap) // 3; ch = (H - top - M - gap) // 2
    if BLACK:
        tiles = [("t", BLUE, "Мягкий пояс на резинке", "высокая посадка, не сползают"),
                 ("p", ("дет", 5, 0.5, 0.35)),
                 ("t", PINK, "Тянутся и не сковывают", "бег, прыжки, растяжка, гимнастика"),
                 ("p", ("дет", 12, 0.5, 0.55)),
                 ("t", PINK, "Базовый чёрный", "к любому верху, под платье и юбку"),
                 ("p", ("дет", 7, 0.5, 0.45))]
    else:
        tiles = [("t", BLUE, "Яркие принты", "бабочки, буквы, сердечки, звёзды"),
                 ("p", ("цв.сердечки", 9, 0.5, 0.5)),
                 ("t", PINK, "Тянутся и не сковывают", "бег, прыжки, танцы и игры"),
                 ("p", ("буквы", 9, 0.5, 0.75)),
                 ("t", PINK, "Мягкий пояс на резинке", "высокая посадка, не сползают"),
                 ("p", ("буквы", 7, 0.5, 0.45))]
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
    paste(c, crop(P("дет", 10) if BLACK else P("бирюзовый", 12), pw, H - 96 - M, fy=0.4 if BLACK else 0.5), (W - M - pw, 96), 26)
    badges = ([(BLUE, "92% хлопок"), (PINK, "8% эластан"), (BLUE, "мягкий трикотаж")] if BLACK else
              [(BLUE, "95% хлопок"), (PINK, "5% лайкра"), (BLUE, "набивной рисунок")])
    y = 200
    for i, (col, tx) in enumerate(badges):
        f = body(500, 46); bw = d.textlength(tx, font=f) + 150; x = M + (i % 2) * 60
        d.rounded_rectangle([x, y, x + bw, y + 116], 18, fill=col)
        sparkle(d, x + 56, y + 46, 26); sparkle(d, x + 34, y + 80, 12)
        d.text((x + 100, y + 58), tx, font=f, fill=WHITE, anchor="lm"); y += 160
    txt = ("Натуральный хлопок дышит и приятен к коже, а эластан помогает велосипедкам тянуться и садиться по фигуре" if BLACK else
           "Рисунок напечатан на самом трикотаже, поэтому ткань остаётся мягкой, дышит и хорошо тянется")
    para(d, (M, y + 30), txt, body(500, 32), W - M - pw - M - 60, GREY)
    save(c, 3, "ткань")


def s4():
    if BLACK:
        c, d = new("Модели", "04")
        gap = 22; top = 96
        cw = (W - 2 * M - 3 * gap) // 4; ch = H - top - M
        title2(d, M + 10, top + 40, "ВЫБЕРИТЕ", "СВОЮ МОДЕЛЬ", 52, cw - 10)
        para(d, (M + 10, top + 230), "Чёрные — для физкультуры и на каждый день, с принтом — для настроения",
             body(500, 28), cw - 20, GREY)
        items = [("дет", 8, 0.5, 0.42, 1.0, "Детские", "110–140"), ("подр", 8, 0.5, 0.42, 1.0, "Подростковые", "146–164"),
                 ("буквы", 18, 0.5, 0.45, 1.0, "С принтом", "98–140")]
        for i, (k, n, fx, fy, z, cap, sz) in enumerate(items, 1):
            x = M + i * (cw + gap); y = top
            paste(c, crop(P(k, n), cw, ch, fx=fx, fy=fy, z=z), (x, y), 26)
            f1, f2 = body(700, 26), body(500, 22)
            bw = cw - 28; bh = 112
            d.rounded_rectangle([x + 14, y + ch - bh - 14, x + 14 + bw, y + ch - 14], 18, fill=WHITE)
            d.text((x + 32, y + ch - bh + 2), cap, font=f1, fill=INK)
            d.text((x + 32, y + ch - bh + 36), f"размеры {sz}", font=f2, fill=GREY)
            d.text((x + 32, y + ch - bh + 66), f"арт. {C[k]}", font=f2, fill=PINK)
        save(c, 4, "модели")
        return
    c, d = new("Расцветки", "04")
    y = title2(d, M, 90, "6 ВЕСЁЛЫХ", "ПРИНТОВ", 56, 600)
    para(d, (M + 640, 110), "Бабочки, буквы, сердечки и звёзды — выберите любимый рисунок или возьмите два на смену",
         body(500, 30), W - 2 * M - 640, GREY)
    shots = [("бабочки", "бабочки", 5, 0.5, 0.45, 1.0), ("бирюзовый", "бирюзовый", 5, 0.5, 0.45, 1.0),
             ("буквы", "буквы", 15, 0.5, 0.72, 1.6), ("звёзды", "звезды", 1, 0.45, 0.4, 1.0),
             ("сердечки и звёзды", "сердечки+звезды", 5, 0.5, 0.5, 1.0), ("цветные сердечки", "цв.сердечки", 8, 0.5, 0.5, 1.0)]
    gap = 16; top = 300
    cw = (W - 2 * M - 5 * gap) // 6; ch = H - top - M
    for i, (nm, k, n, fx, fy, z) in enumerate(shots):
        x = M + i * (cw + gap)
        paste(c, crop(P(k, n), cw, ch, fx=fx, fy=fy, z=z), (x, top), 22)
        f = body(600, 20); f2 = body(500, 18)
        tw = max(d.textlength(nm, font=f), d.textlength(f"арт. {C[k]}", font=f2)) + 24
        d.rounded_rectangle([x + (cw - tw) / 2, H - M - 74, x + (cw + tw) / 2, H - M - 12], 12, fill=WHITE)
        d.text((x + cw / 2, H - M - 56), nm, font=f, fill=INK, anchor="mm")
        d.text((x + cw / 2, H - M - 30), f"арт. {C[k]}", font=f2, fill=PINK, anchor="mm")
    save(c, 4, "расцветки")


def s5():
    c, d = new("Производство", "05")
    d.text((M, 130), "СОБСТВЕННОЕ", font=head(70), fill=INK)
    d.text((M, 215), "ПРОИЗВОДСТВО", font=head(70), fill=PINK)
    d.text((M, 300), "В РОССИИ", font=head(70), fill=INK)
    y = para(d, (M, 420), "Шьём детскую одежду сами, с вниманием к каждому шву и детали", body(500, 32), 700) + 36
    pts = ["Сделано в России, г. Иваново", "Более 400 000 счастливых детей", "Более 5 лет на рынке",
           "Средняя оценка велосипедок — 4,9"]
    for tx in pts:
        d.ellipse([M, y + 12, M + 14, y + 26], fill=PINK); d.text((M + 32, y), tx, font=body(600, 32), fill=INK); y += 58
    d.text((M, H - M - 50), "T O T E M F O X", font=body(600, 34), fill=LINE)
    pw = 640
    paste(c, crop(P("дет", 13) if BLACK else P("буквы", 14), pw, H - 96 - M, fy=0.45), (W - M - pw, 96), 26)
    save(c, 5, "производство")


def s6():
    c, d = new("Ваши вопросы", "06")
    d.rectangle([0, 70, W, H], fill=(243, 239, 233))
    d.text((W / 2, 112), "ВАШИ ВОПРОСЫ", font=head(56), fill=INK, anchor="mm")
    if BLACK:
        qa = [("Подойдут для физкультуры и гимнастики?",
               "Да. Из отзывов: «Ходим на гимнастику в них. Всё отлично. Удобные, качественные»."),
              ("Как выбрать размер?",
               "Ориентируйтесь на рост ребёнка и таблицу замеров. Если ребёнок между размерами — возьмите на размер больше."),
              ("Есть размеры для подростков?",
               "Да: детские — 110–140 (арт. 254017094), подростковые — 146–164 (арт. 446602065).")]
    else:
        qa = [("Подойдут для физкультуры и танцев?",
               "Да. Хлопковый трикотаж с лайкрой тянется и не сковывает движений, а пояс на резинке не даёт сползать."),
              ("Принт не жёсткий?",
               "Рисунок напечатан на самой ткани, поэтому велосипедки остаются мягкими и приятными к телу."),
              ("Как выбрать размер?",
               "Ориентируйтесь на рост ребёнка и таблицу замеров. Если ребёнок между размерами — возьмите на размер больше.")]
    y = 168
    fq, fa = body(500, 27), body(500, 27)
    for q, a in qa:
        lines = wrap(d, q, fq, 640); h = 34 + len(lines) * 35
        d.rounded_rectangle([M + 60, y, M + 60 + 760, y + h], 22, fill=WHITE)
        d.text((M + 90, y + h / 2), "?", font=head(52), fill=PINK, anchor="mm")
        para(d, (M + 140, y + 17), q, fq, 640, INK, 1.3)
        y += h + 10
        lines = wrap(d, a, fa, 760); h = 34 + len(lines) * 35
        x = W - M - 60 - 880
        d.rounded_rectangle([x, y, x + 880, y + h], 22, fill=WHITE)
        d.text((x + 34, y + h / 2), "!", font=head(52), fill=PINK, anchor="mm")
        para(d, (x + 80, y + 17), a, fa, 760, INK, 1.3)
        y += h + 18
    save(c, 6, "ваши_вопросы")


def s7():
    c, d = new("Уход", "07")
    pw = 560
    paste(c, crop(P("дет", 9) if BLACK else P("цв.сердечки", 7), pw, H - 96 - M, fy=0.45 if BLACK else 0.5), (M, 96), 26)
    x = M + pw + 80
    y = title2(d, x, 110, "ПРОСТОЙ", "УХОД", 84, W - M - x)
    sub = ("При бережном уходе велосипедки надолго сохранят вид" if BLACK else
           "При бережном уходе принт надолго останется ярким")
    rules = (["Бережная стирка при 30 °C", "Стирать наизнанку", "Без сильного отжима", "Сушить в расправленном виде"] if BLACK else
             ["Бережная стирка при 30 °C", "Стирать наизнанку, с похожими цветами", "Без сильного отжима",
              "Сушить в расправленном виде"])
    y = para(d, (x, y + 34), sub, body(500, 30), W - M - x, GREY) + 30
    f = body(600, 29)
    for i, tx in enumerate(rules, 1):
        n = len(wrap(d, tx, f, W - M - x - 100)); hh = 30 + n * 38
        d.rounded_rectangle([x, y, W - M, y + hh], 20, fill=WHITE)
        d.ellipse([x + 18, y + hh / 2 - 22, x + 62, y + hh / 2 + 22], fill=PINK if i % 2 else BLUE)
        d.text((x + 40, y + hh / 2), str(i), font=head(26), fill=WHITE, anchor="mm")
        para(d, (x + 84, y + 15), tx, f, W - M - x - 100)
        y += hh + 14
    save(c, 7, "уход")


for fn in (s1, s2, s3, s4, s5, s6, s7):
    fn()
