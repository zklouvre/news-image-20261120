#!/usr/bin/env python3
"""Draw 'The Daily Globe' front page summing up Friday 20 November 2026.

Facts come ONLY from ~/workspace/makefun-study/news-image-20261120-facts.md.
Output: entry.png, exactly 1024x1024, PNG, <= 1 MiB.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 24                      # side margin
CW = W - 2 * M              # content width = 976

PAPER = (247, 243, 234)     # newsprint cream
WHITE = (255, 255, 255)
INK = (26, 26, 26)
GRAY = (90, 86, 78)
RED = (185, 28, 28)
RED_TINT = (252, 235, 235)
BORDER = (198, 192, 180)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_h(d, lines, fnt, lh):
    return len(lines) * lh


# ---------------------------------------------------------------- icons
def icon_chart(d, x, y, s=64):
    """Falling bars + down arrow, red."""
    bw = s // 5
    heights = [int(s * 0.85), int(s * 0.62), int(s * 0.45), int(s * 0.28)]
    for i, h in enumerate(heights):
        bx = x + i * (bw + 4)
        d.rectangle([bx, y + s - h, bx + bw, y + s], fill=RED)
    # down arrow on the right
    ax = x + s + 6
    d.line([ax, y + 6, ax, y + s - 14], fill=RED, width=5)
    d.polygon([(ax - 9, y + s - 20), (ax + 9, y + s - 20), (ax, y + s - 2)],
              fill=RED)


def icon_leaf(d, x, y, s=44):
    """Green leaf."""
    d.ellipse([x, y, x + s, y + s], fill=(21, 128, 61))
    d.polygon([(x + s * 0.28, y + s * 0.72), (x + s * 0.30, y + s * 0.30),
               (x + s * 0.62, y + s * 0.22), (x + s * 0.74, y + s * 0.55),
               (x + s * 0.55, y + s * 0.78)], fill=(247, 243, 234))
    d.line([x + s * 0.30, y + s * 0.70, x + s * 0.68, y + s * 0.30],
           fill=(21, 128, 61), width=2)


def icon_eu(d, x, y, s=44):
    """Blue circle with yellow stars."""
    d.ellipse([x, y, x + s, y + s], fill=(29, 78, 216))
    import math
    cx, cy, r = x + s / 2, y + s / 2, s * 0.30
    for i in range(6):
        a = math.pi * 2 * i / 6 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([sx - 2.5, sy - 2.5, sx + 2.5, sy + 2.5], fill=(250, 204, 21))


def icon_drone(d, x, y, s=44):
    """Simple quadcopter, slate gray."""
    c = (71, 85, 105)
    cx, cy = x + s / 2, y + s / 2
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        px, py = cx + dx * s * 0.32, cy + dy * s * 0.32
        d.line([cx, cy, px, py], fill=c, width=3)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], outline=c, width=3)
    d.rounded_rectangle([cx - 11, cy - 8, cx + 11, cy + 8], radius=4, fill=c)


def icon_baseball(d, x, y, s=44):
    """White baseball with red stitches."""
    d.ellipse([x, y, x + s, y + s], fill=(255, 255, 255),
              outline=(185, 28, 28), width=2)
    # two short curved seams bulging toward the left and right edges
    d.arc([x + s * 0.05, y + s * 0.22, x + s * 0.55, y + s * 0.78],
          start=90, end=270, fill=(185, 28, 28), width=2)
    d.arc([x + s * 0.45, y + s * 0.22, x + s * 0.95, y + s * 0.78],
          start=270, end=90, fill=(185, 28, 28), width=2)


def icon_ballot(d, x, y, s=44):
    """Ballot box with a check mark."""
    d.rectangle([x + 4, y + s * 0.42, x + s - 4, y + s - 4],
                fill=(126, 34, 206))
    d.rectangle([x + 2, y + s * 0.30, x + s - 2, y + s * 0.46],
                fill=(88, 28, 135))
    d.rectangle([x + s * 0.32, y + s * 0.36, x + s * 0.68, y + s * 0.40],
                fill=(247, 243, 234))
    d.line([x + s * 0.30, y + s * 0.22, x + s * 0.46, y + s * 0.02,
            x + s * 0.78, y + s * 0.34], fill=(21, 128, 61), width=4)


ICONS = {"chart": icon_chart, "leaf": icon_leaf, "eu": icon_eu,
         "drone": icon_drone, "baseball": icon_baseball, "ballot": icon_ballot}

# ---------------------------------------------------------------- panels
def draw_panel(d, x, y, w, h, kicker, kcolor, headline, summary, icon=None):
    d.rectangle([x, y, x + w, y + h], fill=WHITE, outline=BORDER, width=1)
    pad = 14
    ix = x + w - pad - 46
    iy = y + pad
    if icon:
        ICONS[icon](d, ix, iy, 46)
    tx = x + pad
    tw = w - 2 * pad - (52 if icon else 0)
    # kicker
    kf = font(SANS_B, 14)
    d.text((tx, y + pad), kicker, font=kf, fill=kcolor)
    # headline, up to 2 lines (auto-shrink font so nothing is clipped)
    lines, hf = [], None
    for size in (22, 20, 19):
        hf = font(SANS_B, size)
        lines = wrap(d, headline, hf, tw)
        if len(lines) <= 2:
            break
    lh = 27 if hf.size >= 22 else 25
    hy = y + pad + 20
    for ln in lines[:2]:
        d.text((tx, hy), ln, font=hf, fill=INK)
        hy += lh
    # summary, up to 3 lines
    sf = font(SANS, 15)
    slines = wrap(d, summary, sf, w - 2 * pad)
    sy = hy + 6
    for ln in slines[:3]:
        d.text((tx, sy), ln, font=sf, fill=(51, 51, 51))
        sy += 19


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    mf = font(SERIF_B, 62)
    title = "THE DAILY GLOBE"
    tw = d.textlength(title, font=mf)
    d.text(((W - tw) / 2, 14), title, font=mf, fill=INK)
    df = font(SANS_B, 32)
    date = "FRIDAY, 20 NOVEMBER 2026"
    dw = d.textlength(date, font=df)
    d.text(((W - dw) / 2, 88), date, font=df, fill=RED)
    d.line([M, 132, W - M, 132], fill=INK, width=3)
    d.line([M, 138, W - M, 138], fill=INK, width=1)

    # ---- lead panel: AI rout -------------------------------------------
    lx, ly, lw, lh = M, 150, CW, 300
    d.rectangle([lx, ly, lx + lw, ly + lh], fill=WHITE, outline=INK, width=2)
    pad = 18
    kf = font(SANS_B, 18)
    d.text((lx + pad, ly + 12), "MARKETS  ·  THE AI ROUT", font=kf, fill=RED)
    icon_chart(d, lx + lw - pad - 78, ly + 12, 64)
    hf = font(SANS_B, 37)
    headline = "Anthropic's record $81bn IPO fails to calm the AI rout"
    hlines = wrap(d, headline, hf, lw - 2 * pad - 96)
    hy = ly + 40
    for ln in hlines[:2]:
        d.text((lx + pad, hy), ln, font=hf, fill=INK)
        hy += 44
    # stat strip
    stats = [("NIKKEI", "-4 to -5%"), ("KOSPI", "-4.7 to -5.2%"),
             ("TAIEX", "-6 to -6.75%"), ("S&P 500", "-2.0%")]
    sw, gap = 226, 12
    sy0 = hy + 10
    for i, (lab, val) in enumerate(stats):
        bx = lx + pad + i * (sw + gap)
        d.rectangle([bx, sy0, bx + sw, sy0 + 62], fill=RED_TINT,
                    outline=(232, 180, 180), width=1)
        lf = font(SANS_B, 13)
        d.text((bx + 10, sy0 + 6), lab, font=lf, fill=GRAY)
        vf = font(SANS_B, 25)
        d.text((bx + 10, sy0 + 26), val, font=vf, fill=RED)
    # summary lines
    sf = font(SANS, 17)
    s1 = ("Anthropic priced at $83, opened above $111 and closed +17% at $97.17 "
          "— about $1.3tn. It then fell ~3% after hours.")
    s2 = ("Asian shares head for their worst week since 2020; Taiwan is down 16% "
          "for the week, its biggest since 1991.")
    sy = sy0 + 62 + 12
    for ln in wrap(d, s1, sf, lw - 2 * pad):
        d.text((lx + pad, sy), ln, font=sf, fill=(51, 51, 51))
        sy += 21
    for ln in wrap(d, s2, sf, lw - 2 * pad):
        d.text((lx + pad, sy), ln, font=sf, fill=(51, 51, 51))
        sy += 21

    # ---- story panels ---------------------------------------------------
    row1_y, row2_y = 462, 674
    ph, pw3, pw2 = 200, 317, 482
    panels_row1 = [
        ("CLIMATE · COP31", (21, 128, 61),
         "Fossil fuels deleted from COP31 draft",
         "Final day in Antalya with no deal in sight. Panama threatens to "
         "block consensus; extension likely.", "leaf"),
        ("EUROPE", (29, 78, 216),
         "Poland probes unknown objects",
         "Objects near the Ukrainian border; warning lifted 07:30. EU to "
         "summon envoy over embassy damage.", "eu"),
        ("UKRAINE", (71, 85, 105),
         "UK pledges 1,000+ drones for Ukraine",
         "A £260m package of long-range drones and other capabilities, "
         "announced in Berlin.", "drone"),
    ]
    panels_row2 = [
        ("SPORT", (180, 83, 9),
         "Trump pardons baseball's Pete Rose",
         "Posthumous pardon wipes away tax convictions. It alone does not "
         "put him in the Hall of Fame.", "baseball"),
        ("EL SALVADOR", (126, 34, 206),
         "Bukele registers for a third term",
         "The president formally filed his candidacy for a third consecutive "
         "term with the electoral court.", "ballot"),
    ]
    for i, (k, kc, hl, sm, ic) in enumerate(panels_row1):
        draw_panel(d, M + i * (pw3 + 12), row1_y, pw3, ph, k, kc, hl, sm, ic)
    for i, (k, kc, hl, sm, ic) in enumerate(panels_row2):
        draw_panel(d, M + i * (pw2 + 12), row2_y, pw2, ph, k, kc, hl, sm, ic)

    # ---- footer ----------------------------------------------------------
    fx, fy, fw, fh = M, 886, CW, 114
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=WHITE, outline=BORDER, width=1)
    tf = font(SANS_B, 16)
    d.text((fx + 14, fy + 10), "ALSO ON 20 NOVEMBER", font=tf, fill=INK)
    bf = font(SANS, 15)
    left = ["US sanctions Comancheros and 'Ndrangheta",
            "UK retail +0.7%; borrowing £17bn in Oct",
            "Iraq moves into Kataib Hezbollah stronghold"]
    right = ["UK-EU summit: youth mobility deal expected",
             "UN chief race stalls after eight votes"]
    by = fy + 36
    for i, item in enumerate(left):
        d.text((fx + 14, by + i * 20), "▪  " + item, font=bf, fill=(51, 51, 51))
    for i, item in enumerate(right):
        d.text((fx + 500, by + i * 20), "▪  " + item, font=bf, fill=(51, 51, 51))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("saved", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
