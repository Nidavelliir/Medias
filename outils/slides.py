"""Générateur de slides 1080x1350. Usage : python3 slides.py spec.json "Nom" "@compte"."""
from PIL import Image, ImageDraw, ImageFont
import random, sys, json, os

F = "/usr/share/fonts/truetype/google-fonts/"
NAVY = (27, 36, 64)
NAVY2 = (39, 52, 90)
YEL = (255, 201, 60)
CORAL = (255, 107, 91)
WHITE = (255, 255, 255)
SOFT = (200, 210, 235)
S = 2
BRAND = sys.argv[2] if len(sys.argv) > 2 else ""
HANDLE = sys.argv[3] if len(sys.argv) > 3 else ""
W, H = 1080, 1350
TAGS = {"insolite": ("INSOLITE", CORAL), "histoire": ("HISTOIRE VRAIE", YEL),
        "origine": ("ORIGINE DU QUOTIDIEN", (110, 200, 170)), "bonus": ("BONUS", SOFT)}


def ft(name, size):
    return ImageFont.truetype(F + name, size * S)


def wrap(d, text, f, maxw):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for w in para.split(" "):
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= maxw * S:
                cur = t
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def base(seed):
    img = Image.new("RGB", (W * S, H * S), NAVY)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(40):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        if (60 < x < 1020 and 180 < y < 1180) or (150 < x < 930 and 1220 < y < 1290):
            continue
        r = rnd.choice([3, 4, 6])
        c = rnd.choice([YEL, CORAL, (90, 110, 170)])
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=c)
    # en-tête logo
    bx, by = 80, 80
    d.rounded_rectangle([bx * S, by * S, (bx + 70) * S, (by + 52) * S], radius=20 * S, fill=YEL)
    d.polygon([((bx + 14) * S, (by + 48) * S), ((bx + 30) * S, (by + 48) * S), ((bx + 8) * S, (by + 66) * S)], fill=YEL)
    d.text(((bx + 35) * S, (by + 26) * S), "?!", font=ft("Poppins-Bold.ttf", 30), fill=NAVY, anchor="mm")
    d.text(((bx + 90) * S, (by + 26) * S), BRAND, font=ft("Poppins-Bold.ttf", 30), fill=WHITE, anchor="lm")
    return img, d


def tag(d, kind, y):
    label, col = TAGS[kind]
    f = ft("Poppins-Bold.ttf", 26)
    tw = d.textlength(label, font=f) / S
    d.rounded_rectangle([80 * S, y * S, (80 + tw + 48) * S, (y + 54) * S], radius=27 * S, fill=col)
    d.text(((80 + 24) * S, (y + 27) * S), label, font=f, fill=NAVY, anchor="lm")


def footer(d, text):
    d.text((540 * S, 1255 * S), text, font=ft("Poppins-Medium.ttf", 28), fill=SOFT, anchor="mm")


def cover(kind, title, highlight, out, seed=1):
    """Slide d'accroche : titre en blanc + phrase finale surlignée en jaune."""
    img, d = base(seed)
    f = ft("Poppins-Bold.ttf", 78)
    n = len(wrap(d, title, f, 920)) + len(wrap(d, highlight, f, 920))
    y0 = int(200 + (1180 - 200 - (100 + n * 98 + 10)) / 2)
    tag(d, kind, y0)
    y = y0 + 100
    for ln in wrap(d, title, f, 920):
        d.text((80 * S, y * S), ln, font=f, fill=WHITE)
        y += 98
    y += 10
    for ln in wrap(d, highlight, f, 920):
        d.text((80 * S, y * S), ln, font=f, fill=YEL)
        y += 98
    footer(d, "Fais défiler  »")
    img.resize((W, H), Image.LANCZOS).save(out)


def text_slide(kind, heading, body, out, closing=None, seed=2):
    img, d = base(seed)
    fh = ft("Poppins-Bold.ttf", 60); fb = ft("Poppins-Regular.ttf", 40); fc = ft("Poppins-Bold.ttf", 46)
    hl = wrap(d, heading, fh, 920); bl = wrap(d, body, fb, 920); cl = wrap(d, closing, fc, 920) if closing else []
    total = 54 + 46 + len(hl) * 78 + 30 + len(bl) * 58 + (30 + len(cl) * 62 if cl else 0)
    y = max(220, int(200 + (1180 - 200 - total) / 2))
    tag(d, kind, y); y += 100
    for ln in hl:
        d.text((80 * S, y * S), ln, font=fh, fill=YEL); y += 78
    y += 30
    for ln in bl:
        if ln:
            d.text((80 * S, y * S), ln, font=fb, fill=WHITE)
        y += 58
    if cl:
        y += 30
        for ln in cl:
            d.text((80 * S, y * S), ln, font=fc, fill=CORAL); y += 62
    footer(d, f"Suis {HANDLE} pour plus d'étonnement")
    img.resize((W, H), Image.LANCZOS).save(out)


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    for s in spec:
        if s["type"] == "cover":
            cover(s["kind"], s["title"], s["highlight"], s[os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), s["out"]))
        else:
            text_slide(s["kind"], s["heading"], s["body"], os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), s["out"]), s.get("closing"))
    print("ok")
