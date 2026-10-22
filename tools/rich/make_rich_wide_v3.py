"""Рич-контент 800×500: рисуем в 1600×1000 и уменьшаем в 2 раза.
Общие константы, MODELS и хелперы берём из make_rich.py (до блоков)."""
import os
import sys

from PIL import Image

here = os.path.dirname(os.path.abspath(__file__))
src_code = open(os.path.join(here, "make_rich.py"), encoding="utf-8").read()
prefix = src_code[:src_code.index("# 1. Обложка")]
SRC_, OUT_, FONT_ = sys.argv[1], sys.argv[2], sys.argv[3]
FMT = sys.argv[4] if len(sys.argv) > 4 else "jpg"
sys.argv = [sys.argv[0], SRC_, OUT_, FONT_, "1600", "1000"]
exec(prefix)

M = 64
OW, OH = 800, 500


def save(c, name):
    im = c.convert("RGB").resize((OW, OH), Image.LANCZOS)
    name = name.rsplit(".", 1)[0] + "." + FMT
    if FMT == "png":
        im.save(os.path.join(OUT, name), optimize=True)
    else:
        im.save(os.path.join(OUT, name), quality=93, subsampling=0)
    print("saved", name)


def fit(d, text, weight, size, width):
    while d.textlength(text, font=font(weight, size)) > width:
        size -= 1
    return font(weight, size)


def header(d, title, sub=None):
    f = fit(d, title, 800, 80, W - 2 * M - 260)
    d.text((M, 52 + (80 - f.size) * 0.8), title, font=f, fill=INK)
    d.rounded_rectangle([M, 152, M + 96, 161], 5, fill=ACCENT)
    if sub:
        d.text((M, 182), sub, font=font(500, 36), fill=MUTED)


def brand(d):
    f = font(700, 26)
    t = "T O T E M F O X"
    d.text((W - M - d.textlength(t, font=f), 62), t, font=f, fill=INK)


# --- тема бренда v3 (молочный фон, Montserrat 600, пудрово-розовый / серо-голубой) ---
BG = (250, 248, 244); INK = (92, 84, 78); ACCENT = (204, 138, 148); MUTED = (160, 150, 140)
SOFT = (232, 238, 242); BLUE2 = (139, 168, 186); LINE2 = (228, 221, 212); WHITE = (255, 255, 255)
_font0 = font
def font(weight, size):
    return _font0(min(weight, 650), size)
def new():
    c = Image.new("RGBA", (W, H), BG + (255,))
    return c, ImageDraw.Draw(c)
def card(canvas, box, r=26, fill=WHITE):
    ImageDraw.Draw(canvas).rounded_rectangle(box, r, fill=fill)
_paste0 = paste_round
def paste_round(canvas, im, xy, r=28, shadow=False):
    return _paste0(canvas, im, xy, r=r, shadow=False)
def header(d, title, sub=None):
    t = title.upper()
    words = t.split()
    f = fit(d, t, 600, 66, W - 2 * M)
    x = M; y = 78
    for i, w in enumerate(words):
        col = ACCENT if (i == len(words) - 1 and len(words) > 1) else INK
        d.text((x, y), w, font=f, fill=col); x += d.textlength(w + " ", font=f)
    if sub:
        d.text((M, 172), sub, font=font(500, 34), fill=MUTED)
def brand(d):
    pass
LABELS = {"01": "Основная информация", "02": "Как носить", "03": "Практичные решения", "04": "Размер",
          "05": "Материал", "06": "Растём вместе"}
_save0 = save
def save(c, name):
    import re as _re
    m = _re.search(r"(?:^|_)(\d{1,2})_", name)
    num = m.group(1).zfill(2) if m else ""
    lab = LABELS.get(num, LABEL_OVERRIDE.get(num, "")) if not LABEL_OVERRIDE else LABEL_OVERRIDE.get(num, "")
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, W, 64], fill=BG)
    f = font(400, 26)
    d.text((M, 30), lab, font=f, fill=MUTED)
    tw = d.textlength(lab, font=f)
    d.text((W - M, 30), num, font=f, fill=MUTED, anchor="ra")
    d.line([(M + tw + 24, 46), (W - M - 60, 46)], fill=LINE2, width=2)
    _save0(c, name)
LABEL_OVERRIDE = {}
_pill0 = pill
def pill(d, xy, text, f, fill=None, color=WHITE, pad=(28, 14)):
    return _pill0(d, xy, text, f, fill=ACCENT if fill is None else fill, color=color, pad=pad)
# --- конец темы ---

TOP = 262  # верх контентной зоны
BOT = H - M


def block_cover():
    c, d = new()
    tf = font(800, 92)
    tf = font(600, 84)
    d.text((M, 160), "ТЁПЛАЯ", font=tf, fill=INK)
    d.text((M, 262), "ФЛИСОВАЯ", font=tf, fill=INK)
    d.text((M, 364), "ПОДДЕВА", font=tf, fill=ACCENT)
    d.text((M, 540), "от выписки до садика", font=font(500, 40), fill=MUTED)
    pill(d, (M, 640), "62–122 см", font(800, 54), pad=(40, 22))
    f = font(700, 26)
    d.text((M, BOT - 30), "T O T E M F O X", font=f, fill=INK)
    shots = [("106ФЛ3F/701735868_05", (0.5, 0.42), "62–80"),
             ("106ФЛ4F/1261337599_06", (0.5, 0.42), "62–92"),
             ("106ФЛ7F/489377759_05", (0.5, 0.45), "92–122")]
    x0, gap = 720, 24
    cw = (W - M - x0 - 2 * gap) // 3
    ch = H - 2 * M
    for i, (p, fc, lab) in enumerate(shots):
        x = x0 + i * (cw + gap)
        paste_round(c, cover(photo(p), cw, ch, fc), (x, M))
        lf = font(700, 34)
        tw = d.textlength(lab + " см", font=lf)
        pill(d, (x + (cw - tw - 48) // 2, M + ch - 84), lab + " см", lf, fill=WHITE, color=INK, pad=(24, 12))
    save(c, "01_oblozhka.jpg")


def block_wear():
    c, d = new()
    header(d, "Не будет ли холодно?", "Поддева — тёплый слой. Носите по погоде:")
    brand(d)
    gap = 28
    cw = (W - 2 * M - 2 * gap) // 3
    chh = BOT - TOP
    items = [("106ФЛ3F/701735868_08", (0.5, 0.35), "Дома и во сне", "как тёплый слип в прохладной квартире"),
             ("106ФЛ6F/252710148_07", (0.5, 0.25), "На прогулке", "весной, осенью и прохладным летом"),
             (None, None, "Зимой — под верхний комбинезон", "")]
    ph = 400
    for i, (p, fc, t, s) in enumerate(items):
        x = M + i * (cw + gap)
        card(c, [x, TOP, x + cw, TOP + chh])
        if p:
            paste_round(c, cover(photo(p), cw - 24, ph, fc), (x + 12, TOP + 12), r=28, shadow=False)
            d.text((x + 32, TOP + ph + 44), t, font=fit(d, t, 800, 42, cw - 64), fill=INK)
            for j, ln in enumerate(wrap(d, s, font(500, 32), cw - 64)[:3]):
                d.text((x + 32, TOP + ph + 112 + j * 42), ln, font=font(500, 32), fill=MUTED)
        else:
            tl = wrap(d, t, font(800, 42), cw - 64)
            for j, ln in enumerate(tl):
                d.text((x + 32, TOP + 36 + j * 52), ln, font=font(800, 42), fill=INK)
            layers = ["боди или термобельё", "флисовая поддева", "зимний комбинезон"]
            by = TOP + 60 + len(tl) * 52
            bh, ag = 112, 46
            for k, ln in enumerate(layers):
                y = by + k * (bh + ag)
                fill, col = (ACCENT, WHITE) if k == 1 else (SOFT, INK)
                d.rounded_rectangle([x + 32, y, x + cw - 32, y + bh], 26, fill=fill)
                d.text((x + 60, y + 32), f"{k + 1} слой", font=font(600, 26), fill=col, anchor="lm")
                d.text((x + 60, y + 76), ln, font=fit(d, ln, 800, 34, cw - 120), fill=col, anchor="lm")
                if k < 2:
                    d.text((x + cw / 2, y + bh + ag / 2), "↓", font=font(700, 40), fill=INK, anchor="mm")
    save(c, "02_kak_nosit.jpg")


def block_details(key, m):
    c, d = new()
    header(d, "Практичные решения для комфорта", m["name"])
    brand(d)
    gap = 24
    tw = (W - 2 * M - 3 * gap) // 4
    th = BOT - TOP
    ph = 400
    for i, (p, fc, t, s) in enumerate(m["tiles"]):
        x = M + i * (tw + gap)
        card(c, [x, TOP, x + tw, TOP + th])
        paste_round(c, cover(photo(p), tw - 20, ph, fc), (x + 10, TOP + 10), r=26, shadow=False)
        tl = wrap(d, t, font(800, 34), tw - 48)
        y = TOP + ph + 36
        for j, ln in enumerate(tl[:2]):
            d.text((x + 24, y + j * 42), ln, font=font(800, 34), fill=INK)
        y += len(tl[:2]) * 42 + 12
        sl = wrap(d, s, font(500, 28), tw - 48)
        if len(tl) > 2 or len(sl) > 3:
            print("WARN overflow", key, t)
        for j, ln in enumerate(sl[:3]):
            d.text((x + 24, y + j * 36), ln, font=font(500, 28), fill=MUTED)
    save(c, f"03_detali_{key}.jpg")


def block_size(key, m):
    c, d = new()
    header(d, "Как выбрать размер", "Размер = рост ребёнка в сантиметрах")
    brand(d)
    sizes, rows = m["sizes"], m["rows"]
    table = [("Возраст*", [AGES[s] for s in sizes])] + [(n, [str(v) for v in vals]) for n, vals in rows]
    if not rows:
        table.append(("Рост ребёнка, см", [f"{s - 5}–{s}" for s in sizes]))
    lab_w = 400 if rows else 330
    tw_ = W - 2 * M if rows else 1110
    col_w = (tw_ - 50 - lab_w) / len(sizes)
    head_h, rh = 84, 70
    top = TOP - 20
    box_h = head_h + len(table) * rh + 20
    card(c, [M, top, M + tw_, top + box_h], r=30)
    d.rounded_rectangle([M, top, M + tw_, top + head_h], 30, fill=BLUE2)
    d.rectangle([M, top + head_h - 30, M + tw_, top + head_h], fill=BLUE2)
    d.text((M + 30, top + head_h / 2), "Размер", font=font(700, 36), fill=WHITE, anchor="lm")
    for j, s in enumerate(sizes):
        d.text((M + 25 + lab_w + col_w * (j + 0.5), top + head_h / 2), str(s), font=font(800, 42), fill=WHITE,
               anchor="mm")
    for i, (name, vals) in enumerate(table):
        y = top + head_h + 10 + i * rh
        if i % 2 == 1:
            d.rounded_rectangle([M + 12, y, M + tw_ - 12, y + rh], 18, fill=(246, 247, 252))
        d.text((M + 30, y + rh / 2), name, font=font(600, 32), fill=INK, anchor="lm")
        vf = font(600, 27) if i == 0 else (font(700, 36) if rows else font(700, 28))
        for j, v in enumerate(vals):
            d.text((M + 25 + lab_w + col_w * (j + 0.5), y + rh / 2), v, font=vf, fill=MUTED if i == 0 else INK,
                   anchor="mm")
    if rows:
        y = top + box_h + 30
        tip_box = [M, y, W - M, y + 92]
    else:
        y = top + box_h + 30
        tip_box = [M, y, M + tw_, y + 150]
        px = M + tw_ + 32
        paste_round(c, cover(photo(m["tiles"][0][0]), W - M - px, BOT - top, (0.5, 0.3)), (px, top))
    d.rounded_rectangle(tip_box, 30, fill=ACCENT)
    d.text((tip_box[0] + 44, (tip_box[1] + tip_box[3]) / 2), "!", font=font(800, 56), fill=WHITE, anchor="mm")
    tf = font(700, 34)
    lines = wrap(d, m["tip"], tf, tip_box[2] - tip_box[0] - 120)
    lh = 44
    ty = (tip_box[1] + tip_box[3]) / 2 - len(lines) * lh / 2
    for k, ln in enumerate(lines):
        d.text((tip_box[0] + 88, ty + k * lh), ln, font=tf, fill=WHITE)
    note = "* возраст ориентировочный; замеры в см по изделию, разложенному на ровной поверхности" if rows \
        else "* возраст ориентировочный"
    d.text((M, tip_box[3] + 22), note, font=font(500, 26), fill=MUTED)
    save(c, f"04_razmer_{key}.jpg")


def block_material():
    c, d = new()
    pw = 660
    paste_round(c, cover(photo("106ФЛ6F/252710148_10"), pw, H - 96 - M, (0.5, 0.5)), (W - M - pw, 96))
    d.text((M, 78), "МЯГКИЙ", font=font(600, 66), fill=INK)
    d.text((M + d.textlength("МЯГКИЙ ", font=font(600, 66)), 78), "ФЛИС", font=font(600, 66), fill=ACCENT)
    d.text((M, 172), "100% полиэстер · сделано в России", font=font(500, 34), fill=MUTED)
    items = ["Мягкий и приятный к коже", "Хорошо держит тепло", "Быстро сохнет", "Не садится и не линяет после стирки"]
    y = 250
    f = font(600, 36)
    for t in items:
        d.ellipse([M, y, M + 54, y + 54], fill=ACCENT)
        d.line([(M + 14, y + 29), (M + 24, y + 39), (M + 41, y + 18)], fill=WHITE, width=6, joint="curve")
        d.text((M + 78, y + 27), t, font=fit(d, t, 600, 36, W - pw - 2 * M - 78 - 40), fill=INK, anchor="lm")
        y += 74
    care = ["Стирка при температуре не выше 40 °C", "Отбеливание запрещено",
            "Сушка в сушильной машине запрещена", "Стирка с бирками запрещена"]
    tl = [ln for t in care for ln in wrap(d, "•  " + t, font(500, 30), W - pw - M - 40 - M - 72)]
    bh = 84 + len(tl) * 40 + 34
    box = [M, BOT - bh, W - pw - M - 40, BOT]
    card(c, box, r=30)
    d.text((M + 36, box[1] + 30), "Совет по уходу", font=font(700, 32), fill=ACCENT)
    for k, ln in enumerate(tl):
        d.text((M + 36, box[1] + 84 + k * 40), ln, font=font(500, 30), fill=INK)
    save(c, "05_material.jpg")


def block_line():
    c, d = new()
    header(d, "Растём вместе", "Флисовые комбинезоны TOTEMFOX от 62 до 122 см")
    brand(d)
    items = [("106ФЛ3F/701735868_05", (0.5, 0.45), "62–80", "С двумя молниями", "и капюшоном"),
             ("106ФЛ4F/1261337599_06", (0.5, 0.4), "62–92", "Слип на молнии", "с воротником-стойкой"),
             ("106ФЛ7F/489377759_05", (0.5, 0.4), "80–122", "Однотонный", "со стойкой")]
    gap = 24
    gap = 40
    cw = (W - 2 * M - (len(items) - 1) * gap) // len(items)
    ph = 470
    chh = ph + 130
    for i, (p, fc, sz, t1, t2) in enumerate(items):
        x = M + i * (cw + gap)
        card(c, [x, TOP, x + cw, TOP + chh], r=30)
        paste_round(c, cover(photo(p), cw - 20, ph, fc), (x + 10, TOP + 10), r=26, shadow=False)
        f = font(800, 34)
        szw = d.textlength(sz + " см", font=f)
        pill(d, (x + (cw - szw - 44) / 2, TOP + ph - 58), sz + " см", f, pad=(22, 10))
        d.text((x + cw / 2, TOP + ph + 50), t1, font=fit(d, t1, 800, 32, cw - 30), fill=INK, anchor="mm")
        d.text((x + cw / 2, TOP + ph + 94), t2, font=fit(d, t2, 500, 28, cw - 30), fill=MUTED, anchor="mm")
    y = TOP + chh + 34
    d.rounded_rectangle([M, y, W - M - 40, y + 12], 6, fill=ACCENT)
    d.polygon([(W - M - 46, y - 16), (W - M, y + 6), (W - M - 46, y + 28)], fill=ACCENT)
    lf = font(600, 30)
    d.text((M, y + 30), "с рождения", font=lf, fill=MUTED)
    d.text((W - M - d.textlength("до 7 лет", font=lf), y + 30), "до 7 лет", font=lf, fill=MUTED)
    save(c, "06_lineyka.jpg")


block_cover()
block_wear()
for k, m in MODELS.items():
    block_details(k, m)
    block_size(k, m)
block_material()
block_line()
