"""Zet de frames van animate_fpa om naar een GIF met bijschrift, een krachtenpaneel (bovenaanzicht) en de
voerverdeling langs de vijzel.

Werkt in de Python van FreeCAD (Pillow zit erbij) of in een gewone Python met Pillow:
    python make_gif_fpa.py <map_met_frames> <uit.gif> [fps] [--clean]     (--clean: zonder tekst in beeld)
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
ANGLE_GAIN = 10.0           # hoeken in het krachtenpaneel 10x overdreven
PX_PER_MM = 0.075
PX_PER_N = 0.45
RED = (205, 30, 30, 255)
BLUE = (30, 90, 215, 255)
GREY = (90, 92, 96, 255)
TEXT = (30, 30, 30, 255)


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def nl(value, decimals=1):
    return ("%.*f" % (decimals, value)).replace(".", ",")


def caption(m):
    speed = "%s m/s" % nl(m["v"] / 1000.0, 2)
    if m["state"] == "voerschuiven" and m["v_factor"] < 0.99:
        speed += " (afgeremd: stroom te hoog)"
    return [
        "%s   ·   %s   ·   %s m" % (m["state"], speed, nl(m["dist"] / 1000.0)),
        "vijzel %s omw/min   ·   %s Nm   ·   %s W   ·   %s A" % (nl(m["rpm"], 0), nl(m["T"]), nl(m["P_el"], 0),
                                                              nl(m["I"])),
        "voer in de vijzel %s kg (voor de vijzel uit geschoven %s kg)" % (nl(m["m"]), nl(m["over"])),
        "naar het voerhek gebracht: %s kg" % nl(m["moved"]),
    ]


def rot(p, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def draw_arrow(draw, p0, p1, color, width=3):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dy)
    if length < 3:
        return
    ux, uy = dx / length, dy / length
    head = min(9.0, 0.5 * length)
    base = (p1[0] - ux * head, p1[1] - uy * head)
    draw.line((p0[0], p0[1], base[0], base[1]), fill=color, width=width)
    draw.polygon([p1, (base[0] - uy * head * 0.55, base[1] + ux * head * 0.55),
                  (base[0] + uy * head * 0.55, base[1] - ux * head * 0.55)], fill=color)


def force_panel(draw, m, small, x0, y0, w=240, h=246):
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 225))
    draw.text((x0 + 10, y0 + 5), "krachten, bovenaanzicht", fill=TEXT, font=small)
    cx, cy = x0 + 104, y0 + 72
    psi = math.radians(m["psi"] * ANGLE_GAIN)

    def to_px(p):                       # robot (x, y) mm -> paneel; robot-voor = boven, hek = rechts
        q = rot(p, psi)
        return (cx + q[0] * PX_PER_MM, cy - q[1] * PX_PER_MM)

    def poly(points, **kw):
        draw.polygon([to_px(p) for p in points], **kw)

    # voerhek
    hx = x0 + w - 16
    draw.line((hx, y0 + 24, hx, y0 + h - 68), fill=(150, 160, 165, 255), width=3)
    draw.text((hx - 4, y0 + 26), "hek", fill=GREY, font=small, anchor="ra")
    # chassis en vijzel
    for x in (-375, 375):
        poly([(x - 50, -650), (x + 50, -650), (x + 50, 650), (x - 50, 650)], outline=GREY)
    for y in (-575, -425, 425, 575):
        poly([(-500, y - 20), (500, y - 20), (500, y + 20), (-500, y + 20)], outline=GREY)
    poly([(-736, -1120), (736, -1120), (736, -760), (-736, -760)], fill=(245, 200, 60, 255), outline=GREY)
    for p_tag, (x, y) in (("RL", (-375, -500)), ("RR", (375, -500)), ("FL", (-375, 500)), ("FR", (375, 500))):
        a = math.radians(m["delta"] * ANGLE_GAIN) if p_tag[0] == "F" else 0.0
        pts = [rot(c, a) for c in ((-50, -215), (50, -215), (50, 215), (-50, 215))]
        poly([(x + c[0], y + c[1]) for c in pts], fill=(25, 25, 25, 255))
        wd = m["wheels"][p_tag]
        lat = wd["lat"]
        p0 = to_px((x + math.copysign(60, lat), y))
        draw_arrow(draw, p0, (p0[0] + lat * PX_PER_N, p0[1]), BLUE)
    # voerkracht op de vijzel: pijl eindigt op de voorkant van het blad (voer duwt van het hek af en terug)
    p1 = to_px((m["xc"], -1130))
    p0 = (p1[0] - m["F_ax"] * PX_PER_N, p1[1] + m["F_push"] * PX_PER_N)
    draw_arrow(draw, p0, p1, RED, 4)
    wl = m["wheels"]
    lines = [
        "wiellast kg: " + "  ".join("%s %s" % (t, nl(wl[t]["N"] / 9.81, 0)) for t in ("RL", "RR", "FL", "FR")),
        "voer op vijzel: %s N opzij, %s N terug" % (nl(-m["F_ax"], 0), nl(m["F_push"], 0)),
        "zijkracht vloer: achter %s N, voor %s N" % (nl(m["F_rear"], 0), nl(m["F_front"], 0)),
        "scheef %s°, stuur %s° (getekend 10x)" % (nl(m["psi"], 2), nl(m["delta"], 2)),
    ]
    for i, line in enumerate(lines):
        draw.text((x0 + 10, y0 + h - 65 + i * 15), line, fill=TEXT, font=small)
    draw.text((x0 + w - 10, y0 + 5), "grip max %s %%" % nl(100 * max(v["use"] for v in wl.values()), 0),
              fill=GREY, font=small, anchor="ra")


def auger_panel(draw, m, small, x0, y0, w=250, h=104):
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 225))
    draw.text((x0 + 10, y0 + 5), "voer langs de vijzel (kg/m)   motor ← → hek", fill=TEXT, font=small)
    bins = m["bins"]
    cap = m["cap_bin"]
    n = len(bins)
    top, bot = y0 + 26, y0 + h - 12
    vmax = 2.0 * cap
    bw = (w - 20) / float(n)
    zc = bot - (bot - top) * min(1.0, cap / vmax)
    for i, b in enumerate(bins):
        hgt = (bot - top) * min(1.0, b / vmax)
        color = (225, 160, 20, 255) if b <= cap else (205, 60, 30, 255)
        bx = x0 + 10 + i * bw
        draw.rectangle((bx, bot - hgt, bx + bw - 0.6, bot), fill=color)
    draw.line((x0 + 10, zc, x0 + w - 10, zc), fill=(80, 80, 80, 255), width=1)
    draw.text((x0 + 12, zc - 2), "capaciteit %s kg/m" % nl(cap / 0.025, 0), fill=GREY, font=small, anchor="lb")
    draw.line((x0 + 10, bot, x0 + w - 10, bot), fill=(120, 120, 120, 255), width=1)


def decorate(image, m, font, small):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = caption(m)
    pad = 8
    line_h = font.size + 5
    width = max(draw.textlength(line, font=font) for line in lines) + 2 * pad
    draw.rounded_rectangle((10, 10, 10 + width, 10 + line_h * len(lines) + 2 * pad - 4), radius=8,
                           fill=(255, 255, 255, 215))
    for i, line in enumerate(lines):
        draw.text((10 + pad, 10 + pad + i * line_h), line, fill=TEXT, font=font)
    force_panel(draw, m, small, image.width - 250, image.height - 256)
    auger_panel(draw, m, small, 10, image.height - 114)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=8, last_hold_ms=1800, overlay=True):
    """overlay=False: alleen de 3D-beelden, zonder bijschrift en panelen."""
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    font = load_font(15)
    small = load_font(12)
    if overlay:
        images = [decorate(Image.open(os.path.join(folder, n)), metas[int(n[6:10])], font, small) for n in names]
    else:
        images = [Image.open(os.path.join(folder, n)).convert("RGB") for n in names]

    sample = [images[i] for i in range(0, len(images), max(1, len(images) // 12))]
    sheet = Image.new("RGB", (images[0].width, images[0].height * len(sample)))
    for i, im in enumerate(sample):
        sheet.paste(im, (0, i * images[0].height))
    palette = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]
    durations = []
    previous = 0
    for i in range(len(frames)):
        current = int(round((i + 1) * 1000.0 / fps / 10.0)) * 10
        durations.append(current - previous)
        previous = current
    durations[-1] = last_hold_ms
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=False)
    print("%d frames -> %s (%.2f MB)" % (len(frames), out_path, os.path.getsize(out_path) / 1e6))
    return out_path


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--clean"]
    main(args[0], args[1], int(args[2]) if len(args) > 2 else 8, overlay="--clean" not in sys.argv)
