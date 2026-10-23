"""Серия инфографики для фото карточки 175334027 (231РНАБ1(1)F/зайкинасером) в стиле бренда v3.
900×1200 (рисуем 1800×2400). Исходники — фото карточки 01.jpg…11.jpg.
Запуск: python3 card_photos_v3_175334027.py <папка_фото> <папка_вывода> <Montserrat-VF.ttf>"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

SRC, OUT, FONT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
W, H, M = 1800, 2400, 96
MILK, INK, PINK, BLUE, GREY, WHITE = (250, 248, 244), (92, 84, 78), (204, 138, 148), (139, 168, 186), (160, 150, 140), (255, 255, 255)


def f(w, s):
    x = ImageFont.truetype(FONT, s); x.set_variation_by_axes([w]); return x


def P(n, box=None):
    im = Image.open(os.path.join(SRC, f"{n:02d}.jpg")).convert("RGB")
    if box:
        im = im.crop((round(box[0] * im.width), round(box[1] * im.height), round(box[2] * im.width), round(box[3] * im.height)))
    return im


def fit(im, w, h, fx=0.5, fy=0.5):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(round(im.width * fx - w / 2), 0), im.width - w); y = min(max(round(im.height * fy - h / 2), 0), im.height - h)
    return im.crop((x, y, x + w, y + h))


def paste(c, im, xy, r=56):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    c.paste(im, xy, m)


def wrap(d, t, fn, w):
    out, cur = [], ""
    for word in t.split():
        s = (cur + " " + word).strip()
        if d.textlength(s, font=fn) <= w: cur = s
        else: out.append(cur); cur = word
    return out + [cur]


def sparkle(d, cx, cy, s, fill=WHITE):
    d.polygon([(cx, cy - s), (cx + s * .22, cy - s * .22), (cx + s, cy), (cx + s * .22, cy + s * .22),
               (cx, cy + s), (cx - s * .22, cy + s * .22), (cx - s, cy), (cx - s * .22, cy - s * .22)], fill=fill)


def header(a, b, sub=None):
    c = Image.new("RGB", (W, H), MILK); d = ImageDraw.Draw(c)
    d.text((M, 96), "T O T E M F O X", font=f(600, 40), fill=GREY)
    s = 132
    while max(d.textlength(a, font=f(600, s)), d.textlength(b, font=f(600, s))) > W - 2 * M: s -= 4
    d.text((M, 170), a, font=f(600, s), fill=INK)
    d.text((M, 170 + s * 1.12), b, font=f(600, s), fill=PINK)
    y = 170 + s * 2.3
    if sub:
        for ln in wrap(d, sub, f(500, 54), W - 2 * M):
            d.text((M, y + 10), ln, font=f(500, 54), fill=GREY); y += 70
    return c, d, round(y + 50)


def pill(d, x, y, t, col, size=56, star=True):
    fn = f(600, size); tw = d.textlength(t, font=fn)
    pad = 120 if star else 56; h = size * 2.3
    d.rounded_rectangle([x, y, x + tw + pad + 56, y + h], 40, fill=col)
    if star:
        sparkle(d, x + 62, y + h / 2 - 8, 30); sparkle(d, x + 36, y + h / 2 + 30, 13)
    d.text((x + pad, y + h / 2), t, font=fn, fill=WHITE, anchor="lm")
    return y + h


def save(c, n, name):
    c.resize((900, 1200), Image.LANCZOS).save(os.path.join(OUT, f"175334027_{n}_{name}.jpg"), quality=94, subsampling=0)
    print("saved", n, name)


# 1 Ткань
c, d, y = header("МЯГКИЙ", "ХЛОПОК", "Нежный трикотаж для чувствительной кожи малыша")
paste(c, fit(P(8), W - 2 * M, H - y - M, fy=0.45), (M, y))
yy = H - M - 3 * 150 - 60
for i, (t, col) in enumerate([("95% хлопок", BLUE), ("дышащий материал", PINK), ("гипоаллергенный", BLUE)]):
    pill(d, M + 50 + (i % 2) * 60, yy + i * 150, t, col)
save(c, 1, "ткань")

# 2 Воротник
c, d, y = header("ВОРОТНИК", "НА КНОПКАХ", "Легко надеть через голову — без слёз и капризов")
ph = H - y - M; pw = (W - 2 * M - 40) // 2
paste(c, fit(P(5, (0.40, 0.24, 1, 1)), pw, ph, fx=0.0, fy=0.3), (M, y))
paste(c, fit(P(3, (0, 0.22, 1, 1)), pw, ph, fy=0.25), (M + pw + 40, y))
pill(d, M + 40, H - M - 330, "кнопки на плече", PINK, 50)
pill(d, M + 40, H - M - 170, "мягкая высокая стойка", BLUE, 50)
save(c, 2, "воротник")

# 3 Удобно играть
c, d, y = header("НЕ СКОВЫВАЕТ", "ДВИЖЕНИЙ", "Тянется вместе с малышом — удобно играть, ползать и бегать")
paste(c, fit(P(2), W - 2 * M, H - y - M, fy=0.4), (M, y))
yy = y + 70
for i, (t, col) in enumerate([("5% эластана", PINK), ("мягкие манжеты", BLUE), ("плотно прилегает", PINK)]):
    pill(d, M + 50, yy + i * 150, t, col, 54)
save(c, 3, "движение")

# 4 Принт
c, d, y = header("ЗАЙКИ", "И ГОРОШЕК", "Нежный принт, который радует и малыша, и маму")
pw = (W - 2 * M - 40) // 2; ph = H - y - M
paste(c, fit(P(7), pw, ph, fx=0.3, fy=0.6), (M, y))
paste(c, fit(P(10), pw, ph, fx=0.4), (M + pw + 40, y))
pill(d, M + 40, H - M - 170, "рисунок устойчив к стирке", PINK, 48)
save(c, 4, "принт")

# 5 На каждый день
c, d, y = header("НА КАЖДЫЙ", "ДЕНЬ", None)
pw = 940
paste(c, fit(P(11, (0.25, 0.08, 1, 1)), pw, H - y - M, fy=0.35), (W - M - pw, y))
yy = y + 20; x = M; w = W - 2 * M - pw - 50
for t in ["Дома", "В садике", "На прогулке под куртку и комбинезон", "На занятиях спортом"]:
    lines = wrap(d, t, f(600, 54), w - 110); hh = 70 + len(lines) * 68
    d.rounded_rectangle([x, yy, x + w, yy + hh], 40, fill=WHITE)
    d.ellipse([x + 40, yy + hh / 2 - 18, x + 76, yy + hh / 2 + 18], fill=PINK)
    for k, ln in enumerate(lines):
        d.text((x + 106, yy + 35 + k * 68), ln, font=f(600, 54), fill=INK)
    yy += hh + 34
d.text((x, yy + 40), "Размеры", font=f(500, 54), fill=GREY)
d.text((x, yy + 110), "80–98", font=f(600, 120), fill=PINK)
save(c, 5, "каждый_день")

# 6 Уход
c, d, y = header("ПРОСТОЙ", "УХОД", "Сохраняет форму и цвет после стирок")
pw = 760
paste(c, fit(P(3, (0, 0.3, 1, 1)), pw, H - y - M, fx=0.6, fy=0.5), (M, y))
x = M + pw + 60; w = W - M - x; yy = y + 20
for i, t in enumerate(["Бережная стирка при 30 °C", "Машинная или ручная стирка", "Сушить в расправленном виде",
                       "Рисунок не стирается"], 1):
    lines = wrap(d, t, f(600, 52), w - 150); hh = 70 + len(lines) * 66
    d.rounded_rectangle([x, yy, x + w, yy + hh], 40, fill=WHITE)
    d.ellipse([x + 30, yy + hh / 2 - 40, x + 110, yy + hh / 2 + 40], fill=PINK if i % 2 else BLUE)
    d.text((x + 70, yy + hh / 2), str(i), font=f(600, 48), fill=WHITE, anchor="mm")
    for k, ln in enumerate(lines):
        d.text((x + 140, yy + 35 + k * 66), ln, font=f(600, 52), fill=INK)
    yy += hh + 34
d.text((x, H - M - 230), "Сделано в России", font=f(600, 54), fill=INK)
d.text((x, H - M - 150), "Собственное производство", font=f(500, 48), fill=GREY)
d.text((x, H - M - 85), "в Иваново", font=f(500, 48), fill=GREY)
save(c, 6, "уход")
