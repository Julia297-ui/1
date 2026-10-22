"""Рич «Ночные сорочки» v2 — в стилистике конкурента (белый фон, подпись раздела + номер,
двухцветные заголовки, розовые/голубые плитки, чат «Ваши вопросы»). 800×500, рисуем 1600×1000."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, BODY, HEAD = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
W, H = 1600, 1000
M = 64
WHITE = (255, 255, 255)
MILK = (250, 248, 244)
INK = (92, 84, 78)
GREY = (160, 150, 140)
LINE = (228, 221, 212)
PINK = (204, 138, 148)
BLUE = (139, 168, 186)
SOFTP = (253, 232, 243)
SOFTB = (226, 243, 252)
C = {"бирюзовый": 613600365, "сердечки": 613600366, "авокадо": 650646660, "леопард": 650646661, "пони": 699282365,
     "собачка": 830501384, "кор.леопард": 830501385, "бел.сердечки": 881695179, "розочки": 1207969238,
     "горох": 1515962002, "розовые сердечки": 1211856227}


def body(w, s):
    f = ImageFont.truetype(BODY, s); f.set_variation_by_axes([w]); return f


def head(s):
    f = ImageFont.truetype(BODY, s); f.set_variation_by_axes([600]); return f


def P(k, n):
    return Image.open(os.path.join(SRC, f"{C[k]}_{n:02d}.jpg")).convert("RGB")


def crop(im, w, h, fx=0.5, fy=0.5, z=1.0):
    if z > 1:
        cw, chh = im.width / z, im.height / z
        x = min(max(im.width * fx - cw / 2, 0), im.width - cw); y = min(max(im.height * fy - chh / 2, 0), im.height - chh)
        im = im.crop((round(x), round(y), round(x + cw), round(y + chh))); fx = fy = 0.5
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(round(im.width * fx - w / 2), 0), im.width - w); y = min(max(round(im.height * fy - h / 2), 0), im.height - h)
    return im.crop((x, y, x + w, y + h))


def paste(c, im, xy, r=28):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    c.paste(im, xy, m)


def new(label, num):
    c = Image.new("RGB", (W, H), MILK); d = ImageDraw.Draw(c)
    f = body(400, 26)
    d.text((M, 34), label, font=f, fill=GREY)
    tw = d.textlength(label, font=f)
    d.text((W - M, 34), num, font=f, fill=GREY, anchor="ra")
    d.line([(M + tw + 24, 50), (W - M - 60, 50)], fill=LINE, width=2)
    return c, d


def wrap(d, t, f, w):
    out, cur = [], ""
    for word in t.split():
        s = (cur + " " + word).strip()
        if d.textlength(s, font=f) <= w: cur = s
        else: out.append(cur); cur = word
    return out + [cur]


def para(d, xy, t, f, w, fill=INK, lh=1.3):
    x, y = xy
    for ln in wrap(d, t, f, w):
        d.text((x, y), ln, font=f, fill=fill); y += f.size * lh
    return y


def heart(d, cx, cy, s, fill=(255, 214, 64)):
    r = s * 0.28
    d.ellipse([cx - s * 0.5, cy - s * 0.45, cx - s * 0.5 + 2 * r, cy - s * 0.45 + 2 * r], fill=fill)
    d.ellipse([cx + s * 0.5 - 2 * r, cy - s * 0.45, cx + s * 0.5, cy - s * 0.45 + 2 * r], fill=fill)
    d.polygon([(cx - s * 0.5 + 2, cy - s * 0.2), (cx + s * 0.5 - 2, cy - s * 0.2), (cx, cy + s * 0.48)], fill=fill)


def sparkle(d, cx, cy, s, fill=WHITE):
    d.polygon([(cx, cy - s), (cx + s * 0.22, cy - s * 0.22), (cx + s, cy), (cx + s * 0.22, cy + s * 0.22),
               (cx, cy + s), (cx - s * 0.22, cy + s * 0.22), (cx - s, cy), (cx - s * 0.22, cy - s * 0.22)], fill=fill)


def save(c, n, name):
    c.resize((800, 500), Image.LANCZOS).save(os.path.join(OUT, f"сорочки_{n}_{name}.jpg"), quality=93, subsampling=0)
    print("saved", n, name)


# 01 Основная информация
def s1():
    c, d = new("Основная информация", "01")
    d.text((M, 150), "T O T E M F O X", font=body(600, 26), fill=GREY)
    hs = 92
    while d.textlength("ИЗ ХЛОПКА", font=head(hs)) > 690 - M - 40: hs -= 2
    d.text((M, 205), "СОРОЧКА", font=head(hs), fill=PINK)
    d.text((M, 205 + hs * 1.2), "ИЗ ХЛОПКА", font=head(hs), fill=INK)
    para(d, (M, 460), "Нежная домашняя сорочка для сна и отдыха из 100% хлопка", body(500, 36), 560)
    heart(d, M + 26, 690, 52, PINK)
    d.text((M + 76, 664), "Размерный ряд", font=body(500, 34), fill=INK)
    d.text((M + 76, 706), "от 128 до 164", font=body(500, 34), fill=INK)
    shots = [("авокадо", 9, 0.28), ("леопард", 8, 0.28), ("розовые сердечки", 8, 0.28)]
    x0, gap = 690, 18
    cw = (W - M - x0 - 2 * gap) // 3
    for i, (k, n, fy) in enumerate(shots):
        paste(c, crop(P(k, n), cw, H - 110 - M, fy=fy, z=1.15), (x0 + i * (cw + gap), 110))
    save(c, 1, "основная_информация")


# 02 Преимущества
def s2():
    c, d = new("Преимущества", "02")
    gap = 22; top = 96
    cw = (W - 2 * M - 2 * gap) // 3; ch = (H - top - M - gap) // 2
    tiles = [("t", BLUE, "Ровные и прочные швы", "аккуратная строчка — прослужит долго"),
             ("p", ("сердечки", 9, 0.5, 0.35, 1.0)),
             ("t", PINK, "Свободный А-силуэт", "ничего не сковывает во сне"),
             ("p", ("леопард", 9, 0.5, 0.45, 1.0)),
             ("t", PINK, "Яркий принт", "не выцветает и не линяет после стирок"),
             ("p", ("авокадо", 11, 0.5, 0.5, 1.0))]
    for i, t in enumerate(tiles):
        x = M + (i % 3) * (cw + gap); y = top + (i // 3) * (ch + gap)
        if t[0] == "t":
            d.rounded_rectangle([x, y, x + cw, y + ch], 26, fill=t[1])
            yy = para(d, (x + 34, y + 36), t[2], body(700, 40), cw - 68, WHITE, 1.15)
            para(d, (x + 34, y + ch - 140), t[3], body(500, 30), cw - 68, WHITE, 1.25)
        else:
            k, n, fx, fy, z = t[1]
            paste(c, crop(P(k, n), cw, ch, fx, fy, z), (x, y), 26)
    save(c, 2, "преимущества")


# 03 Ткань
def s3():
    c, d = new("Ткань", "03")
    pw = 660
    paste(c, crop(P("сердечки", 9), pw, H - 96 - M, fy=0.45), (W - M - pw, 96), 26)
    badges = [(BLUE, "100% хлопок"), (PINK, "дышащий трикотаж"), (BLUE, "кулирная гладь")]
    y = 200
    for i, (col, t) in enumerate(badges):
        f = body(500, 48)
        bw = d.textlength(t, font=f) + 150; x = M + (i % 2) * 60
        d.rounded_rectangle([x, y, x + bw, y + 120], 18, fill=col)
        sparkle(d, x + 56, y + 48, 26); sparkle(d, x + 34, y + 82, 12)
        d.text((x + 100, y + 60), t, font=f, fill=WHITE, anchor="lm")
        y += 165
    para(d, (M, y + 30), "Мягкая натуральная ткань приятна к коже, хорошо пропускает воздух — ночью не жарко", body(500, 32), W - M - pw - M - 60, GREY)
    save(c, 3, "ткань")


# 04 Большой выбор расцветок
def s4():
    c, d = new("Большой выбор расцветок", "04")
    shots = [("авокадо", 8), ("бирюзовый", 7), ("коричневый", None), ("собачка", 7), ("пони", 7)]
    shots = [("авокадо", 8), ("бирюзовый", 7), ("кор.леопард", 7), ("собачка", 7), ("пони", 7)]
    gap = 16; top = 96
    cw = (W - 2 * M - 4 * gap) // 5; ch = H - top - M
    for i, (k, n) in enumerate(shots):
        x = M + i * (cw + gap)
        paste(c, crop(P(k, n), cw, ch, fy=0.4, z=1.1), (x, top), 22)
        t = f"арт. {C[k]}"; f = body(600, 24); tw = d.textlength(t, font=f) + 30
        d.rounded_rectangle([x + 14, top + 300, x + 14 + tw, top + 344], 10, fill=WHITE)
        d.text((x + 29, top + 322), t, font=f, fill=INK, anchor="lm")
    bx, by = M + cw + gap + 40, H - M - 230
    d.rounded_rectangle([bx, by, bx + 560, by + 200], 24, fill=PINK)
    d.text((bx + 34, by + 30), "11 ПРИНТОВ", font=head(54), fill=WHITE)
    d.text((bx + 34, by + 112), "от нежных до ярких —", font=body(500, 32), fill=WHITE)
    d.text((bx + 34, by + 150), "соберите любимые", font=body(500, 32), fill=WHITE)
    save(c, 4, "расцветки")


# 05 Производство
def s5():
    c, d = new("Производство", "05")
    d.text((M, 130), "СОБСТВЕННОЕ", font=head(70), fill=INK)
    d.text((M, 215), "ПРОИЗВОДСТВО", font=head(70), fill=PINK)
    d.text((M, 300), "В РОССИИ", font=head(70), fill=INK)
    y = para(d, (M, 420), "Шьём детскую одежду сами, с вниманием к каждому шву и детали", body(500, 32), 700) + 36
    pts = ["Сделано в России, г. Иваново", "Более 400 000 счастливых детей", "Более 5 лет на рынке", "Рейтинг магазина 4,9"]
    for t in pts:
        d.ellipse([M, y + 12, M + 14, y + 26], fill=PINK); d.text((M + 32, y), t, font=body(600, 32), fill=INK); y += 58
    d.text((M, H - M - 50), "T O T E M F O X", font=body(600, 34), fill=LINE)
    pw = 640
    paste(c, crop(P("леопард", 7), pw, H - 96 - M, fy=0.4), (W - M - pw, 96), 26)
    save(c, 5, "производство")


# 06 Ваши вопросы
def s6():
    c, d = new("Ваши вопросы", "06")
    d.rectangle([0, 70, W, H], fill=(243, 239, 233))
    d.text((W / 2, 112), "ВАШИ ВОПРОСЫ", font=head(56), fill=INK, anchor="mm")
    qa = [("Сорочка не жаркая? Ребёнок не вспотеет ночью?",
           "Сорочка сшита из 100% хлопка — кулирная гладь дышит, в ней комфортно и летом, и в отопительный сезон."),
          ("Не сядет и не полиняет после стирки?",
           "Покупатели пишут: «После стирки не села, не потянулась, не потеряла свой цвет»."),
          ("Если не подойдёт размер, можно вернуть?",
           "Сорочки — бельевой товар и по закону не подлежат возврату. Примерьте сорочку на пункте выдачи до выкупа.")]
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


# 07 Уход
def s7():
    c, d = new("Уход", "07")
    pw = 560
    paste(c, crop(P("пони", 13), pw, H - 96 - M, fy=0.35), (M, 96), 26)
    x = M + pw + 90
    d.text((x, 130), "ПРОСТОЙ", font=head(84), fill=INK)
    d.text((x, 232), "УХОД", font=head(84), fill=PINK)
    para(d, (x, 370), "При правильном уходе сорочка сохранит внешний вид надолго", body(500, 32), W - M - x)
    y = 500
    for t in ["Стирка при температуре не выше 30 °C", "Стирать наизнанку, с похожими цветами",
              "Без отбеливателя", "Сушить в расправленном виде"]:
        d.ellipse([x, y + 12, x + 12, y + 24], fill=INK); d.text((x + 30, y), t, font=body(600, 30), fill=INK); y += 56
    heart(d, x + 30, y + 90, 56, PINK)
    para(d, (x + 82, y + 60), "Не садится и не линяет после стирок", body(500, 34), W - M - x - 90)
    save(c, 7, "уход")


for f in (s1, s2, s3, s4, s5, s6, s7):
    f()
