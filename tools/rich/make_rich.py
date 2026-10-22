import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT, FONT = sys.argv[1], sys.argv[2], sys.argv[3]
W = int(sys.argv[4]) if len(sys.argv) > 4 else 1440
H = int(sys.argv[5]) if len(sys.argv) > 5 else 1440
os.makedirs(OUT, exist_ok=True)

BG = (241, 243, 248)
INK = (40, 36, 110)
ACCENT = (242, 96, 60)
MUTED = (104, 106, 138)
WHITE = (255, 255, 255)
SOFT = (226, 230, 244)
M = 80  # поля

AGES = {62: "1–3 мес", 68: "3–6 мес", 74: "6–9 мес", 80: "9–12 мес", 86: "1–1,5 г", 92: "1,5–2 г",
        98: "2–3 г", 104: "3–4 г", 110: "4–5 л", 116: "5–6 л", 122: "6–7 л"}

MODELS = {
    "106FL3F": {
        "name": "С капюшоном и двумя молниями · 62–80 см",
        "tiles": [("106ФЛ3F/701735868_05", (0.5, 0.45), "Две молнии во всю длину", "легко переодеть даже спящего малыша"),
                  ("106ФЛ3F/701735868_12", (0.5, 0.35), "Капюшон и закрытая шея", "планка: молния не касается кожи"),
                  ("106ФЛ3F/701735868_09", (0.5, 0.5), "Регулируемый рукав", "манжет подворачивается на вырост"),
                  ("106ФЛ3F/701735868_11", (0.5, 0.45), "Свободный крой", "не сковывает движений")],
        "sizes": [62, 68, 74, 80],
        "rows": [("Длина изделия", [51, 53, 57, 66]), ("Длина по спинке", [36, 37, 38, 43]),
                 ("Ширина под проймой", [26, 27, 29, 33]), ("Длина рукава", [21, 23, 25, 28]),
                 ("Длина штанины", [15, 16, 19, 24])],
        "tip": "Сравните замеры с вещью, которая сейчас впору малышу",
    },
    "106FL3-2F": {
        "name": "С капюшоном для первых шагов · 80–92 см",
        "tiles": [("106ФЛ3(2)F/706700787_06", (0.5, 0.3), "Свободный крой", "удобно ползать и делать первые шаги"),
                  ("106ФЛ3(2)F/706700787_07", (0.5, 0.4), "Две молнии", "легко надевать и снимать"),
                  ("106ФЛ3(2)F/706700787_16", (0.5, 0.5), "Кнопки на горловине", "шея закрыта от ветра"),
                  ("106ФЛ3(2)F/706700787_09", (0.5, 0.5), "Регулируемый рукав", "манжет подворачивается на вырост")],
        "sizes": [80, 86, 92],
        "rows": [("Длина изделия", [65, 66, 72]), ("Длина по спинке", [41, 43, 46]),
                 ("Ширина под проймой", [30, 33, 35]), ("Длина рукава", [26, 28, 30]),
                 ("Длина штанины", [24, 24, 28])],
        "tip": "Сравните замеры с вещью, которая сейчас впору малышу",
    },
    "106FL4F": {
        "name": "Слип на молнии · 62–92 см",
        "tiles": [("106ФЛ4F/1894149691_05", (0.5, 0.3), "Длинная молния", "легко надевать и снимать"),
                  ("106ФЛ4F/1894149691_08", (0.5, 0.45), "Воротник-стойка", "не пускает холодный воздух"),
                  ("106ФЛ4F/1894149691_10", (0.5, 0.5), "Надёжная молния", "застёгивается плавно"),
                  ("106ФЛ4F/1894149691_06", (0.5, 0.5), "Ровные швы", "собственное производство")],
        "sizes": [62, 68, 74, 80, 86, 92],
        "rows": [("Длина по спинке", [32, 34, 36, 39, 40, 42]), ("Ширина под проймой", [23, 26, 29, 31, 33, 35]),
                 ("Длина рукава", [19, 21, 23, 25, 27, 29]), ("Длина штанины", [18, 20, 22, 23, 25, 27])],
        "tip": "Сравните замеры с вещью, которая сейчас впору малышу",
    },
    "106FL6F": {
        "name": "Однотонный со стойкой · 80–110 см",
        "tiles": [("106ФЛ6F/252710148_07", (0.5, 0.27), "Свободный крой", "не сковывает движений"),
                  ("106ФЛ6F/252710148_02", (0.5, 0.45), "Стойка и мягкая вставка", "молния не касается шеи"),
                  ("106ФЛ6F/252710148_06", (0.5, 0.5), "Мягкие манжеты", "держат тепло у запястий"),
                  ("106ФЛ6F/252710148_10", (0.5, 0.5), "Резинка на спинке", "комбинезон хорошо сидит")],
        "sizes": [80, 86, 92, 98, 104, 110],
        "rows": [],
        "tip": "Свободный крой: берите по росту, на размер больше брать не нужно",
    },
    "106FL7F": {
        "name": "Однотонный с вышивкой · 92–122 см",
        "tiles": [("106ФЛ7F/489377759_05", (0.5, 0.35), "Свободный крой", "для игр, прогулок и садика"),
                  ("106ФЛ7F/489377759_12", (0.5, 0.4), "Стойка, молния и вышивка", "защита подбородка"),
                  ("106ФЛ7F/489377759_14", (0.5, 0.5), "Мягкие манжеты", "держат тепло у запястий"),
                  ("106ФЛ7F/489377759_11", (0.5, 0.45), "Резинка на спинке", "комбинезон хорошо сидит")],
        "sizes": [92, 98, 104, 110, 116, 122],
        "rows": [("Длина изделия", [80, 85, 89, 94, 98, 106]), ("Ширина под проймой", [34, 35, 37, 39, 40, 41]),
                 ("Длина рукава", [33, 36, 38, 41, 44, 49]), ("Длина штанины", [33, 38, 42, 46, 48, 50])],
        "tip": "Свободный крой: берите по росту, на размер больше брать не нужно",
    },
}


def font(weight, size):
    f = ImageFont.truetype(FONT, size)
    f.set_variation_by_axes([weight])
    return f


def photo(path):
    return Image.open(os.path.join(SRC, path + ".jpg")).convert("RGB")


def cover(im, w, h, focus=(0.5, 0.5)):
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = min(max(round(im.width * focus[0] - w / 2), 0), im.width - w)
    y = min(max(round(im.height * focus[1] - h / 2), 0), im.height - h)
    return im.crop((x, y, x + w, y + h))


def paste_round(canvas, im, xy, r=36, shadow=True):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    if shadow:
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([xy[0], xy[1] + 10, xy[0] + im.width, xy[1] + im.height + 10], r,
                                             fill=(40, 36, 110, 38))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    canvas.paste(im, xy, mask)


def card(canvas, box, r=36, fill=WHITE):
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([box[0], box[1] + 8, box[2], box[3] + 8], r, fill=(40, 36, 110, 30))
    canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(canvas).rounded_rectangle(box, r, fill=fill)


def wrap(d, text, f, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def header(d, title, sub=None, y=M):
    size = 84
    while d.textlength(title, font=font(800, size)) > W - 2 * M:
        size -= 1
    d.text((M, y + (84 - size) * 0.8), title, font=font(800, size), fill=INK)
    d.rounded_rectangle([M, y + 112, M + 110, y + 122], 5, fill=ACCENT)
    if sub:
        d.text((M, y + 150), sub, font=font(500, 40), fill=MUTED)


def brand(d):
    f = font(700, 26)
    t = "T O T E M F O X"
    d.text((W - M - d.textlength(t, font=f), 34), t, font=f, fill=INK)


def new():
    c = Image.new("RGBA", (W, H), BG + (255,))
    return c, ImageDraw.Draw(c)


def save(c, name):
    c.convert("RGB").save(os.path.join(OUT, name), quality=92)
    print("saved", name)


def pill(d, xy, text, f, fill=ACCENT, color=WHITE, pad=(28, 14)):
    w = d.textlength(text, font=f)
    x, y = xy
    hgt = f.size + pad[1] * 2
    d.rounded_rectangle([x, y, x + w + pad[0] * 2, y + hgt], hgt // 2, fill=fill)
    d.text((x + pad[0], y + hgt / 2), text, font=f, fill=color, anchor="lm")
    return x + w + pad[0] * 2


# 1. Обложка
def block_cover():
    c, d = new()
    tf = font(800, 96)
    d.text((M, M), "Тёплая флисовая", font=tf, fill=INK)
    d.text((M, M + 110), "поддева", font=tf, fill=INK)
    d.text((M, M + 250), "от выписки до садика", font=font(500, 46), fill=MUTED)
    brand(d)
    # бейдж размеров
    bx, by, br = W - M - 150, M + 230, 150
    d.ellipse([bx - br, by - br, bx + br, by + br], fill=ACCENT)
    d.text((bx, by - 22), "62–122", font=font(800, 70), fill=WHITE, anchor="mm")
    d.text((bx, by + 46), "см", font=font(600, 40), fill=WHITE, anchor="mm")
    shots = [("106ФЛ3F/701735868_05", (0.5, 0.42), "62–80"),
             ("106ФЛ3(2)F/706700787_06", (0.5, 0.45), "80–92"),
             ("106ФЛ7F/489377759_05", (0.5, 0.45), "92–122")]
    gap, top = 30, 470
    cw = (W - 2 * M - 2 * gap) // 3
    ch = H - top - M
    for i, (p, fc, lab) in enumerate(shots):
        x = M + i * (cw + gap)
        paste_round(c, cover(photo(p), cw, ch, fc), (x, top))
        f = font(700, 40)
        tw = d.textlength(lab + " см", font=f)
        pill(d, (x + (cw - tw - 56) // 2, top + ch - 96), lab + " см", f, fill=WHITE, color=INK)
    save(c, "01_oblozhka.jpg")


# 2. Как носить
def block_wear():
    c, d = new()
    header(d, "Не будет ли холодно?", "Поддева — тёплый слой. Носите по погоде:")
    brand(d)
    rows = [("106ФЛ3F/701735868_08", (0.5, 0.4), "Дома и во сне", "как тёплый слип в прохладной квартире"),
            ("106ФЛ6F/252710148_07", (0.5, 0.35), "На прогулке", "весной, осенью и прохладным летом — самостоятельно"),
            (None, None, "Зимой — под верхний комбинезон", "")]
    top, gap = 330, 30
    rh = (H - top - M - 2 * gap) // 3
    for i, (p, fc, t, s) in enumerate(rows):
        y = top + i * (rh + gap)
        card(c, [M, y, W - M, y + rh])
        num_f = font(800, 44)
        if p:
            ph = rh - 40
            paste_round(c, cover(photo(p), 300, ph, fc), (M + 20, y + 20), r=28, shadow=False)
            tx = M + 360
            d.text((tx, y + 70), t, font=font(800, 54), fill=INK)
            for j, ln in enumerate(wrap(d, s, font(500, 38), W - M - tx - 40)):
                d.text((tx, y + 150 + j * 50), ln, font=font(500, 38), fill=MUTED)
        else:
            d.text((M + 40, y + 40), t, font=font(800, 54), fill=INK)
            layers = ["боди или термобельё", "флисовая поддева", "зимний комбинезон"]
            aw = 60
            bw = (W - 2 * M - 80 - 2 * aw) // 3
            bx, by, bh = M + 40, y + 130, 160
            for k, ln in enumerate(layers):
                x = bx + k * (bw + aw)
                fill, col = (ACCENT, WHITE) if k == 1 else (SOFT, INK)
                d.rounded_rectangle([x, by, x + bw, by + bh], 28, fill=fill)
                d.text((x + bw / 2, by + 40), f"{k + 1} слой", font=font(600, 28), fill=col, anchor="mm")
                lines = wrap(d, ln, font(800, 34), bw - 40)
                for j, t2 in enumerate(lines):
                    d.text((x + bw / 2, by + 92 + j * 42 - (len(lines) - 1) * 21), t2, font=font(800, 34), fill=col, anchor="mm")
                if k < 2:
                    d.text((x + bw + aw / 2, by + bh / 2), "→", font=font(700, 48), fill=INK, anchor="mm")
    save(c, "02_kak_nosit.jpg")


# 3. Детали по модели
def block_details(key, m):
    c, d = new()
    header(d, "Практичные решения для комфорта", m["name"])
    brand(d)
    top, gap = 330, 30
    tw = (W - 2 * M - gap) // 2
    th = (H - top - M - gap) // 2
    cap = 165
    for i, (p, fc, t, s) in enumerate(m["tiles"]):
        x = M + (i % 2) * (tw + gap)
        y = top + (i // 2) * (th + gap)
        card(c, [x, y, x + tw, y + th])
        im = cover(photo(p), tw - 24, th - cap - 12, fc)
        paste_round(c, im, (x + 12, y + 12), r=28, shadow=False)
        size = 40
        while d.textlength(t, font=font(800, size)) > tw - 64:
            size -= 1
        d.text((x + 32, y + th - cap + 20), t, font=font(800, size), fill=INK)
        for j, ln in enumerate(wrap(d, s, font(500, 30), tw - 64)[:2]):
            d.text((x + 32, y + th - cap + 76 + j * 38), ln, font=font(500, 30), fill=MUTED)
    save(c, f"03_detali_{key}.jpg")


# 4. Размер по модели
def block_size(key, m):
    c, d = new()
    header(d, "Как выбрать размер", "Размер = рост ребёнка в сантиметрах")
    brand(d)
    sizes, rows = m["sizes"], m["rows"]
    top = 330
    lab_w = 430
    col_w = (W - 2 * M - 60 - lab_w) / len(sizes)
    rh = 96
    table = [("Возраст*", [AGES[s] for s in sizes])] + [(n, [str(v) for v in vals]) for n, vals in rows]
    if not rows:
        table.append(("Рост ребёнка, см", [f"{s - 5}–{s}" for s in sizes]))
    head_h = 110
    box_h = head_h + len(table) * rh + 30
    card(c, [M, top, W - M, top + box_h])
    d.rounded_rectangle([M, top, W - M, top + head_h], 36, fill=INK)
    d.rectangle([M, top + head_h - 36, W - M, top + head_h], fill=INK)
    d.text((M + 36, top + head_h / 2), "Размер", font=font(700, 40), fill=WHITE, anchor="lm")
    for j, s in enumerate(sizes):
        cx = M + 30 + lab_w + col_w * (j + 0.5)
        d.text((cx, top + head_h / 2), str(s), font=font(800, 48), fill=WHITE, anchor="mm")
    for i, (name, vals) in enumerate(table):
        y = top + head_h + 15 + i * rh
        if i % 2 == 1:
            d.rounded_rectangle([M + 16, y, W - M - 16, y + rh], 20, fill=(246, 247, 252))
        d.text((M + 36, y + rh / 2), name, font=font(600, 36), fill=INK, anchor="lm")
        vf = font(600, 32) if i == 0 or not rows else font(700, 40)
        for j, v in enumerate(vals):
            cx = M + 30 + lab_w + col_w * (j + 0.5)
            d.text((cx, y + rh / 2), v, font=vf, fill=MUTED if i == 0 else INK, anchor="mm")
    y = top + box_h + 50
    tf = font(700, 40)
    lines = wrap(d, m["tip"], tf, W - 2 * M - 160)
    tip_h = 60 + len(lines) * 54
    d.rounded_rectangle([M, y, W - M, y + tip_h], 36, fill=ACCENT)
    d.text((M + 50, y + tip_h / 2), "!", font=font(800, 64), fill=WHITE, anchor="mm")
    for k, ln in enumerate(lines):
        d.text((M + 100, y + 30 + k * 54), ln, font=tf, fill=WHITE)
    if not rows:
        py = y + tip_h + 110
        paste_round(c, cover(photo(m["tiles"][0][0]), W - 2 * M, H - py - M, (0.5, 0.2)), (M, py))
    note = "* возраст ориентировочный; замеры в см по изделию, разложенному на ровной поверхности" if rows \
        else "* возраст ориентировочный"
    for k, ln in enumerate(wrap(d, note, font(500, 30), W - 2 * M)):
        d.text((M, y + tip_h + 36 + k * 40), ln, font=font(500, 30), fill=MUTED)
    save(c, f"04_razmer_{key}.jpg")


# 5. Материал
def block_material():
    c, d = new()
    pw = 640
    c.paste(cover(photo("106ФЛ6F/252710148_10"), pw, H, (0.5, 0.5)), (W - pw, 0))
    brand_f = font(700, 30)
    d.text((M, M), "Мягкий флис", font=font(800, 88), fill=INK)
    d.rounded_rectangle([M, M + 130, M + 110, M + 140], 5, fill=ACCENT)
    d.text((M, M + 175), "100% полиэстер · сделано в России", font=font(500, 36), fill=MUTED)
    items = ["Мягкий и приятный к коже", "Хорошо держит тепло", "Быстро сохнет",
             "Не садится и не теряет цвет после стирки"]
    y = M + 290
    f = font(600, 42)
    tw = W - pw - M - 140 - 40
    for t in items:
        d.ellipse([M, y + 2, M + 64, y + 66], fill=ACCENT)
        d.line([(M + 17, y + 35), (M + 28, y + 47), (M + 48, y + 22)], fill=WHITE, width=7, joint="curve")
        lines = wrap(d, t, f, tw)
        for k, ln in enumerate(lines):
            d.text((M + 96, y + 8 + k * 54), ln, font=f, fill=INK)
        y += max(1, len(lines)) * 54 + 62
    box = [M, H - M - 290, W - pw - 50, H - M]
    card(c, box)
    tf = font(700, 36)
    d.text((M + 40, box[1] + 36), "Совет по уходу", font=tf, fill=ACCENT)
    tip = "Стирайте при 30 °C с кондиционером — флис останется мягким и не будет электризоваться"
    for k, ln in enumerate(wrap(d, tip, font(500, 34), box[2] - box[0] - 80)):
        d.text((M + 40, box[1] + 100 + k * 46), ln, font=font(500, 34), fill=INK)
    save(c, "05_material.jpg")


# 6. Линейка
def block_line():
    c, d = new()
    header(d, "Растём вместе", "Флисовые комбинезоны TOTEMFOX от 62 до 122 см")
    brand(d)
    items = [("106ФЛ3F/701735868_05", (0.5, 0.45), "62–80", "С двумя молниями", "и капюшоном"),
             ("106ФЛ4F/1894149691_05", (0.5, 0.42), "62–92", "Слип на молнии", "с воротником-стойкой"),
             ("106ФЛ3(2)F/706700787_06", (0.5, 0.45), "80–92", "С капюшоном", "для первых шагов"),
             ("106ФЛ7F/489377759_05", (0.5, 0.45), "80–122", "Однотонный", "со стойкой")]
    top, gap = 330, 24
    cw = (W - 2 * M - 3 * gap) // 4
    ph = 760
    for i, (p, fc, sz, t1, t2) in enumerate(items):
        x = M + i * (cw + gap)
        card(c, [x, top, x + cw, top + ph + 150])
        paste_round(c, cover(photo(p), cw - 20, ph, fc), (x + 10, top + 10), r=28, shadow=False)
        f = font(800, 38)
        szw = d.textlength(sz + " см", font=f)
        pill(d, (x + (cw - szw - 48) / 2, top + ph - 60), sz + " см", f, pad=(24, 12))
        size = 32
        while d.textlength(t1, font=font(800, size)) > cw - 30:
            size -= 1
        d.text((x + cw / 2, top + ph + 62), t1, font=font(800, size), fill=INK, anchor="mm")
        size = 28
        while d.textlength(t2, font=font(500, size)) > cw - 30:
            size -= 1
        d.text((x + cw / 2, top + ph + 108), t2, font=font(500, size), fill=MUTED, anchor="mm")
    y = top + ph + 210
    d.rounded_rectangle([M, y, W - M, y + 14], 7, fill=SOFT)
    d.rounded_rectangle([M, y, W - M - 40, y + 14], 7, fill=ACCENT)
    d.polygon([(W - M - 50, y - 18), (W - M, y + 7), (W - M - 50, y + 32)], fill=ACCENT)
    d.text((M, y + 40), "с рождения", font=font(600, 32), fill=MUTED)
    t = "до 7 лет"
    d.text((W - M - d.textlength(t, font=font(600, 32)), y + 40), t, font=font(600, 32), fill=MUTED)
    save(c, "06_lineyka.jpg")


block_cover()
block_wear()
for k, m in MODELS.items():
    block_details(k, m)
    block_size(k, m)
block_material()
block_line()
