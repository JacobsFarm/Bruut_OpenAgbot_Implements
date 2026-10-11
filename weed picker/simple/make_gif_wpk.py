"""Turns the frames of animate_wpk into a GIF with a caption and a panel (electric power of the two rotors against the
motor limit, and the driving speed over time).

Works in FreeCAD's Python (Pillow is included) or in a normal Python with Pillow:
    python make_gif_wpk.py <folder_with_frames> <out.gif> [fps] [--clean]     (--clean: no text in the picture)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (90, 92, 96, 255)
POWER = (40, 90, 190, 255)
SPEED = (225, 110, 25, 255)
LIMIT = (190, 40, 40, 200)


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def caption(m):
    state = "raising the deck" if m["raising"] else ("topping" if m["n_cut"] else "driving into the patch")
    return [
        "Weed picker: twin-rotor topper, the cut weeds go into one windrow",
        "%s   ·   %.2f m/s   ·   %.1f m   ·   cut height %.0f mm" % (state, m["v"] / 1000.0, m["dist"] / 1000.0,
                                                                     m["cut"]),
        "rotors %d rpm   ·   ≈ %d W electric   ·   %d of %d weeds in the strip cut" % (
            m["rpm"], m["P_el"], m["n_cut"], m["n_strip"]),
        "cut %.1f kg   ·   in the windrow ≈ %.1f kg" % (m["kg_cut"], m["kg_windrow"]),
    ]


def panel(draw, metas, i, small, x0, y0, w=300, h=130, p_max=2000.0, v_max=0.6):
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 225))
    draw.text((x0 + 10, y0 + 5), "power (W)", fill=POWER, font=small)
    draw.text((x0 + w - 10, y0 + 5), "speed (m/s)", fill=SPEED, font=small, anchor="ra")
    top, bot = y0 + 26, y0 + h - 20
    left, right = x0 + 10, x0 + w - 10
    t_end = metas[-1]["t"]

    def px(t):
        return left + (right - left) * t / t_end

    for frac in (0.5, 1.0):
        yy = bot - (bot - top) * frac
        draw.line((left, yy, right, yy), fill=(225, 225, 225, 255), width=1)
        draw.text((left + 2, yy + 1), "%.0f" % (p_max * frac), fill=POWER, font=small)
        draw.text((right - 2, yy + 1), "%.1f" % (v_max * frac), fill=SPEED, font=small, anchor="ra")
    yl = bot - (bot - top) * min(1.0, metas[0]["P_limit"] / p_max)
    draw.line((left, yl, right, yl), fill=LIMIT, width=1)
    draw.text((left + 40, yl - 13), "motor limit", fill=LIMIT, font=small)
    pts_p = [(px(m["t"]), bot - (bot - top) * min(1.0, m["P_el"] / p_max)) for m in metas[:i + 1]]
    pts_v = [(px(m["t"]), bot - (bot - top) * min(1.0, m["v"] / 1000.0 / v_max)) for m in metas[:i + 1]]
    if len(pts_p) > 1:
        draw.line(pts_p, fill=POWER, width=2)
        draw.line(pts_v, fill=SPEED, width=2)
    draw.line((left, bot, right, bot), fill=(120, 120, 120, 255), width=1)
    draw.line((px(metas[i]["t"]), top, px(metas[i]["t"]), bot), fill=(150, 150, 150, 200), width=1)
    draw.text((left, bot + 3), "0 s", fill=GREY, font=small)
    draw.text((right, bot + 3), "%.0f s" % t_end, fill=GREY, font=small, anchor="ra")


def decorate(image, metas, i, font, small):
    m = metas[i]
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = caption(m)
    pad = 8
    line_h = font.size + 5
    width = max(draw.textlength(line, font=font) for line in lines) + 2 * pad
    draw.rounded_rectangle((10, 10, 10 + width, 10 + line_h * len(lines) + 2 * pad - 4), radius=8,
                           fill=(255, 255, 255, 215))
    for k, line in enumerate(lines):
        draw.text((10 + pad, 10 + pad + k * line_h), line, fill=TEXT, font=font)
    panel(draw, metas, i, small, image.width - 310, image.height - 140)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=10, last_hold_ms=2200, overlay=True):
    """overlay=False: only the 3D pictures, without caption and panel."""
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    font = load_font(15)
    small = load_font(12)
    if overlay:
        images = [decorate(Image.open(os.path.join(folder, n)), metas, int(n[6:10]), font, small) for n in names]
    else:
        images = [Image.open(os.path.join(folder, n)).convert("RGB") for n in names]
    sample = [images[k] for k in range(0, len(images), max(1, len(images) // 12))]
    sheet = Image.new("RGB", (images[0].width, images[0].height * len(sample)))
    for k, im in enumerate(sample):
        sheet.paste(im, (0, k * images[0].height))
    palette = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]
    durations = []
    previous = 0
    for k in range(len(frames)):
        current = int(round((k + 1) * 1000.0 / fps / 10.0)) * 10
        durations.append(current - previous)
        previous = current
    durations[-1] = last_hold_ms
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=False)
    print("%d frames -> %s (%.2f MB)" % (len(frames), out_path, os.path.getsize(out_path) / 1e6))
    return out_path


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--clean"]
    main(args[0], args[1], int(args[2]) if len(args) > 2 else 10, overlay="--clean" not in sys.argv)
