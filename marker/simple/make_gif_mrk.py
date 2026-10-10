"""Turns the frames of animate_mrk into a GIF with a caption and a panel of the capture window (seen from above in
robot coordinates: the window the nozzle can reach, the design point and the nozzle).

Works in the Python of FreeCAD (Pillow is included) or in a normal Python with Pillow:
    python make_gif_mrk.py <folder_with_frames> <out.gif> [fps] [--clean]     (--clean: no text in the image)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (90, 92, 96, 255)
PINK = (235, 50, 140, 255)
WINDOW = (225, 232, 240, 255)


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def caption(m, speed):
    sx, sy, zc, lift = m["stage"]
    tx, ty = m["target_rel"]
    err = m["stop_err"]
    stop = "%d mm %s" % (abs(err), "too early" if err < 0 else "too far")
    lines = ["Field marker: the robot stops roughly, the stage puts the nozzle on the point",
             "point %d/%d   ·   %s   ·   t %.1f s (%g x speed)" % (m["i"], m["n"], m["state"], m["t"], speed)]
    if m["phase"] == "drive":
        lines.append("driving %.2f m/s, robot %d mm right of the line" % (m["v"] / 1000.0, m["robot_x"]))
    else:
        lines.append("robot stopped %s, %d mm to the right  ->  stage X %+.0f, Y %.0f mm" % (stop, m["robot_x"], tx, ty))
    shroud = "shroud on the ground, lifted %.0f mm" % lift if lift > 0.5 else "shroud %.0f mm above the ground" % (
        m["shroud_bottom"])
    lines.append("nozzle %.0f mm from the point   ·   Z %.0f   ·   %s" % (m["nozzle_err"], zc, shroud))
    return lines


def window_panel(draw, m, small, x0, y0, w=300, h=130):
    """Capture window (x -400..400, y -1000..-800) with the point (cross) and the nozzle (pink circle)."""
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 225))
    draw.text((x0 + 10, y0 + 5), "capture window, from above (robot coordinates)", fill=TEXT, font=small)
    wx0, wx1, wy0, wy1 = m["window"]
    left, right, top, bot = x0 + 20, x0 + w - 20, y0 + 32, y0 + h - 30
    sc = min((right - left) / (wx1 - wx0), (bot - top) / (wy1 - wy0 + 120.0))

    def px(x, y):
        cx = (left + right) / 2.0 + x * sc
        cy = top + (wy1 + 60.0 - y) * sc
        return cx, cy
    a = px(wx0, wy1)
    b = px(wx1, wy0)
    draw.rectangle((a[0], a[1], b[0], b[1]), fill=WINDOW, outline=(150, 160, 175, 255))
    tx, ty = m["target_rel"]
    c = px(tx, ty)
    draw.line((c[0] - 7, c[1], c[0] + 7, c[1]), fill=TEXT, width=2)
    draw.line((c[0], c[1] - 7, c[0], c[1] + 7), fill=TEXT, width=2)
    sx, sy = m["stage"][0], m["stage"][1]
    n = px(sx, sy)
    r = 28.5 * sc + 2
    draw.ellipse((n[0] - r, n[1] - r, n[0] + r, n[1] + r), outline=PINK, width=2)
    front = px(0.0, wy1 + 60.0)
    draw.text((front[0], front[1] - 2), "robot (rear tyres) ^", fill=GREY, font=small, anchor="mb")
    draw.text((x0 + 10, y0 + h - 18), "+ point   o nozzle   window 800 x 200 mm", fill=GREY, font=small)


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
    if m["phase"] != "done":
        window_panel(draw, m, small, 10, image.height - 140)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=10, last_hold_ms=2500, overlay=True, frame_fps=5):
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
