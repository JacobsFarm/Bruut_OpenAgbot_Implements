"""Turns the frames of animate_brk into a GIF with a caption and a drive panel (belt motor power, side force on the
robot, castor lift).

Works in the Python of FreeCAD (Pillow is included) or in a normal Python with Pillow:
    python make_gif_brk.py <folder_with_frames> <out.gif> [fps] [--clean]     (--clean: no text in the image)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (205, 208, 212, 255)
BLUE = (40, 100, 230, 255)
ORANGE = (240, 140, 25, 255)
GREEN = (60, 150, 70, 255)
TAN = (189, 168, 102, 255)


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def caption(m, speed):
    return ["Electric belt rake: moss and thatch carried to the left into one windrow (outside -> inside)",
            "%s   ·   robot %.1f m/s, belt %.1f m/s   ·   t %.1f s (%g x speed)" % (
                m["state"], m["v"] / 1000.0, m["u"] / 1000.0, m["t"], speed),
            "%.2f kg of litter in the new windrow (incl. the previous pass's windrow)   ·   %.1f m driven" % (
                m["moved_kg"], m["driven_m"])]


def bar(draw, small, x0, y0, label, value, vmax, unit, color, w=150):
    draw.text((x0, y0), label, fill=TEXT, font=small)
    draw.rectangle((x0 + 95, y0 + 3, x0 + 95 + w, y0 + 13), fill=GREY)
    f = max(0.0, min(1.0, value / vmax)) if vmax > 0 else 0.0
    draw.rectangle((x0 + 95, y0 + 3, x0 + 95 + w * f, y0 + 13), fill=color)
    draw.text((x0 + 100 + w, y0), "%.0f %s" % (value, unit), fill=TEXT, font=small)


def panel(draw, m, small, x0, y0):
    w, h = 320, 76
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 225))
    bar(draw, small, x0 + 10, y0 + 8, "belt motor", m["P_el"], 750.0, "W", BLUE)
    bar(draw, small, x0 + 10, y0 + 30, "side force", m["side_N"], 400.0, "N", ORANGE)
    bar(draw, small, x0 + 10, y0 + 52, "castor lift", m["lift"], 150.0, "mm", GREEN)


def legend(draw, small, x0, y0):
    items = ((TAN, "litter, windrow"), (ORANGE, "litter on the move (tines)"))
    w = 190
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + 18 * len(items) + 10), radius=8, fill=(255, 255, 255, 215))
    for i, (c, t) in enumerate(items):
        y = y0 + 7 + 18 * i
        draw.rectangle((x0 + 10, y + 3, x0 + 22, y + 13), fill=c)
        draw.text((x0 + 30, y), t, fill=TEXT, font=small)


def decorate(image, m, font, small, speed):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = caption(m, speed)
    pad = 8
    line_h = font.size + 5
    width = max(draw.textlength(line, font=font) for line in lines) + 2 * pad
    draw.rounded_rectangle((10, 10, 10 + width, 10 + line_h * len(lines) + 2 * pad - 4), radius=8,
                           fill=(255, 255, 255, 215))
    for i, line in enumerate(lines):
        draw.text((10 + pad, 10 + pad + i * line_h), line, fill=TEXT, font=font)
    panel(draw, m, small, 10, image.height - 86)
    legend(draw, small, image.width - 200, image.height - 56)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=10, last_hold_ms=2500, overlay=True, frame_fps=10):
    """overlay=False: only the 3D images, without caption and panel. frame_fps = real-time rate of the frames."""
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    font = load_font(14)
    small = load_font(11)
    speed = fps / float(frame_fps)
    if overlay:
        images = [decorate(Image.open(os.path.join(folder, n)), metas[int(n[6:10])], font, small, speed) for n in names]
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
