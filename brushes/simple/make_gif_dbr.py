"""Zet de frames van animate_dbr om naar een GIF met bijschrift en de verdeling van het materiaal over de breedte
(wat de borstels al gepasseerd zijn, kg/m2 per 100 mm).

Werkt in de Python van FreeCAD (Pillow zit erbij) of in een gewone Python met Pillow:
    python make_gif_dbr.py <map_met_frames> <uit.gif> [fps] [--clean]     (--clean: zonder tekst in beeld)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (90, 92, 96, 255)
BAR = (205, 150, 60, 255)


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def nl(value, decimals=1):
    return ("%.*f" % (decimals, value)).replace(".", ",")


def caption(m):
    per = "per borstel" if m["n"] > 1 else "borstel"
    return [
        m["title"],
        "%s   ·   %s m/s   ·   %s m" % (m["state"], nl(m["v"] / 1000.0, 2), nl(m["dist"] / 1000.0)),
        "%s: %s omw/min   ·   %s Nm   ·   %s W   ·   %s A bij 48 V" % (per, nl(m["rpm"], 0), nl(m["T"]),
                                                                    nl(m["P_el"], 0), nl(m["I"])),
        "verplaatst materiaal: %s kg" % nl(m["moved"]),
    ]


def profile_panel(draw, m, small, x0, y0, w=300, h=120, vmax=12.0):
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 225))
    draw.text((x0 + 10, y0 + 5), "na de borstels, over de breedte (kg/m²)", fill=TEXT, font=small)
    prof = m["profile"]
    n = len(prof)
    top, bot = y0 + 26, y0 + h - 22
    bw = (w - 20) / float(n)
    for i, b in enumerate(prof):
        hgt = (bot - top) * min(1.0, b / vmax)
        bx = x0 + 10 + i * bw
        draw.rectangle((bx, bot - hgt, bx + bw - 0.8, bot), fill=BAR)
    draw.line((x0 + 10, bot, x0 + w - 10, bot), fill=(120, 120, 120, 255), width=1)
    for xm, label, anchor in ((-1.5, "-1,5 m", "la"), (0.0, "midden", "ma"), (1.5, "+1,5 m", "ra")):
        px = x0 + 10 + (xm + 1.5) / 3.0 * (w - 20)
        draw.line((px, bot, px, bot + 4), fill=GREY, width=1)
        draw.text((px, bot + 5), label, fill=GREY, font=small, anchor=anchor)
    for xw in (-0.375, 0.375):                     # wielsporen (hart band)
        px = x0 + 10 + (xw + 1.5) / 3.0 * (w - 20)
        draw.line((px, top, px, bot), fill=(150, 150, 150, 160), width=1)
    draw.text((x0 + w - 10, y0 + 5), "| = wielspoor", fill=GREY, font=small, anchor="ra")


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
    profile_panel(draw, m, small, image.width - 310, image.height - 130)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=10, last_hold_ms=2200, overlay=True):
    """overlay=False: alleen de 3D-beelden, zonder bijschrift en paneel."""
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
    main(args[0], args[1], int(args[2]) if len(args) > 2 else 10, overlay="--clean" not in sys.argv)
