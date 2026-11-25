from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
import os
D = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(D, "Syncopate.ttf")
S = 4  # scale vs. reference cover (554x751)
W, H = 554*S, 751*S
INK = (28, 28, 28)

def tracked(draw, text, size, y, x=None, width=None, track=0.0, center=False):
    f = ImageFont.truetype(FONT, size)
    ws = [draw.textlength(c, font=f) for c in text]
    if width is not None and len(text) > 1:
        gap = (width - sum(ws)) / (len(text) - 1)
    else:
        gap = track * size
    total = sum(ws) + gap*(len(text)-1)
    if center: x = (W - total)/2
    for c, w in zip(text, ws):
        draw.text((x, y), c, font=f, fill=INK, anchor="ls")
        x += w + gap

# --- flat cover
cover = Image.new("RGB", (W, H), (250, 250, 249))
d = ImageDraw.Draw(cover)
px0, py0, px1, py1 = 103*S, 135*S, 455*S, 620*S
pw, ph = px1-px0, py1-py0
photo = Image.open(os.path.join(D, "porsche.jpg")).convert("L")
photo = ImageOps.fit(photo, (pw, ph), Image.LANCZOS, centering=(0.5, 0.55))
photo = ImageEnhance.Contrast(photo).enhance(1.05).convert("RGB")
cover.paste(photo, (px0, py0))
tracked(d, "24H", 9*S, 83*S, x=103*S, track=0.15)
tracked(d, "PORSCHE", 30*S, 121*S, x=px0, width=pw)
tracked(d, "THERE IS NO SUBSTITUTE", 12*S, 668*S, track=0.18, center=True)
tracked(d, "KARL HAB", 10*S, 735*S, track=0.2, center=True)
cover.save(os.path.join(D, "cover_flat.png"))

# --- hardcover look: spine hinge + soft light gradient
book = cover.copy().convert("RGBA")
shade = Image.new("L", (W, H), 0)
sd = ImageDraw.Draw(shade)
for i in range(40*S):  # left spine gradient
    a = int(60 * (1 - i/(40*S))**2)
    sd.line([(i, 0), (i, H)], fill=a)
hx = 14*S  # hinge groove
for i in range(-3*S, 3*S):
    a = int(35 * (1 - abs(i)/(3*S)))
    sd.line([(hx+i, 0), (hx+i, H)], fill=max(a, shade.getpixel((hx+i, 0))))
dark = Image.new("RGBA", (W, H), (0, 0, 0, 255)); dark.putalpha(shade)
book = Image.alpha_composite(book, dark)
light = Image.new("L", (W, H), 0); ld = ImageDraw.Draw(light)
for x in range(0, W, 2):
    ld.line([(x, 0), (x+1, H)], fill=int(18 * (x/W)))
lightl = Image.new("RGBA", (W, H), (255, 255, 255, 255)); lightl.putalpha(light)
book = Image.alpha_composite(book, lightl)
# page edges on right/bottom
pages = Image.new("RGBA", (W+4*S, H+3*S), (0, 0, 0, 0))
pdraw = ImageDraw.Draw(pages)
pdraw.rectangle([4*S, 3*S, W+4*S-1, H+3*S-1], fill=(232, 230, 225, 255))
pages.paste(book, (0, 0))

# --- scene
M = 120*S
bg = Image.new("RGBA", (pages.width + 2*M, pages.height + 2*M), (236, 234, 230, 255))
sh = Image.new("L", bg.size, 0)
ImageDraw.Draw(sh).rectangle([M+8*S, M+14*S, M+pages.width+6*S, M+pages.height+10*S], fill=120)
sh = sh.filter(ImageFilter.GaussianBlur(18*S))
shadow = Image.new("RGBA", bg.size, (40, 35, 30, 255)); shadow.putalpha(sh)
bg = Image.alpha_composite(bg, shadow)
bg.alpha_composite(pages, (M, M))
bg.convert("RGB").save(os.path.join(D, "mockup_24h_porsche.png"))
bg.convert("RGB").resize((bg.width//2, bg.height//2), Image.LANCZOS).save(os.path.join(D, "mockup_24h_porsche.jpg"), quality=92)
