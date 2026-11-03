"""Turns the frames of animate_hfw into a GIF with a caption and a legend.

Works in the Python of FreeCAD (Pillow is included) or in a normal Python with Pillow:
    python make_gif_hfw.py <folder_with_frames> <out.gif> [fps] [--clean]     (--clean: no text in the image)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont


def _to_animations(gif):
    """Also copy the GIF to <repo>/animations/ (all animations together; see collect_animations.py)."""
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isfile(os.path.join(d, "collect_animations.py")) and os.path.dirname(d) != d:
        d = os.path.dirname(d)
    if d not in sys.path:
        sys.path.insert(0, d)
    import collect_animations
    collect_animations.collect(gif)


FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (90, 92, 96, 255)
ORANGE = (240, 140, 25, 255)


def load_font(size):
    for path in FONT_PATHS:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def caption(m, speed):
    return ["Hot foam weeder: hot water (96 C) with 0.5 % foam under the flame-weeder hood, 0.4 l/m2",
            "%s   ·   %.2f m/s   ·   t %.1f s (%g x speed)" % (m["state"], m["v"] / 1000.0, m["t"], speed),
            "weeds under foam %d/%d, killed %d (2 s above ~60 C)" % (m["foamed"], m["n"], m["dead"]),
            "%.1f m2 treated: %.1f l water, %.0f g propane" % (m["m2"], m["water_l"], m["gas_g"])]


def legend(draw, small, x0, y0):
    items = (((60, 140, 40, 255), "weed"), (ORANGE, "under hot foam"), ((40, 30, 25, 255), "killed"),
             ((235, 235, 230, 255), "foam layer"))
    w = 160
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + 18 * len(items) + 10), radius=8, fill=(255, 255, 255, 215))
    for i, (c, t) in enumerate(items):
        y = y0 + 7 + 18 * i
        draw.rectangle((x0 + 10, y + 3, x0 + 22, y + 13), fill=c, outline=GREY)
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
    legend(draw, small, image.width - 170, image.height - 92)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=12, last_hold_ms=2500, overlay=True, frame_fps=2):
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
    _to_animations(out_path)
    print("%d frames -> %s (%.2f MB)" % (len(frames), out_path, os.path.getsize(out_path) / 1e6))
    return out_path


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--clean"]
    main(args[0], args[1], int(args[2]) if len(args) > 2 else 12, overlay="--clean" not in sys.argv)
