#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Pure Python stdlib. Renders a short, warm invitation letter as one
1024x1024 PNG using a hand-defined 5x7 bitmap font, simple shape
drawing (house, sun, kettle, cookie, heart) and a hand-rolled PNG
encoder (zlib + struct). No Pillow, no numpy, no third-party imports.

Writes entry.png to MAKEFUN_OUTPUT_DIR (or /output by default),
validates it (PNG signature, 1024x1024, <= 1 MiB, decodable, text
actually drawn), mode 0644.
"""

import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024
MAX_BYTES = 1_048_576

# ---------------------------------------------------------------- palette
PAPER = (253, 243, 214)      # warm cream paper
PAPER_EDGE = (244, 228, 188)  # slightly deeper paper near the border
INK = (58, 38, 24)           # dark brown ink
BORDER = (139, 94, 60)       # warm brown frame
BORDER_SOFT = (190, 150, 105)
ROOF = (176, 72, 48)         # terracotta roof
HOUSE_WALL = (238, 196, 132)
DOOR = (122, 72, 40)
WINDOW = (255, 214, 110)
SUN = (255, 196, 66)
SUN_RAY = (240, 160, 40)
HEART = (198, 74, 54)
KETTLE = (74, 128, 128)      # teal kettle
KETTLE_DARK = (52, 96, 96)
STEAM = (150, 150, 150)
COOKIE = (205, 155, 90)
CHIP = (90, 55, 30)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 characters; '#' is ink, '.' is empty.
# Defined by hand in this file for the characters the letter needs.
FONT = {
    "A": ("#...#", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "####.", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "####.", "#....", "#####"),
    "F": ("#####", "#....", "####.", "#....", "#...."),
    "G": (".####", "#....", "#.###", "#...#", ".###."),
    "H": ("#...#", "#...#", "#####", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#..#."),
    "L": ("#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "####.", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#.#.#", ".##.#"),
    "R": ("####.", "#...#", "####.", "#.#..", "#..#."),
    "S": (".####", "#....", ".###.", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", "#####"),
    "a": (".###.", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "####.", "#...#", "#...#", "####."),
    "c": (".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", ".####", "#...#", "#...#", ".####"),
    "e": (".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", "####.", ".#...", ".#..."),
    "g": (".####", "#...#", "#...#", ".####", "....#"),
    "h": ("#....", "####.", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", ".##.."),
    "k": ("#....", "#..#.", "#.#..", "##...", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", ".###."),
    "m": ("##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": ("####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".###.", "#...#", "#...#", "#...#", ".###."),
    "p": ("####.", "#...#", "#...#", "####.", "#...."),
    "q": (".####", "#...#", "#...#", ".####", "....#"),
    "r": ("#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", "####.", ".#...", ".#...", "..##."),
    "u": ("#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": ("#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": ("#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "x": ("#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": ("#...#", "#...#", "#...#", ".####", ".###."),
    "z": ("#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "...#.", "..#..", "#####"),
    "3": ("####.", "....#", ".###.", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#####", "...#."),
    "5": ("#####", "#....", "####.", "....#", ".###."),
    "6": (".###.", "#....", "####.", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#.."),
    "8": (".###.", "#...#", ".###.", "#...#", ".###."),
    "9": (".###.", "#...#", ".####", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".##.."),
    ",": (".....", ".....", ".....", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "...#.", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", "....."),
    "-": (".....", ".....", ".###.", ".....", "....."),
    "\u2014": (".....", ".....", "#####", ".....", "....."),
    ":": (".....", ".##..", ".....", ".##..", "....."),
    ";": (".....", ".##..", ".....", ".##..", ".#..."),
    "(": ("...#.", "..#..", ".#...", ".#...", "..#.."),
    ")": (".#...", "..#..", "...#.", "...#.", "..#.."),
    "&": (".##..", "#..#.", ".#...", "#.#.#", ".##.#"),
}


def glyph(ch):
    """Return the 5-row glyph for ch (5 rows x 5 cols), blank if unknown."""
    rows = FONT.get(ch)
    if rows is None:
        return (".....",) * 5
    # Pad the 5-row definitions out to 7 rows: rows above are the
    # middle band; add one empty row top and bottom for descenders.
    return (".....",) + rows + (".....",)


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.buf = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, color)

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.width, x1)
        y1 = min(self.height, y1)
        r, g, b = color
        for y in range(y0, y1):
            i = (y * self.width + x0) * 3
            for x in range(x0, x1):
                self.buf[i] = r
                self.buf[i + 1] = g
                self.buf[i + 2] = b
                i += 3

    def rect_outline(self, x0, y0, x1, y1, color, w=1):
        self.fill_rect(x0, y0, x1, y0 + w, color)
        self.fill_rect(x0, y1 - w, x1, y1, color)
        self.fill_rect(x0, y0, x0 + w, y1, color)
        self.fill_rect(x1 - w, y0, x1, y1, color)

    def line(self, x0, y0, x1, y1, color, w=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for ox in range(w):
                for oy in range(w):
                    self.set_pixel(x0 + ox, y0 + oy, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            dx = int((r * r - (y - cy) ** 2) ** 0.5)
            self.fill_rect(cx - dx, y, cx + dx + 1, y + 1, color)

    def circle_outline(self, cx, cy, r, color, w=2):
        for a in range(0, 360):
            import math

            rad = math.radians(a)
            for t in range(w):
                self.set_pixel(
                    int(cx + (r - t) * math.cos(rad)),
                    int(cy + (r - t) * math.sin(rad)),
                    color,
                )

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Scanline fill: sort vertices by y, then walk edges.
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / max(1, by - ay)
                xa = ax + (bx - ax) * t1
            else:
                xa = bx
            t2 = (y - ay) / max(1, cy - ay)
            xb = ax + (cx - ax) * t2
            if xa > xb:
                xa, xb = xb, xa
            self.fill_rect(int(xa), y, int(xb) + 1, y + 1, color)

    def text(self, x, y, s, scale, color):
        """Draw s with the 5x7 font at scale; returns the width drawn."""
        cx = x
        for ch in s:
            rows = glyph(ch)
            for ry, row in enumerate(rows):
                for rx, bit in enumerate(row):
                    if bit == "#":
                        self.fill_rect(
                            cx + rx * scale,
                            y + ry * scale,
                            cx + (rx + 1) * scale,
                            y + (ry + 1) * scale,
                            color,
                        )
            cx += 6 * scale
        return cx - x

    def text_width(self, s, scale):
        return len(s) * 6 * scale


# ------------------------------------------------------------------ doodles
def draw_house(cv, x0, y0):
    """A little house with a chimney, centred on x0, roof apex at y0."""
    # chimney
    cv.fill_rect(x0 + 48, y0 + 14, x0 + 68, y0 + 52, DOOR)
    # smoke puffs
    cv.fill_circle(x0 + 58, y0 + 2, 7, STEAM)
    cv.fill_circle(x0 + 66, y0 - 8, 9, STEAM)
    # body
    cv.fill_rect(x0 - 80, y0 + 64, x0 + 80, y0 + 128, HOUSE_WALL)
    cv.rect_outline(x0 - 80, y0 + 64, x0 + 80, y0 + 128, BORDER, 3)
    # roof
    cv.fill_triangle(x0 - 100, y0 + 66, x0, y0, x0 + 100, y0 + 66, ROOF)
    # door
    cv.fill_rect(x0 - 20, y0 + 88, x0 + 20, y0 + 128, DOOR)
    cv.fill_circle(x0 + 12, y0 + 110, 3, WINDOW)
    # windows
    cv.fill_rect(x0 - 66, y0 + 80, x0 - 36, y0 + 106, WINDOW)
    cv.rect_outline(x0 - 66, y0 + 80, x0 - 36, y0 + 106, BORDER, 2)
    cv.line(x0 - 51, y0 + 80, x0 - 51, y0 + 106, BORDER, 2)
    cv.fill_rect(x0 + 36, y0 + 80, x0 + 66, y0 + 106, WINDOW)
    cv.rect_outline(x0 + 36, y0 + 80, x0 + 66, y0 + 106, BORDER, 2)
    cv.line(x0 + 51, y0 + 80, x0 + 51, y0 + 106, BORDER, 2)


def draw_sun(cv, cx, cy):
    cv.fill_circle(cx, cy, 34, SUN)
    cv.circle_outline(cx, cy, 34, SUN_RAY, 3)
    for a in range(0, 360, 45):
        import math

        rad = math.radians(a)
        x0 = int(cx + 44 * math.cos(rad))
        y0 = int(cy + 44 * math.sin(rad))
        x1 = int(cx + 60 * math.cos(rad))
        y1 = int(cy + 60 * math.sin(rad))
        cv.line(x0, y0, x1, y1, SUN_RAY, 3)


def draw_heart(cv, cx, cy, s):
    cv.fill_circle(cx - s // 2, cy - s // 4, s // 2, HEART)
    cv.fill_circle(cx + s // 2, cy - s // 4, s // 2, HEART)
    cv.fill_triangle(cx - s, cy, cx + s, cy, cx, cy + s, HEART)


def draw_kettle(cv, x0, y0):
    """A teal kettle with a spout, handle and steam, top-left at (x0, y0)."""
    # steam curls
    for dx, phase in ((30, 0), (55, 3)):
        for t in range(0, 34, 2):
            import math

            x = x0 + dx + int(5 * math.sin((t + phase) / 6.0))
            cv.fill_circle(x, y0 + 30 - t, 3, STEAM)
    # body: trapezoid-ish, drawn as rect + slanted sides
    cv.fill_rect(x0 + 10, y0 + 34, x0 + 80, y0 + 96, KETTLE)
    cv.fill_triangle(x0 + 10, y0 + 34, x0 + 26, y0 + 34, x0 + 10, y0 + 96, KETTLE)
    cv.fill_triangle(x0 + 80, y0 + 34, x0 + 64, y0 + 34, x0 + 80, y0 + 96, KETTLE)
    cv.rect_outline(x0 + 10, y0 + 34, x0 + 80, y0 + 96, KETTLE_DARK, 2)
    # spout
    cv.fill_triangle(x0 + 78, y0 + 44, x0 + 108, y0 + 26, x0 + 82, y0 + 62, KETTLE)
    # handle
    cv.line(x0 + 10, y0 + 44, x0 - 12, y0 + 52, KETTLE_DARK, 4)
    cv.line(x0 - 12, y0 + 52, x0 + 10, y0 + 78, KETTLE_DARK, 4)
    # lid + knob
    cv.fill_rect(x0 + 34, y0 + 28, x0 + 56, y0 + 36, KETTLE_DARK)
    cv.fill_circle(x0 + 45, y0 + 26, 5, KETTLE_DARK)


def draw_cookie(cv, cx, cy):
    cv.fill_circle(cx, cy, 42, COOKIE)
    cv.circle_outline(cx, cy, 42, CHIP, 3)
    for dx, dy in ((-16, -12), (10, -18), (18, 8), (-8, 14), (-2, -2)):
        cv.fill_circle(cx + dx, cy + dy, 5, CHIP)


# ------------------------------------------------------------------ letter
LETTER_LINES = [
    "Dear Judge,",
    "Please come visit",
    "my house!",
    "The kettle is on,",
    "the biscuits are warm,",
    "and the Wi-Fi password",
    "is on the fridge.",
    "\u2014 Your host",
]

PS_LINES = [
    "P.S. Yes, I know you're AI \u2014",
    "but a robot can dream, right?",
]


def render():
    cv = Canvas(WIDTH, HEIGHT, PAPER)
    # faint deeper-paper band inside the frame
    cv.fill_rect(46, 46, WIDTH - 46, HEIGHT - 46, PAPER_EDGE)
    cv.fill_rect(58, 58, WIDTH - 58, HEIGHT - 58, PAPER)
    # double frame
    cv.rect_outline(30, 30, WIDTH - 30, HEIGHT - 30, BORDER, 6)
    cv.rect_outline(46, 46, WIDTH - 46, HEIGHT - 46, BORDER_SOFT, 2)

    # header doodles: house centre, sun right, heart left
    draw_house(cv, WIDTH // 2, 62)
    draw_sun(cv, 872, 118)
    draw_heart(cv, 138, 122, 26)

    # the letter, scale 5
    scale = 5
    x = 140
    y = 252
    line_h = 62
    for i, line in enumerate(LETTER_LINES):
        cv.text(x, y + i * line_h, line, scale, INK)

    # divider
    cv.line(300, 752, WIDTH - 300, 752, BORDER_SOFT, 2)

    # postscript, scale 3, centred
    ps_scale = 3
    for i, line in enumerate(PS_LINES):
        w = cv.text_width(line, ps_scale)
        cv.text((WIDTH - w) // 2, 782 + i * 38, line, ps_scale, INK)

    # footer doodles: kettle left, cookie right
    draw_kettle(cv, 96, 830)
    draw_cookie(cv, 868, 872)
    return cv


# ------------------------------------------------------------------ PNG io
def png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    row_len = cv.width * 3
    for y in range(cv.height):
        raw.append(0)  # filter: none
        raw += cv.buf[y * row_len:(y + 1) * row_len]
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(
        b"IHDR", struct.pack(">IIBBBBB", cv.width, cv.height, 8, 2, 0, 0, 0)
    )
    png += png_chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += png_chunk(b"IEND", b"")
    return png


def validate_png(path):
    """Check the written file: signature, IHDR size, decodable IDAT."""
    with open(path, "rb") as f:
        data = f.read()
    if len(data) > MAX_BYTES:
        raise SystemExit("FAIL: %s is %d bytes (> 1 MiB)" % (path, len(data)))
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("FAIL: %s is not a PNG" % path)
    pos = 8
    ihdr = None
    idat = b""
    while pos < len(data):
        (ln,) = struct.unpack(">I", data[pos:pos + 4])
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + ln]
        if kind == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", payload)
        elif kind == b"IDAT":
            idat += payload
        pos += 12 + ln
    if ihdr is None:
        raise SystemExit("FAIL: no IHDR chunk")
    w, h, depth, ctype = ihdr[0], ihdr[1], ihdr[2], ihdr[3]
    if (w, h) != (WIDTH, HEIGHT):
        raise SystemExit("FAIL: dimensions %dx%d, expected 1024x1024" % (w, h))
    if depth != 8 or ctype != 2:
        raise SystemExit("FAIL: bit depth %d / colour type %d" % (depth, ctype))
    raw = zlib.decompress(idat)
    if len(raw) != HEIGHT * (1 + WIDTH * 3):
        raise SystemExit("FAIL: decoded size %d, expected %d"
                         % (len(raw), HEIGHT * (1 + WIDTH * 3)))
    return len(data), w, h, raw


def count_ink(raw, x0, y0, x1, y1):
    """Count non-paper pixels in a rectangle of the decoded image."""
    n = 0
    for y in range(y0, y1):
        row = y * (1 + WIDTH * 3) + 1
        for x in range(x0, x1):
            i = row + x * 3
            if (raw[i], raw[i + 1], raw[i + 2]) != PAPER:
                n += 1
    return n


# ------------------------------------------------------------------ main
def main():
    os.umask(0o022)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
        probe = os.path.join(out_dir, ".write-test")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
    except OSError:
        out_dir = "output"
        os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")

    cv = render()
    png = encode_png(cv)
    with open(out_path, "wb") as f:
        f.write(png)
    os.chmod(out_path, 0o644)

    size, w, h, raw = validate_png(out_path)
    # The letter text must actually be drawn: check ink in line 1 and
    # in the longest line (line 5, "the biscuits are warm,").
    ink_top = count_ink(raw, 140, 252, 500, 252 + 35)
    ink_long = count_ink(raw, 140, 252 + 4 * 62, 850, 252 + 4 * 62 + 35)
    if ink_top < 100 or ink_long < 100:
        raise SystemExit(
            "FAIL: text areas look blank (line1=%d, line5=%d ink px)"
            % (ink_top, ink_long)
        )
    print("OK: %s  %d bytes  %dx%d  line1_ink=%d  line5_ink=%d"
          % (out_path, size, w, h, ink_top, ink_long))
    return 0


if __name__ == "__main__":
    sys.exit(main())
