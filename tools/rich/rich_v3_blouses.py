"""Общий рич «Школьные блузки» в стандарте v3. Хелперы — из rich_template_v3_nightgowns.py.
Запуск: python3 rich_v3_blouses.py <папка_фото> <папка_вывода> <Montserrat-VF.ttf> <любой_шрифт> [lace|plain]
lace  — для моделей с кружевом (401ФЛ3F, 4F, 8F, 10F, 11F, 18F);
plain — для нарядных без кружева (401ФЛ15F, 5F, 6F): другие тексты на слайдах 01, 02, 03, 07, 08.
Фото: <nmID>_<NN>.jpg (как в карточке WB)."""
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
t = open(os.path.join(here, "rich_template_v3_nightgowns.py"), encoding="utf-8").read()
exec(t[:t.index("# 01 Основная информация")])
LACE = (sys.argv[5] if len(sys.argv) > 5 else "lace") == "lace"
C = {"3F": 459578952, "10F": 309902207, "8F": 458437324, "4F": 459594111, "11F": 309909133, "18F": 1483546172,
     "15F": 1267235473, "5F": 1841075081,
     "10F_голубой": 309902209, "10F_молочный": 309902208, "10F_розовый": 309902210, "10F_серый": 309902206,
     "10F_сиреневый": 309902211, "10F_темно-синий": 309902212, "10F_бордовый": 309902213}


def save(c, n, name):
    c.resize((800, 500), Image.LANCZOS).save(os.path.join(OUT, f"блузки_{n}_{name}.jpg"), quality=93, subsampling=0)
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
    rows = [("ШКОЛЬНАЯ", INK), ("БЛУЗКА", INK), ("С КРУЖЕВОМ" if LACE else "НАРЯДНАЯ", PINK)]
    while max(d.textlength(r[0], font=head(s)) for r in rows) > 600: s -= 2
    for i, (tx, col) in enumerate(rows):
        d.text((M, 205 + i * s * 1.15), tx, font=head(s), fill=col)
    y = 205 + 3 * s * 1.15
    sub = ("Мягкий хлопковый трикотаж и нежное кружево — для школы и праздников" if LACE else
           "Мягкий хлопковый трикотаж и нарядные детали — для школы и праздников")
    y = para(d, (M, y + 30), sub, body(500, 34), 600) + 40
    heart(d, M + 26, y + 26, 52, PINK)
    d.text((M + 76, y), "Размеры", font=body(500, 34), fill=INK)
    d.text((M + 76, y + 42), "от 128 до 164" if LACE else "от 128 до 170", font=body(500, 34), fill=INK)
    shots = [("3F", 10, 0.3), ("8F", 13, 0.3), ("11F", 9, 0.3)] if LACE else [("15F", 6, 0.3), ("5F", 1, 0.3), ("15F", 9, 0.3)]
    x0, gap = 720, 18
    cw = (W - M - x0 - 2 * gap) // 3
    for i, (k, n, fy) in enumerate(shots):
        paste(c, crop(P(k, n), cw, H - 110 - M, fy=fy, z=1.1), (x0 + i * (cw + gap), 110))
    save(c, 1, "основная_информация")


def s2():
    c, d = new("Преимущества", "02")
    gap = 22; top = 96
    cw = (W - 2 * M - 2 * gap) // 3; ch = (H - top - M - gap) // 2
    if LACE:
        tiles = [("t", BLUE, "Нежное кружево", "на кокетке, рукавах и воланах"),
                 ("p", ("10F", 13, 0.5, 0.45)),
                 ("t", PINK, "Мягкая и приятная к телу", "комфортно весь учебный день"),
                 ("p", ("11F", 20, 0.5, 0.5)),
                 ("t", PINK, "Тянется и держит форму", "не сковывает движения"),
                 ("p", ("8F", 15, 0.5, 0.45))]
    else:
        tiles = [("t", BLUE, "Нарядные детали", "шифоновые рукава, жабо, рюши"),
                 ("p", ("15F", 11, 0.5, 0.45)),
                 ("t", PINK, "Мягкая и приятная к телу", "комфортно весь учебный день"),
                 ("p", ("5F", 5, 0.5, 0.45)),
                 ("t", PINK, "Тянется и держит форму", "не сковывает движения"),
                 ("p", ("15F", 10, 0.5, 0.45))]
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
    paste(c, crop(P("3F", 15) if LACE else P("15F", 10), pw, H - 96 - M, fy=0.45), (W - M - pw, 96), 26)
    badges = [(BLUE, "92% хлопок"), (PINK, "кулирная гладь"), (BLUE, "эластичное кружево" if LACE else "8% эластан")]
    y = 200
    for i, (col, tx) in enumerate(badges):
        f = body(500, 46); bw = d.textlength(tx, font=f) + 150; x = M + (i % 2) * 60
        d.rounded_rectangle([x, y, x + bw, y + 116], 18, fill=col)
        sparkle(d, x + 56, y + 46, 26); sparkle(d, x + 34, y + 80, 12)
        d.text((x + 100, y + 58), tx, font=f, fill=WHITE, anchor="lm"); y += 160
    para(d, (M, y + 30), "Натуральный трикотаж дышит и приятен к коже, а эластан помогает блузке держать форму",
         body(500, 32), W - M - pw - M - 60, GREY)
    save(c, 3, "ткань")


def s4():
    c, d = new("Модели", "04")
    gap = 20; top = 96
    cw = (W - 2 * M - 3 * gap) // 4; ch = (H - top - M - gap) // 2
    title2(d, M + 10, top + 40, "ВЫБЕРИТЕ", "СВОЮ МОДЕЛЬ", 54, cw - 10)
    para(d, (M + 10, top + 230), "Белый верх для линейки и цветные — на каждый день", body(500, 28), cw - 20, GREY)
    items = [("3F", 10, 0.32, 1.5, "Кружевные рукава"), ("10F", 17, 0.27, 1.9, "Кружевная кокетка"),
             ("8F", 13, 0.3, 1.35, "Длинный рукав"), ("4F", 12, 0.35, 1.0, "Кружево с воланом"),
             ("11F", 19, 0.4, 1.0, "Воротник «питер-пэн»"), ("18F", 7, 0.3, 1.7, "Рукава-фонарики"),
             ("15F", 6, 0.38, 1.2, "Шифоновые рукава")]
    for i, (k, n, fy, z, cap) in enumerate(items, 1):
        x = M + (i % 4) * (cw + gap); y = top + (i // 4) * (ch + gap)
        paste(c, crop(P(k, n), cw, ch, fy=fy, z=z), (x, y), 26)
        f1, f2 = body(700, 25), body(500, 21)
        bw = cw - 28; bh = 82
        d.rounded_rectangle([x + 14, y + ch - bh - 14, x + 14 + bw, y + ch - 14], 18, fill=WHITE)
        d.text((x + 32, y + ch - bh + 2), cap, font=f1, fill=INK)
        d.text((x + 32, y + ch - bh + 38), f"арт. {C[k]}", font=f2, fill=PINK)
    save(c, 4, "модели")


def s5():
    c, d = new("Расцветки", "05")
    y = title2(d, M, 90, "8 НЕЖНЫХ", "ОТТЕНКОВ", 56, 600)
    para(d, (M + 640, 110), "Классический белый для торжественных дней и мягкие пастельные цвета — на каждый день",
         body(500, 30), W - 2 * M - 640, GREY)
    shots = [("белый", "10F", 3), ("молочный", "10F_молочный", 3), ("голубой", "10F_голубой", 3), ("розовый", "10F_розовый", 3),
             ("сиреневый", "10F_сиреневый", 3), ("серый", "10F_серый", 3), ("тёмно-синий", "10F_темно-синий", 3),
             ("бордовый", "10F_бордовый", 2)]
    gap = 14; top = 300
    cw = (W - 2 * M - 7 * gap) // 8; ch = H - top - M
    for i, (nm, k, n) in enumerate(shots):
        x = M + i * (cw + gap)
        paste(c, crop(P(k, n), cw, ch, fy=0.35 if n == 3 else 0.3, z=1.25 if n == 3 else 1.9), (x, top), 22)
        f = body(600, 22); tw = d.textlength(nm, font=f) + 28
        d.rounded_rectangle([x + (cw - tw) / 2, H - M - 56, x + (cw + tw) / 2, H - M - 14], 12, fill=WHITE)
        d.text((x + cw / 2, H - M - 35), nm, font=f, fill=INK, anchor="mm")
    save(c, 5, "расцветки")


def s6():
    c, d = new("Производство", "06")
    d.text((M, 130), "СОБСТВЕННОЕ", font=head(70), fill=INK)
    d.text((M, 215), "ПРОИЗВОДСТВО", font=head(70), fill=PINK)
    d.text((M, 300), "В РОССИИ", font=head(70), fill=INK)
    y = para(d, (M, 420), "Шьём школьную одежду сами, с вниманием к каждому шву и детали", body(500, 32), 700) + 36
    pts = ["Сделано в России, г. Иваново", "Более 400 000 счастливых детей", "Более 5 лет на рынке",
           "Средняя оценка блузок — 4,9"]
    for tx in pts:
        d.ellipse([M, y + 12, M + 14, y + 26], fill=PINK); d.text((M + 32, y), tx, font=body(600, 32), fill=INK); y += 58
    d.text((M, H - M - 50), "T O T E M F O X", font=body(600, 34), fill=LINE)
    pw = 640
    paste(c, crop(P("18F", 7), pw, H - 96 - M, fy=0.4), (W - M - pw, 96), 26)
    save(c, 6, "производство")


def s7():
    c, d = new("Ваши вопросы", "07")
    d.rectangle([0, 70, W, H], fill=(243, 239, 233))
    d.text((W / 2, 112), "ВАШИ ВОПРОСЫ", font=head(56), fill=INK, anchor="mm")
    qa = [("Кружево не колется? Ребёнку будет комфортно?" if LACE else "Ткань не колется? Ребёнку будет комфортно?",
           "Основа — мягкий трикотаж из хлопка. Покупатели пишут: «Переживала, что кружева будут колоться, — очень нежные и приятные к телу»."
           if LACE else "Основа — мягкий трикотаж из хлопка: покупатели отмечают, что блузки мягкие и приятные к телу."),
          ("Как выбрать размер?",
           "Блузка облегает фигуру. Ориентируйтесь на рост ребёнка; если он между размерами или любит посвободнее — возьмите на размер больше."),
          ("Блузка сохранит вид после стирок?",
           "При бережном уходе — да. Из отзывов: «После стирки не полиняла, не вытянулась, не села, хорошо гладится».")]
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
    save(c, 7, "ваши_вопросы")


def s8():
    c, d = new("Уход", "08")
    pw = 560
    paste(c, crop(P("10F", 8) if LACE else P("15F", 11), pw, H - 96 - M, fy=0.4), (M, 96), 26)
    x = M + pw + 80
    if LACE:
        y = title2(d, x, 110, "КАК СОХРАНИТЬ", "КРУЖЕВО", 72, W - M - x)
        sub = "Кружево эластичное — ему нужен бережный уход"
        rules = ["Бережная или деликатная стирка", "Стирка отдельно от вещей с молниями", "Без сильного отжима",
                 "Стирка отдельно от вещей с ворсом или начёсом", "Гладить с изнанки, не касаясь кружева"]
    else:
        y = title2(d, x, 110, "ПРОСТОЙ", "УХОД", 84, W - M - x)
        sub = "При бережном уходе блузка надолго сохранит вид"
        rules = ["Бережная или деликатная стирка при 30 °C", "Стирка отдельно от вещей с молниями", "Без сильного отжима",
                 "Гладить с изнанки"]
    y = para(d, (x, y + 34), sub, body(500, 30), W - M - x, GREY) + 30
    f = body(600, 29)
    for i, tx in enumerate(rules, 1):
        n = len(wrap(d, tx, f, W - M - x - 100)); hh = 30 + n * 38
        d.rounded_rectangle([x, y, W - M, y + hh], 20, fill=WHITE)
        d.ellipse([x + 18, y + hh / 2 - 22, x + 62, y + hh / 2 + 22], fill=PINK if i % 2 else BLUE)
        d.text((x + 40, y + hh / 2), str(i), font=head(26), fill=WHITE, anchor="mm")
        para(d, (x + 84, y + 15), tx, f, W - M - x - 100)
        y += hh + 14
    save(c, 8, "уход")


for fn in (s1, s2, s3, s4, s5, s6, s7, s8):
    fn()
