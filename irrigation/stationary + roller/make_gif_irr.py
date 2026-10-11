"""Turns the frames of animate_irr into a GIF with a caption and a panel with two bars (hose on the reel, water given).

Works in the Python of FreeCAD (Pillow is included) or in a normal Python with Pillow:
    python make_gif_irr.py <folder_with_frames> <out.gif> [fps] [--clean]     (--clean: no text in the image)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (90, 92, 96, 255)
BLUE = (30, 90, 200, 255)
GREEN = (60, 110, 70, 255)
TRACK = (225, 232, 240, 255)


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def clock(seconds):
    m = int(round(seconds / 60.0))
    return "%d:%02d h" % (m // 60, m % 60)


def caption(m):
    lines = ["Irrigation hose reel: strip %d, %d m lay-flat hose, an outlet every 2 m, strips %.0f m apart"
             % (m["strip"], m["hose_len"], m["strip_w"]),
             "%s" % m["state"],
             "real time %s (this phase %.0f of %.0f min)" % (clock(m["t"]), m["t_phase"] / 60.0, m["dur"] / 60.0)]
    move = "robot %.2f m/s %s" % (abs(m["v"]), "forward" if m["v"] > 0 else "in reverse") if abs(m["v"]) > 0.01 \
        else "robot stands still"
    lines.append("hose: %.0f m on the reel (coil O%d), %.0f m in the field   ·   %s" % (m["l_reel"], m["coil_d"],
                                                                                    m["s_c"], move))
    pump = "pump on: %.1f m3/h at %.2f bar (inlet)" % (m["q"], m["h_in"] * 0.0981) if m["pump"] else "pump off"
    lines.append("%s   ·   water given %.0f of %.0f mm" % (pump, m["given"], m["gift"]))
    return lines


def bar(draw, x0, y0, w, label, frac, color, small, text):
    draw.text((x0, y0), label, fill=TEXT, font=small)
    draw.rounded_rectangle((x0, y0 + 16, x0 + w, y0 + 28), radius=5, fill=TRACK)
    if frac > 0.005:
        draw.rounded_rectangle((x0, y0 + 16, x0 + max(10, w * min(1.0, frac)), y0 + 28), radius=5, fill=color)
    draw.text((x0 + w + 8, y0 + 13), text, fill=GREY, font=small)


def panel(draw, m, small, x0, y0, w=330, h=82):
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 225))
    bar(draw, x0 + 10, y0 + 6, 220, "hose on the reel", m["l_reel"] / m["hose_len"], BLUE, small,
        "%.0f m" % m["l_reel"])
    bar(draw, x0 + 10, y0 + 42, 220, "water given on this strip", m["given"] / m["gift"], GREEN, small,
        "%.0f mm" % m["given"])


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
    panel(draw, m, small, 10, image.height - 92)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=8, last_hold_ms=2500, overlay=True):
    """overlay=False: only the 3D images, without caption and panel."""
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    font = load_font(13)
    small = load_font(11)
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
