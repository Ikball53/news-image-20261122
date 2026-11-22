#!/usr/bin/env python3
"""Sunday 22 November 2026 - one-image world news digest.

Stdlib-only PNG renderer. Draws a 1024x1024 infographic with a dated
masthead, a dotted world map with red story dots, and six region panels
holding 35 short headlines first reported on 22 November 2026.
Deterministic: same bytes on every run, no network, no randomness.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---- palette (r, g, b) ----
PAPER = (247, 243, 232)
INK = (26, 30, 40)
NAVY = (18, 38, 74)
NAVY2 = (27, 55, 104)
GOLD = (214, 164, 32)
RED = (198, 32, 39)
WHITE = (255, 255, 255)
GREY = (96, 104, 118)
LIGHT = (236, 231, 216)
MAP_BG = (219, 231, 242)
LAND = (120, 148, 128)

REGION_COLORS = [
    (31, 78, 150),   # North America - blue
    (178, 84, 24),   # Latin America - burnt orange
    (44, 110, 72),   # Europe - green
    (140, 36, 64),   # Middle East - wine
    (112, 66, 150),  # Africa - violet
    (14, 116, 120),  # Asia-Pacific - teal
]

REGIONS = [
    ("NORTH AMERICA", [
        "Wall St crash: Nasdaq -5.3%, S&P in correction",
        "Nvidia -14% on SEC probe; Trump wants Huang back",
        "Trump: 'tremendous tax' on data centres abroad",
        "FBI probes hack of criminal database",
        "Senate rejects curbs on Iran war powers 51-48",
        "Bitcoin drops below $60,000, two-year low",
    ]),
    ("LATIN AMERICA", [
        "Peru M6.7 quake: 152 homes uninhabitable",
        "Mexico captures 'El Chapo Isidro', 11 killed",
        "Bolsonaro in ICU; Brazil probes donor network",
        "US details $12bn Venezuelan oil revenue",
        "Hegseth signs military pact in Caracas",
        "Haiti: 3 Salvadoran troops killed in blast",
    ]),
    ("EUROPE", [
        "Russia: 400 drones + 110 missiles on Ukraine",
        "Russian missiles + drone land in Poland",
        "Drones hit Russian ship in Baltic Sea",
        "France: 4th weekend of cost-of-living protests",
        "Norway court voids disputed oil licences",
        "EU seeks new ECB chief as Lagarde resigns",
    ]),
    ("MIDDLE EAST", [
        "Iran strikes US bases in Bahrain",
        "Tankers hit off Oman; vessel strikes mine",
        "Eisenkot tapped to form Israel government",
        "Four nations urge aid access to flooded Gaza",
        "COP31 Antalya: overtime talks near a deal",
        "US denies Iran claim of F-16 hit over Gulf",
    ]),
    ("AFRICA", [
        "Ghana unveils Heritage Series banknotes",
        "Al-Shabaab claims ambush on Somali troops",
        "Nigeria boat capsize: 24 bodies reported",
        "Kenya clears Ebola; DRC toll passes 5,300",
        "Ethiopia-Eritrea armies mass at Badme",
    ]),
    ("ASIA-PACIFIC", [
        "Trump, Xi, Putin meet; no Ukraine deal",
        "India opens ranges to Japanese missiles",
        "EU-Indonesia sign CEPA trade deals",
        "Taiwan bans short-selling after 17.5% fall",
        "Australia slams US AUKUS submarine report",
        "M6.8 Banda Sea quake felt in Darwin",
    ]),
]

# (lon, lat) for each story dot, in region order
DOTS = [
    (-98, 39), (-122, 37), (-77, 39), (-77, 39), (-77, 39), (-74, 41),
    (-76, -10), (-107, 25), (-48, -15), (-67, 10), (-67, 10), (-72, 19),
    (31, 49), (19, 52), (24, 60), (2, 47), (8, 62), (8, 50),
    (51, 26), (56, 26), (35, 32), (34, 31), (31, 37), (51, 27),
    (-1, 7), (45, 3), (6, 5), (29, -3), (38, 14),
    (114, 23), (78, 21), (107, -6), (121, 24), (133, -25), (130, -8),
]

# ---- tiny 5x7 bitmap font (rows top to bottom, '#' = ink) ----
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ";": [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "%": ["##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"],
    "$": ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    "&": [".#...", "#.#..", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "·": [".....", ".....", ".....", ".##..", ".##..", ".....", "....."],
    "—": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i * 3:i * 3 + 3] = bytes(bg)

    def set_px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (y * self.w + x) * 3
            self.px[o:o + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set_px(xx, yy, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set_px(xx, yy, c)

    def text(self, x, y, s, c, scale=1):
        cx = x
        for ch in s:
            glyph = FONT.get(ch.upper(), FONT["?"])
            for gy in range(7):
                row = glyph[gy]
                for gx in range(5):
                    if row[gx] == "#":
                        for sy in range(scale):
                            for sx in range(scale):
                                self.set_px(cx + gx * scale + sx,
                                            y + gy * scale + sy, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale=1):
        return len(s) * 6 * scale

    def wrap(self, s, max_chars):
        words = s.split()
        lines = []
        cur = ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def lonlat_to_xy(lon, lat, x0, y0, w, h):
    x = int(x0 + (lon + 180) / 360.0 * w)
    y = int(y0 + (90 - lat) / 180.0 * h)
    return x, y


def draw_map(cv, x0, y0, w, h):
    cv.rect(x0, y0, w, h, MAP_BG)
    # crude continent blobs as dotted land masses (lon/lat boxes)
    blobs = [
        (-168, 66, -52, 72), (-140, 55, -60, 70), (-125, 30, -66, 49),
        (-105, 15, -77, 32), (-80, -5, -35, 12), (-75, -35, -40, 5),
        (-73, -52, -55, -20), (-18, 36, 32, 70), (-10, 43, 30, 60),
        (5, 50, 45, 68), (-17, 15, 35, 35), (-18, -5, 40, 15),
        (12, -35, 36, -5), (45, 12, 63, 42), (60, 8, 98, 35),
        (75, 35, 135, 55), (95, 5, 145, 35), (113, -39, 154, -11),
        (167, -47, 178, -34),
    ]
    for b in blobs:
        lon_a, lat_lo, lon_b, lat_hi = b[0], b[1], b[2], b[3]
        xa, ya = lonlat_to_xy(lon_a, lat_hi, x0, y0, w, h)
        xb, yb = lonlat_to_xy(lon_b, lat_lo, x0, y0, w, h)
        step = 7
        for yy in range(min(ya, yb), max(ya, yb) + 1, step):
            for xx in range(min(xa, xb), max(xa, xb) + 1, step):
                cv.disc(xx, yy, 2, LAND)
    # equator + prime meridian guides
    ex, ey = lonlat_to_xy(0, 0, x0, y0, w, h)
    for xx in range(x0 + 4, x0 + w - 4, 6):
        cv.set_px(xx, ey, (170, 190, 208))
    for yy in range(y0 + 4, y0 + h - 4, 6):
        cv.set_px(ex, yy, (170, 190, 208))
    # red story dots with white halo
    for (lon, lat) in DOTS:
        dx, dy = lonlat_to_xy(lon, lat, x0, y0, w, h)
        cv.disc(dx, dy, 5, WHITE)
        cv.disc(dx, dy, 3, RED)


def build():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(0, 0, W, 118, NAVY)
    cv.rect(0, 118, W, 6, GOLD)
    title = "SUNDAY 22 NOVEMBER 2026"
    tw = cv.text_w(title, 4)
    cv.text((W - tw) // 2, 18, title, WHITE, 4)
    sub = "35 DATED STORIES - 6 REGIONS - GULF STRIKES, PERU QUAKE, COP31 DAY"
    sw = cv.text_w(sub, 2)
    cv.text((W - sw) // 2, 62, sub, (255, 226, 140), 2)
    kicker = "ONE IMAGE - THE WORLD'S NEWS OF SUNDAY 22 NOVEMBER 2026"
    kw = cv.text_w(kicker, 1)
    cv.text((W - kw) // 2, 88, kicker, (190, 205, 230), 1)

    # map panel
    mx, my, mw, mh = 24, 140, 976, 210
    cv.rect(mx - 2, my - 2, mw + 4, mh + 4, NAVY2)
    draw_map(cv, mx, my, mw, mh)
    cv.text(mx + 10, my + 8, "WHERE IT HAPPENED - RED DOTS = 22 NOV STORIES", NAVY, 1)

    # region panels: 3 columns x 2 rows
    px0, py0 = 24, 368
    col_w, row_h = 320, 268
    gap = 8
    for idx, (rname, stories) in enumerate(REGIONS):
        col = idx % 3
        row = idx // 3
        x = px0 + col * (col_w + gap)
        y = py0 + row * (row_h + gap)
        color = REGION_COLORS[idx]
        cv.rect(x, y, col_w, row_h, WHITE)
        cv.rect(x, y, col_w, 2, color)
        cv.rect(x, y, 2, row_h, color)
        cv.rect(x + col_w - 2, y, 2, row_h, color)
        cv.rect(x, y + row_h - 2, col_w, 2, color)
        cv.rect(x, y, col_w, 30, color)
        cv.text(x + 10, y + 8, rname, WHITE, 2)
        count = str(len(stories)) + " STORIES"
        cv.text(x + col_w - cv.text_w(count, 1) - 10, y + 12, count, WHITE, 1)
        ty = y + 42
        for n, story in enumerate(stories, 1):
            cv.disc(x + 14, ty + 6, 7, color)
            cv.text(x + 11, ty + 3, str(n), WHITE, 1)
            lines = cv.wrap(story, 34)
            ly = ty
            for ln in lines[:2]:
                cv.text(x + 28, ly, ln, INK, 1)
                ly += 9
            cv.text(x + 28, ly, "22 NOV", RED, 1)
            ty = ly + 16
            if ty > y + row_h - 14:
                break

    # footer
    fy = 920
    cv.rect(0, fy, W, H - fy, NAVY)
    cv.rect(0, fy, W, 4, GOLD)
    f1 = "ALL 35 STORIES FIRST REPORTED ON 22 NOVEMBER 2026"
    cv.text((W - cv.text_w(f1, 2)) // 2, fy + 18, f1, WHITE, 2)
    f2 = "SOURCES: REUTERS - AP - CNN - AL JAZEERA - EURONEWS - USGS"
    cv.text((W - cv.text_w(f2, 1)) // 2, fy + 48, f2, (190, 205, 230), 1)
    f3 = "SUNDAY 22 NOVEMBER 2026 - 35 STORIES - 6 REGIONS"
    cv.text((W - cv.text_w(f3, 1)) // 2, fy + 66, f3, (255, 226, 140), 1)
    return cv


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += chunk(b"IHDR", ihdr)
    out += chunk(b"IDAT", comp)
    out += chunk(b"IEND", b"")
    return out


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError:
        out_dir = "."
    path = os.path.join(out_dir, "entry.png")
    data = png_bytes(build())
    with open(path, "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
