"""Turns the frames of animate_ird into a GIF with a caption and a row panel (top view of both rows around the knives:
plants with their safe circle, the two knives of each row in red; forward = up).

Works in the Python of FreeCAD (Pillow is included) or in a normal Python with Pillow:
    python make_gif_ird.py <folder_with_frames> <out.gif> [fps] [--clean]     (--clean: no text in the image)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (120, 122, 126, 255)
GREEN = (50, 130, 60, 255)
LIGHT = (200, 230, 200, 255)
RED = (220, 40, 30, 255)
ORANGE = (240, 140, 25, 255)
SOIL = (232, 220, 205, 255)

WIN_U = (-180.0, 180.0)         # mm across (row line at 0, outwards to the right)
WIN_V = (-380.0, 520.0)         # mm along (forward = up)
SCALE = 0.17                    # px per mm


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def caption(m, speed):
    th = m["theta"]
    state = "driving %.1f m/s" % (m["v"] / 1000.0) if m["v"] > 0 else "stopped"
    lines = ["In-row weeder, double arms: two knives per row swing out to both sides around every plant",
             "%s   ·   t %.1f s (%g x speed)   ·   %.2f m driven" % (state, m["t"], speed, m["driven_m"]),
             "arms left %.0f° / %.0f°, right %.0f° / %.0f°  (outer / inner; 23° = in, 3° = out)" % (
                 th["left_outer"], th["left_inner"], th["right_outer"], th["right_inner"]),
             "%d plants passed, none touched (safe zone Ø100)   ·   %d weed seedlings hoed out" % (
                 m["plants_passed"], m["killed"])]
    return lines


def _pt(x0, y0, u, v, flip):
    """Panel point for (u, v); flip: the left row is drawn mirrored (outwards = to the left)."""
    if flip:
        px = x0 + (WIN_U[1] - u) * SCALE
    else:
        px = x0 + (u - WIN_U[0]) * SCALE
    py = y0 + (WIN_V[1] - v) * SCALE
    return px, py


def row_box(draw, small, x0, y0, row, flip, title):
    w = (WIN_U[1] - WIN_U[0]) * SCALE
    h = (WIN_V[1] - WIN_V[0]) * SCALE
    draw.rectangle((x0, y0, x0 + w, y0 + h), fill=SOIL, outline=GREY)
    rx, _ = _pt(x0, y0, 0.0, 0.0, flip)
    draw.line((rx, y0, rx, y0 + h), fill=GREY, width=1)
    for (u, v) in row["plants"]:
        if not (WIN_V[0] - 60 < v < WIN_V[1] + 60):
            continue
        px, py = _pt(x0, y0, u, v, flip)
        r = 50.0 * SCALE
        draw.ellipse((px - r, py - r, px + r, py + r), outline=GREEN, width=1)
        r2 = 4.0
        draw.ellipse((px - r2, py - r2, px + r2, py + r2), fill=GREEN)
    for kn in row["knives"]:
        draw.polygon([_pt(x0, y0, u, v, flip) for (u, v) in kn], fill=RED)
    draw.text((x0 + 2, y0 + h + 2), title, fill=TEXT, font=small)
    return w, h


def panel(draw, m, small, x0, y0):
    w = (WIN_U[1] - WIN_U[0]) * SCALE
    h = (WIN_V[1] - WIN_V[0]) * SCALE
    pw = 2 * w + 40
    draw.rounded_rectangle((x0, y0, x0 + pw, y0 + h + 40), radius=8, fill=(255, 255, 255, 225))
    draw.text((x0 + 8, y0 + 3), "from above, forward = up", fill=TEXT, font=small)
    row_box(draw, small, x0 + 12, y0 + 20, m["rows"]["left"], True, "left row")
    row_box(draw, small, x0 + 28 + w, y0 + 20, m["rows"]["right"], False, "right row")


def legend(draw, small, x0, y0):
    items = (((250, 210, 50, 255), "camera image on the ground"), (ORANGE, "plant detected (safe zone)"),
             ((85, 60, 38, 255), "soil hoed by a knife"), ((158, 140, 76, 255), "seedling hoed out"))
    w = 205
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
    h = (WIN_V[1] - WIN_V[0]) * SCALE
    panel(draw, m, small, 10, image.height - h - 50)
    legend(draw, small, image.width - 215, image.height - 92)
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
