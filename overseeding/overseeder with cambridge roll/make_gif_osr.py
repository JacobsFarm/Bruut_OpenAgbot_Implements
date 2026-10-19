"""Turns the frames of animate_osr into a GIF with a caption, an ON/OFF indicator of the seeder and a colour legend.

Works in the Python of FreeCAD (Pillow is included) or in a normal Python with Pillow:
    python make_gif_osr.py <folder_with_frames> <out.gif> [fps] [--clean]     (--clean: no text in the image)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (90, 92, 96, 255)
ON = (40, 160, 70, 255)
OFF = (150, 152, 156, 255)
LEGEND = [("bare soil", (13, 10, 9)), ("seed on the soil", (219, 179, 77)), ("seed pressed in", (115, 82, 43)),
          ("rolled lawn", (128, 173, 82)), ("camera strip", (140, 190, 250))]


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def caption(m, speed):
    lines = ["Overseeder + Cambridge roll: seed only where the soil is bare, the roll presses it in",
             "%s   ·   t %.1f s (%g x speed)   ·   %.2f m/s   ·   articulation %+.0f°"
             % (m["phase"], m["t"], speed, m["v"] / 1000.0, m["articulation"])]
    if m["flow"]:
        lines.append("seed falling: metering roller %.0f rpm, %d bare cells ahead" % (m["rpm"], m["ahead"]))
    elif m["motor"]:
        lines.append("motor starting / stopping, seed on its way down")
    else:
        lines.append("full grass ahead: seeder off" if not m["ahead"] else "%d bare cells ahead" % m["ahead"])
    lines.append("bare soil seeded %.0f %%   ·   rolled %.0f %%   ·   seed %.0f g   ·   draft %d N"
                 % (m["seeded_pct"], m["rolled_pct"], m["seed_g"], m["draft"]))
    return lines


def indicator(draw, m, big, small, x0, y0):
    state = m["flow"] or m["motor"]
    col = ON if state else OFF
    draw.rounded_rectangle((x0, y0, x0 + 150, y0 + 52), radius=10, fill=col)
    draw.text((x0 + 75, y0 + 18), "SEEDER " + ("ON" if state else "OFF"), fill=(255, 255, 255, 255), font=big,
              anchor="mm")
    t = m["timing"]
    draw.text((x0 + 75, y0 + 40), "on %.0f mm early, off %.0f mm early" % (t["lead_on_mm"], t["lead_off_mm"]),
              fill=(255, 255, 255, 255), font=small, anchor="mm")


def legend(draw, small, x0, y0):
    h = 16 * len(LEGEND) + 10
    draw.rounded_rectangle((x0, y0, x0 + 130, y0 + h), radius=8, fill=(255, 255, 255, 215))
    for i, (name, rgb) in enumerate(LEGEND):
        y = y0 + 6 + 16 * i
        draw.rectangle((x0 + 8, y + 2, x0 + 20, y + 12), fill=rgb + (255,), outline=(60, 60, 60, 255))
        draw.text((x0 + 26, y), name, fill=TEXT, font=small)


def decorate(image, m, font, small, big, speed):
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
    indicator(draw, m, big, small, 10, image.height - 62)
    legend(draw, small, image.width - 140, image.height - 16 * len(LEGEND) - 20)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=8, last_hold_ms=2500, overlay=True, frame_fps=4):
    """overlay=False: only the 3D images. frame_fps = real-time rate of the frames (animate_osr.FPS)."""
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    font = load_font(13)
    small = load_font(10)
    big = load_font(15, bold=True)
    speed = fps / float(frame_fps)
    if overlay:
        images = [decorate(Image.open(os.path.join(folder, n)), metas[int(n[6:10])], font, small, big, speed)
                  for n in names]
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
