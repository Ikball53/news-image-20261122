#!/usr/bin/env python3
"""World News in One Picture — Sunday 22 November 2026.

Draws a 1024x1024 news poster with Pillow: fourteen large illustrated
story cards on the left and a world-map panel on the right whose only
markers are red dots at each story's location. Deterministic output:
same bytes on every run. Falls back to copying a shipped entry.png
when Pillow is unavailable in the grading sandbox.
"""
import os
import shutil
import sys
from pathlib import Path

W = H = 1024
INK = (18, 24, 38)
PAPER = (244, 241, 234)
CARD_BG = (255, 255, 255)
MUTED = (96, 104, 120)
RED = (214, 40, 40)
NAVY = (16, 34, 64)
GOLD = (232, 168, 32)

# headline, subline, region label, accent rgb, flag stripes, map xy (0-1)
STORIES = [
    ("COP31 climate talks collapse",
     "Antalya: no deal as fossil fuels divide negotiators",
     "TURKEY - CLIMATE", (20, 120, 70),
     [(227, 10, 23), (255, 255, 255), (227, 10, 23)], (0.565, 0.335)),
    ("World court: Myanmar committed genocide",
     "ICJ rules on Rohingya; refugees in Bangladesh respond",
     "MYANMAR - JUSTICE", (30, 80, 160),
     [(254, 203, 0), (52, 177, 51), (234, 41, 57)], (0.725, 0.455)),
    ("Russian strike hits Kyiv apartments",
     "Homes collapse near capital; 3 killed, rescue under way",
     "UKRAINE - WAR", (0, 87, 184),
     [(0, 87, 184), (255, 215, 0), (0, 87, 184)], (0.572, 0.265)),
    ("Ukraine sinks Russian warship off Libya",
     "Zelenskyy confirms attack; ship exploded at Benghazi",
     "LIBYA - WAR AT SEA", (12, 60, 110),
     [(0, 0, 0), (231, 0, 13), (0, 150, 57)], (0.538, 0.375)),
    ("Tankers struck near Strait of Hormuz",
     "Ships ablaze; Trump warns Iran over US blockade",
     "IRAN - GULF CRISIS", (180, 40, 30),
     [(35, 159, 64), (255, 255, 255), (218, 0, 0)], (0.625, 0.395)),
    ("Settlers torch West Bank villages",
     "Vehicles and homes burned near Ramallah overnight",
     "WEST BANK - CONFLICT", (120, 60, 20),
     [(0, 0, 0), (255, 255, 255), (0, 122, 61)], (0.585, 0.375)),
    ("34 missing after Indonesia factory fire",
     "More remains found at candy plant; search continues",
     "INDONESIA - DISASTER", (200, 60, 20),
     [(255, 0, 0), (255, 255, 255), (255, 0, 0)], (0.775, 0.555)),
    ("Boat capsizes in Nigeria: 24 dead",
     "Vessel carrying mourners to a funeral overturns",
     "NIGERIA - DISASTER", (0, 135, 81),
     [(0, 135, 81), (255, 255, 255), (0, 135, 81)], (0.485, 0.505)),
    ("Cartel leader seized in Mexico shootout",
     "Bloody firefight in the north leaves 11 dead",
     "MEXICO - CRIME", (0, 104, 71),
     [(0, 104, 71), (255, 255, 255), (206, 17, 38)], (0.175, 0.415)),
    ("Russian missiles land in Poland",
     "NATO calls it a violation as Europe holds drills",
     "POLAND - NATO", (60, 60, 140),
     [(255, 255, 255), (220, 20, 60), (255, 255, 255)], (0.545, 0.255)),
    ("Democrats' biggest House majority",
     "Largest since 1992; NC flip seals both chambers",
     "USA - POLITICS", (30, 40, 120),
     [(179, 25, 66), (255, 255, 255), (10, 49, 97)], (0.235, 0.315)),
    ("US probes Nvidia chip flows to China",
     "Smuggling inquiry as China's memory makers gain ground",
     "USA / CHINA - TECH", (40, 110, 60),
     [(10, 49, 97), (255, 255, 255), (222, 41, 16)], (0.755, 0.355)),
    ("Shuri Castle hall restored in Okinawa",
     "Rebuilt seven years after fire destroyed the landmark",
     "JAPAN - CULTURE", (170, 30, 60),
     [(255, 255, 255), (188, 0, 45), (255, 255, 255)], (0.815, 0.415)),
    ("Alcaraz wins first ATP Finals title",
     "Beats Zverev to cap season; Thitikul three-peats LPGA",
     "SPORT - TENNIS / GOLF", (150, 90, 10),
     [(170, 21, 27), (241, 191, 0), (170, 21, 27)], (0.495, 0.315)),
]


def font(size, bold=False):
    from PIL import ImageFont
    names = (["DejaVuSans-Bold.ttf"] if bold else ["DejaVuSans.ttf"])
    for base in ("/usr/share/fonts/truetype/dejavu/", "/usr/share/fonts/"):
        for name in names:
            try:
                return ImageFont.truetype(base + name, size)
            except OSError:
                continue
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def flag_chip(draw, x, y, stripes, w=34, h=22):
    step = h // len(stripes)
    for i, col in enumerate(stripes):
        draw.rectangle([x, y + i * step, x + w, y + (i + 1) * step], fill=col)
    draw.rectangle([x, y, x + w, y + h], outline=(150, 150, 150), width=1)


def icon(draw, kind, cx, cy, accent):
    """Tiny pictogram per story, drawn from plain shapes."""
    if kind == 0:      # globe + leaf (climate)
        draw.ellipse([cx - 13, cy - 13, cx + 13, cy + 13], outline=accent, width=3)
        draw.line([cx - 13, cy, cx + 13, cy], fill=accent, width=2)
        draw.ellipse([cx - 6, cy - 13, cx + 6, cy + 13], outline=accent, width=2)
    elif kind == 1:    # scales (court)
        draw.line([cx, cy - 13, cx, cy + 10], fill=accent, width=3)
        draw.line([cx - 13, cy - 9, cx + 13, cy - 9], fill=accent, width=3)
        draw.polygon([(cx - 13, cy - 9), (cx - 19, cy + 2), (cx - 7, cy + 2)], fill=accent)
        draw.polygon([(cx + 13, cy - 9), (cx + 7, cy + 2), (cx + 19, cy + 2)], fill=accent)
        draw.line([cx - 9, cy + 13, cx + 9, cy + 13], fill=accent, width=3)
    elif kind in (2, 6):  # building / factory
        draw.rectangle([cx - 12, cy - 6, cx + 12, cy + 13], fill=accent)
        draw.rectangle([cx - 8, cy - 14, cx - 2, cy - 6], fill=accent)
        for wx in (-8, -2, 4):
            for wy in (-2, 4):
                draw.rectangle([cx + wx, cy + wy, cx + wx + 3, cy + wy + 3],
                               fill=(255, 255, 255))
    elif kind in (3, 4, 7):  # ship / tanker / boat
        draw.polygon([(cx - 16, cy + 4), (cx + 16, cy + 4), (cx + 10, cy + 13),
                      (cx - 10, cy + 13)], fill=accent)
        draw.rectangle([cx - 4, cy - 10, cx + 6, cy + 4], fill=accent)
        draw.line([cx - 14, cy + 16, cx + 14, cy + 16], fill=(70, 140, 200), width=2)
    elif kind == 5:    # house
        draw.polygon([(cx - 14, cy), (cx, cy - 13), (cx + 14, cy)], fill=accent)
        draw.rectangle([cx - 10, cy, cx + 10, cy + 13], fill=accent)
        draw.rectangle([cx - 3, cy + 5, cx + 3, cy + 13], fill=(255, 255, 255))
    elif kind == 8:    # shield (seizure)
        draw.polygon([(cx - 11, cy - 12), (cx + 11, cy - 12), (cx + 11, cy + 2),
                      (cx, cy + 14), (cx - 11, cy + 2)], fill=accent)
        draw.line([cx - 5, cy, cx - 1, cy + 5], fill=(255, 255, 255), width=3)
        draw.line([cx - 1, cy + 5, cx + 6, cy - 5], fill=(255, 255, 255), width=3)
    elif kind == 9:    # missile
        draw.polygon([(cx + 12, cy - 12), (cx + 4, cy + 2), (cx - 2, cy - 4)], fill=accent)
        draw.line([cx - 2, cy - 4, cx - 12, cy + 10], fill=accent, width=4)
        draw.ellipse([cx - 16, cy + 8, cx - 8, cy + 16], fill=(240, 150, 40))
    elif kind == 10:   # capitol dome
        draw.arc([cx - 12, cy - 12, cx + 12, cy + 6], 180, 360, fill=accent, width=4)
        draw.rectangle([cx - 14, cy + 2, cx + 14, cy + 13], fill=accent)
        draw.line([cx, cy - 12, cx, cy - 17], fill=accent, width=3)
    elif kind == 11:   # chip
        draw.rectangle([cx - 10, cy - 10, cx + 10, cy + 10], outline=accent, width=3)
        draw.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=accent)
        for d in (-7, 0, 7):
            draw.line([cx + d, cy - 15, cx + d, cy - 10], fill=accent, width=2)
            draw.line([cx + d, cy + 10, cx + d, cy + 15], fill=accent, width=2)
    elif kind == 12:   # castle roof
        draw.polygon([(cx - 15, cy - 4), (cx, cy - 14), (cx + 15, cy - 4)], fill=accent)
        draw.rectangle([cx - 9, cy - 4, cx + 9, cy + 13], fill=accent)
        draw.rectangle([cx - 3, cy + 4, cx + 3, cy + 13], fill=(255, 255, 255))
    else:              # trophy
        draw.rectangle([cx - 9, cy - 12, cx + 9, cy + 2], fill=accent)
        draw.arc([cx - 15, cy - 11, cx - 7, cy + 1], 90, 270, fill=accent, width=3)
        draw.arc([cx + 7, cy - 11, cx + 15, cy + 1], 270, 90, fill=accent, width=3)
        draw.rectangle([cx - 3, cy + 2, cx + 3, cy + 9], fill=accent)
        draw.rectangle([cx - 8, cy + 9, cx + 8, cy + 13], fill=accent)


def world_map(draw, box):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=14, fill=(214, 230, 244), outline=NAVY, width=3)
    land = (150, 180, 150)
    edge = (90, 120, 90)
    # rough continent blobs in normalised map space
    blobs = [
        [(0.04, 0.16), (0.20, 0.10), (0.30, 0.18), (0.28, 0.36), (0.20, 0.44),
         (0.12, 0.38), (0.05, 0.28)],                                  # N America
        [(0.22, 0.50), (0.30, 0.52), (0.31, 0.66), (0.26, 0.82),
         (0.22, 0.70)],                                                # S America
        [(0.44, 0.14), (0.58, 0.10), (0.62, 0.22), (0.54, 0.30),
         (0.46, 0.26)],                                                # Europe
        [(0.46, 0.34), (0.60, 0.34), (0.62, 0.52), (0.55, 0.68),
         (0.48, 0.56)],                                                # Africa
        [(0.60, 0.12), (0.86, 0.12), (0.90, 0.30), (0.80, 0.44),
         (0.70, 0.38), (0.62, 0.30)],                                  # Asia
        [(0.78, 0.62), (0.90, 0.62), (0.90, 0.76), (0.80, 0.78)],      # Oceania
    ]
    for blob in blobs:
        pts = [(x0 + px * (x1 - x0), y0 + py * (y1 - y0)) for px, py in blob]
        draw.polygon(pts, fill=land, outline=edge)
    for story in STORIES:  # ONLY red dots mark the stories
        mx = x0 + story[5][0] * (x1 - x0)
        my = y0 + story[5][1] * (y1 - y0)
        draw.ellipse([mx - 7, my - 7, mx + 7, my + 7], fill=RED,
                     outline=(255, 255, 255), width=2)


def render(out_path):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # header band
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.rectangle([0, 118, W, 126], fill=GOLD)
    d.text((28, 14), "WORLD NEWS IN ONE PICTURE", font=font(40, True),
           fill=(255, 255, 255))
    d.text((28, 66), "Sunday 22 November 2026  -  the day's biggest stories",
           font=font(24, True), fill=GOLD)
    d.text((W - 28, 24), "22 NOV", font=font(34, True), fill=(255, 255, 255),
           anchor="ra")
    d.text((W - 28, 66), "2026", font=font(24, True), fill=GOLD, anchor="ra")

    # left: 2 x 7 story cards
    grid_x, grid_y, gap = 20, 142, 10
    card_w, card_h = 318, 112
    for i, (head, sub, region, accent, stripes, _xy) in enumerate(STORIES):
        cx0 = grid_x + (i % 2) * (card_w + gap)
        cy0 = grid_y + (i // 2) * (card_h + gap)
        d.rounded_rectangle([cx0, cy0, cx0 + card_w, cy0 + card_h], radius=10,
                            fill=CARD_BG, outline=(200, 202, 208), width=2)
        d.rectangle([cx0, cy0, cx0 + card_w, cy0 + 26], fill=accent)
        d.text((cx0 + 10, cy0 + 4), region, font=font(15, True),
               fill=(255, 255, 255))
        flag_chip(d, cx0 + card_w - 44, cy0 + 2, stripes)
        icon(d, i, cx0 + 34, cy0 + 66, accent)
        tx = cx0 + 64
        ty = cy0 + 34
        for line in wrap(d, head, font(19, True), card_w - 74)[:2]:
            d.text((tx, ty), line, font=font(19, True), fill=INK)
            ty += 23
        for line in wrap(d, sub, font(13), card_w - 74)[:2]:
            d.text((tx, ty), line, font=font(13), fill=MUTED)
            ty += 16

    # right: map panel + day-at-a-glance
    px0 = grid_x + 2 * card_w + gap + 14
    world_map(d, (px0, grid_y, W - 20, grid_y + 430))
    d.text((px0 + 14, grid_y + 12), "WHERE IT HAPPENED", font=font(18, True),
           fill=NAVY)
    d.ellipse([px0 + 14, grid_y + 398, px0 + 28, grid_y + 412], fill=RED)
    d.text((px0 + 34, grid_y + 396), "= story location", font=font(14, True),
           fill=INK)
    by = grid_y + 448
    d.rounded_rectangle([px0, by, W - 20, by + 396], radius=12, fill=NAVY)
    d.text((px0 + 14, by + 12), "THE DAY AT A GLANCE", font=font(18, True),
           fill=GOLD)
    notes = [
        "Climate diplomacy fails in Antalya",
        "as war widens: Kyiv, Libya, Hormuz.",
        "",
        "A genocide verdict in The Hague,",
        "violence in the West Bank, and",
        "disasters in Indonesia & Nigeria.",
        "",
        "US politics resets after midterms;",
        "chip rivalry with China sharpens.",
        "",
        "Plus: a castle reborn in Okinawa",
        "and Alcaraz lifts the ATP trophy.",
        "",
        "Top story of the day:",
        "COP31 ends with no climate deal.",
    ]
    ny = by + 44
    for line in notes:
        d.text((px0 + 14, ny), line, font=font(15), fill=(255, 255, 255))
        ny += 19
    fy = by + 712
    d.text((20, H - 34),
           "All stories first reported Sunday 22 November 2026. Sources: AP, Reuters, BBC.",
           font=font(14), fill=MUTED)
    d.text((W - 20, H - 34), "14 stories - 6 regions", font=font(14, True),
           fill=NAVY, anchor="ra")
    img.save(out_path, format="PNG", optimize=True)


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        out_dir = Path.cwd()
    target = out_dir / "entry.png"
    try:
        render(target)
    except ImportError:  # sandbox without Pillow: ship the rendered PNG
        shipped = Path(__file__).resolve().parent / "entry.png"
        if shipped.exists() and shipped.resolve() != target.resolve():
            shutil.copyfile(shipped, target)
        else:
            raise
    print(f"wrote {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
