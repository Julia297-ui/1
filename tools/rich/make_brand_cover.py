import sys, os
from PIL import Image, ImageDraw, ImageFont
BODY, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
W, H = 1600, 1000          # рисуем ×2, сохраняем 800×500
import json
PAL = json.loads(os.environ.get("PAL", "null")) or {"крем": [[252,243,234],[140,126,108],[232,219,203]]}
def f(w, s):
    x = ImageFont.truetype(BODY, s); x.set_variation_by_axes([w]); return x
def onesie(d, x, y, s, w=8):
    p = [(x, y), (x + .3*s, y - .12*s), (x + .4*s, y), (x + .6*s, y), (x + .7*s, y - .12*s), (x + s, y),
         (x + 1.08*s, y + .28*s), (x + .86*s, y + .36*s), (x + .82*s, y + .9*s), (x + .62*s, y + 1.05*s),
         (x + .5*s, y + .95*s), (x + .38*s, y + 1.05*s), (x + .18*s, y + .9*s), (x + .14*s, y + .36*s), (x - .08*s, y + .28*s), (x, y)]
    d.line(p, fill=LN, width=w, joint="curve")
    d.arc([x + .38*s, y - .08*s, x + .62*s, y + .12*s], 0, 180, fill=LN, width=w)
def sock(d, x, y, s, w=8):
    p = [(x, y), (x + .4*s, y), (x + .4*s, y + .6*s), (x + .75*s, y + .78*s), (x + .72*s, y + 1.0*s), (x + .1*s, y + .95*s), (x, y + .75*s), (x, y)]
    d.line(p, fill=LN, width=w, joint="curve"); d.line([(x, y + .15*s), (x + .4*s, y + .15*s)], fill=LN, width=w)
def star(d, cx, cy, r, w=7):
    import math
    pts = [(cx + (r if i % 2 == 0 else r * .45) * math.cos(math.radians(-90 + i * 36)),
            cy + (r if i % 2 == 0 else r * .45) * math.sin(math.radians(-90 + i * 36))) for i in range(11)]
    d.line(pts, fill=LN, width=w, joint="curve")
def heart(d, cx, cy, s, w=7):
    d.arc([cx - s, cy - s*.6, cx, cy + s*.4], 150, 360, fill=LN, width=w)
    d.arc([cx, cy - s*.6, cx + s, cy + s*.4], 180, 30, fill=LN, width=w)
    d.line([(cx - s*.93, cy + .05*s), (cx, cy + s), (cx + s*.93, cy + .05*s)], fill=LN, width=w, joint="curve")
def render(tag, name):
    c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
    onesie(d, 70, 730, 210, 7); sock(d, 1380, 90, 170, 7); star(d, 360, 150, 46, 6); star(d, 1230, 830, 40, 6)
    heart(d, 1470, 560, 50, 6); heart(d, 180, 140, 40, 6); star(d, 1160, 130, 28, 5); sock(d, 1380, 770, 90, 6)
    star(d, 520, 880, 26, 5); heart(d, 1000, 900, 30, 5)
    s = 230
    while d.textlength("TOTEMFOX", font=f(500, s)) > 1180: s -= 4
    d.text((W / 2, 420), "TOTEMFOX", font=f(500, s), fill=TXT, anchor="mm")
    s2 = 76
    while d.textlength(tag, font=f(400, s2)) > 1100: s2 -= 2
    d.text((W / 2, 600), tag, font=f(400, s2), fill=TXT, anchor="mm")
    c.resize((800, 500), Image.LANCZOS).save(os.path.join(OUT, name), quality=95, subsampling=0)
    print("saved", name)
TAG = os.environ.get("TAG", "забота в каждой детали")
for nm, (bg, tx, ln) in PAL.items():
    BG, TXT, LN = tuple(bg), tuple(tx), tuple(ln)
    render(TAG, f"обложка_{nm}.jpg")
