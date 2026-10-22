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
# --- конец темы ---
