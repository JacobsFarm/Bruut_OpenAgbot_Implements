"""Turns the frames of animate_ssc into a GIF. Without text by default; text=True adds a caption (phase, speed,
blocks logged, pH under the detector, samples taken) and the pH legend.

Works in the Python of FreeCAD (Pillow is included) or in a normal Python with Pillow:
    python make_gif_ssc.py <folder_with_frames> <out.gif> [fps] [--text]
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

PH_COLORS = [(0.80, 0.08, 0.08), (0.93, 0.33, 0.08), (0.98, 0.62, 0.12), (0.98, 0.88, 0.22), (0.72, 0.80, 0.50),
             (0.42, 0.52, 0.85), (0.30, 0.25, 0.72)]     # same as animate_ssc.PH_COLORS (no FreeCAD import here)


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
STATE = {"scan": "step 1: scanning, one spectrum per second (block 10 x 1.2 m)",
         "transit": "step 2: driving to the next calibration sample",
         "sample": "step 2: soil sampler takes a calibration core", "done": "map ready: scan + calibration samples"}


def load_font(size):
    for path in FONT_PATHS:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def decorate(image, m, font, small, speed):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = ["Soil scanner: gamma-ray spectrometer 0.6 m above the ground",
             "%s   ·   t %.0f s (%g x speed)" % (STATE[m["phase"]], m["t"], speed),
             "%.2f m/s   ·   blocks %d / %d   ·   samples %d / %d" % (m["v"], m["blocks"], m["n_blocks"], m["done"],
                                                                     m["n_samples"])]
    if m["ph"] is not None and m["phase"] == "scan":
        lines.append("pH under the detector %.2f" % m["ph"])
    pad, line_h = 8, font.size + 5
    width = max(draw.textlength(line, font=font) for line in lines) + 2 * pad
    draw.rounded_rectangle((10, 10, 10 + width, 10 + line_h * len(lines) + 2 * pad - 4), radius=8,
                           fill=(255, 255, 255, 215))
    for i, line in enumerate(lines):
        draw.text((10 + pad, 10 + pad + i * line_h), line, fill=TEXT, font=font)
    x0, y0 = 10, image.height - 40
    draw.rounded_rectangle((x0, y0, x0 + 300, y0 + 30), radius=6, fill=(255, 255, 255, 215))
    for i, c in enumerate(PH_COLORS):
        draw.rectangle((x0 + 40 + i * 34, y0 + 6, x0 + 72 + i * 34, y0 + 18), fill=tuple(int(v * 255) for v in c) + (255,))
    draw.text((x0 + 8, y0 + 5), "pH", fill=TEXT, font=small)
    draw.text((x0 + 40, y0 + 19), "4.4", fill=TEXT, font=small)
    draw.text((x0 + 268, y0 + 19), "5.1", fill=TEXT, font=small)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=10, last_hold_ms=3000, text=False, frame_fps=2):
    """text=False: only the 3D images. frame_fps = real-time rate of the frames (animate_ssc.FPS)."""
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    font, small = load_font(14), load_font(10)
    speed = fps / float(frame_fps)
    if text:
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
    args = [a for a in sys.argv[1:] if a != "--text"]
    main(args[0], args[1], int(args[2]) if len(args) > 2 else 10, text="--text" in sys.argv)
