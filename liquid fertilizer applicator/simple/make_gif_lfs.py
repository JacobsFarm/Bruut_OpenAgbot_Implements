"""Zet de frames van animate_lfs om naar een GIF met bijschrift en een paneel 'mesdiepte per rij'.

Werkt in de Python van FreeCAD (Pillow zit erbij) of in een gewone Python met Pillow:
    python make_gif_lfs.py <map_met_frames> <uit.gif> [fps]
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
DEPTH_RANGE = (0.0, 70.0)       # mm onder maaiveld, schaal van het paneel
TARGET = 40.0
ROW_NAMES = ("1", "2", "3", "4", "5")


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def nl(value, decimals=1):
    return ("%.*f" % (decimals, value)).replace(".", ",")


def caption(m):
    pump = "pomp aan, %s l/min" % nl(m["flow"], 1) if m["pump"] else "pomp uit"
    depths = [d for d in m["depth"] if d > 0.0]
    if not depths:
        knife = "messen boven de grond"
    elif round(min(depths)) == round(max(depths)):
        knife = "mesdiepte %s mm" % nl(min(depths), 0)
    else:
        knife = "mesdiepte %s–%s mm" % (nl(min(depths), 0), nl(max(depths), 0))
    return [
        "%s   ·   %s m/s   ·   %s m" % (m["state"], nl(m["v"] / 1000.0, 2), nl(m["dist"] / 1000.0)),
        "%s   ·   toegediend %s l" % (pump, nl(m["applied_l"], 2)),
        "hefraam %s%s°   ·   %s" % ("+" if m["psi"] >= 0 else "", nl(m["psi"]), knife),
        "robot stampt %s°  rolt %s°" % (nl(m["pitch"]), nl(m["roll"])),
    ]


def panel(draw, m, small, x0, y0):
    w, h = 250, 140
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 220))
    draw.text((x0 + 10, y0 + 6), "bodemvolging: mesdiepte (mm)", fill=(30, 30, 30, 255), font=small)
    lo, hi = DEPTH_RANGE
    top, bot = y0 + 30, y0 + h - 22

    def zy(v):
        v = max(lo, min(hi, v))
        return top + (v - lo) / (hi - lo) * (bot - top)

    ground = zy(0.0)
    target = zy(TARGET)
    draw.line((x0 + 10, ground, x0 + w - 10, ground), fill=(110, 140, 70, 255), width=2)
    for xx in range(x0 + 10, x0 + w - 10, 8):
        draw.line((xx, target, xx + 4, target), fill=(120, 120, 120, 255), width=1)
    values = list(m["depth"]) + [None]
    names = list(ROW_NAMES) + ["wielen"]
    slot_w = (w - 20) / len(values)
    for i, (v, name) in enumerate(zip(values, names)):
        cx = x0 + 10 + slot_w * (i + 0.5)
        if v is None:
            for k, g in enumerate(m["wheel_gap"]):
                on = g < 5.0
                yy = ground + 18 + k * 18
                color = (60, 60, 60, 255) if on else (190, 190, 190, 255)
                draw.ellipse((cx - 7, yy - 7, cx + 7, yy + 7), outline=color, width=3)
                draw.text((cx + 11, yy), "L" if k == 0 else "R", fill=color, font=small, anchor="lm")
            draw.text((cx, bot + 3), name, fill=(60, 60, 60, 255), font=small, anchor="mt")
            continue
        color = (235, 104, 52, 255) if v > 0.0 else (190, 190, 190, 255)
        y = zy(max(0.0, v))
        draw.rectangle((cx - 9, ground, cx + 9, max(ground + 1, y)), fill=color)
        draw.text((cx, bot + 3), name, fill=(60, 60, 60, 255), font=small, anchor="mt")
        draw.text((cx, max(ground + 1, y) + 2), nl(v, 0), fill=(40, 40, 40, 255), font=small, anchor="mt")


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
        draw.text((10 + pad, 10 + pad + i * line_h), line, fill=(30, 30, 30, 255), font=font)
    panel(draw, m, small, image.width - 262, image.height - 152)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=10, last_hold_ms=1500):
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    font = load_font(16)
    small = load_font(13)
    images = [decorate(Image.open(os.path.join(folder, n)), metas[int(n[6:10])], font, small) for n in names]

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
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 10)
