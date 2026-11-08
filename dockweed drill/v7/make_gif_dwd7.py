"""Turn the frames of animate_dwd7 into a GIF with a caption, a steering panel and a wheel-load panel.

Runs in FreeCAD's Python (Pillow is included) or in a plain Python with Pillow:
    python make_gif_dwd7.py <frame_folder> <out.gif> [fps]
(Different name than make_gif.py in "agbot design", because that folder is also on sys.path for the animation.)
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
WHEEL_RANGE = (0.0, 120.0)      # kg
WHEELS = ("FL", "FR", "RL", "RR")
STEER_MAX = 30.0                # deg, robot_steer_max_deg


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _z(v):
    """Round tiny values to 0.0 so the caption never shows "-0.0"."""
    return v if abs(v) >= 0.05 else 0.0


def caption(m, speedup):
    spindle = "spindle %d rpm · %d W · %.1f A" % (m["rpm"], m["power"], m["current"]) if m["rpm"] else "spindle stopped"
    pot = "can on the sward" if m["pot_on_ground"] else "can hanging"
    depth = "depth %d mm" % m["depth"] if m["depth"] > 0 else "cutter above ground"
    act = "LA36 %.1f A" % m["act_a"] if m["act_a"] > 0 else "LA36 idle"
    if m["phase"] in ("drive", "away"):
        where = "spindle %+d mm beside the plant, %d mm to go" % (m["off_x"], max(0, m["to_go"])) \
            if m["phase"] == "drive" else "spindle x %+d mm" % m["spindle_x"]
        line3 = "%s · steering %+.1f° · heading %+.1f°" % (where, _z(m["steer"]), _z(m["heading"]))
    else:
        line3 = "Z %+d mm · %s · %s · spindle on the plant (%+d mm)" % (m["z"], depth, pot, m["off_x"])
    return [
        m["text"],
        "plant %d/%d · done %d · t %.1f s (%dx speed)" % (m["plant"], m["n_plants"], m["done"], m["t"], speedup),
        line3,
        "%s · Z force %d N · %s" % (spindle, m["fz"], act),
    ]


def wheel_panel(draw, m, small, x0, y0):
    w, h = 250, 132
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 220))
    draw.text((x0 + 10, y0 + 6), "robot wheel load (kg)", fill=(30, 30, 30, 255), font=small)
    lo, hi = WHEEL_RANGE
    top, bot = y0 + 30, y0 + h - 24

    def zy(v):
        v = max(lo, min(hi, v))
        return bot - (v - lo) / (hi - lo) * (bot - top)
    slot_w = (w - 20) / len(WHEELS)
    for i, name in enumerate(WHEELS):
        v = m["wheels"][name]
        cx = x0 + 10 + slot_w * (i + 0.5)
        color = (40, 120, 200, 255) if name[0] == "F" else (225, 110, 25, 255)
        if v < 20.0:
            color = (200, 40, 40, 255)
        draw.rectangle((cx - 12, zy(v), cx + 12, bot), fill=color)
        draw.text((cx, bot + 2), name, fill=(60, 60, 60, 255), font=small, anchor="mt")
        draw.text((cx, zy(v) - 2), "%.0f" % v, fill=(40, 40, 40, 255), font=small, anchor="mb")


def steer_panel(draw, m, small, x0, y0):
    """Front wheel angles (left, right) as bars from the middle, scale +-30 deg (+ = left)."""
    w, h = 250, 74
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 220))
    draw.text((x0 + 10, y0 + 6), "front wheel steering (° , + = left)", fill=(30, 30, 30, 255), font=small)
    mid = x0 + w / 2
    half = (w - 70) / 2
    for k, (name, key) in enumerate((("FL", "steer_l"), ("FR", "steer_r"))):
        y = y0 + 30 + k * 20
        v = m[key] + 0.0 if abs(m[key]) >= 0.05 else 0.0          # no "-0.0"
        draw.text((x0 + 10, y - 2), name, fill=(60, 60, 60, 255), font=small)
        draw.rectangle((mid - half, y + 4, mid + half, y + 10), fill=(225, 225, 225, 255))
        end = mid - max(-1.0, min(1.0, v / STEER_MAX)) * half          # + = left: bar to the left
        color = (200, 40, 40, 255) if abs(v) > STEER_MAX - 0.5 else (60, 140, 60, 255)
        draw.rectangle((min(mid, end), y + 2, max(mid, end), y + 12), fill=color)
        draw.line((mid, y, mid, y + 14), fill=(80, 80, 80, 255), width=1)
        draw.text((x0 + w - 10, y - 2), "%+.1f" % v, fill=(40, 40, 40, 255), font=small, anchor="ra")


def decorate(image, m, font, small, speedup):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = caption(m, speedup)
    pad = 8
    line_h = font.size + 5
    width = max(draw.textlength(line, font=font) for line in lines) + 2 * pad
    draw.rounded_rectangle((10, 10, 10 + width, 10 + line_h * len(lines) + 2 * pad - 4), radius=8,
                           fill=(255, 255, 255, 215))
    for i, line in enumerate(lines):
        draw.text((10 + pad, 10 + pad + i * line_h), line, fill=(30, 30, 30, 255), font=font)
    wheel_panel(draw, m, small, image.width - 262, image.height - 144)
    steer_panel(draw, m, small, image.width - 262, image.height - 226)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=12, last_hold_ms=1500, sim_dt=0.25, text=True):
    """text=False: the bare frames, without caption and panels."""
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    if text:
        with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
            metas = json.load(handle)
        font = load_font(14)
        small = load_font(13)
        speedup = int(round(sim_dt * fps))
        images = [decorate(Image.open(os.path.join(folder, n)), metas[int(n[6:10])], font, small, speedup)
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
    _to_animations(out_path)
    print("%d frames -> %s (%.2f MB)" % (len(frames), out_path, os.path.getsize(out_path) / 1e6))
    return out_path


def label_frame(image, text, font):
    """Exploded animation: one label line at the bottom (the part that is being placed)."""
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    pad = 8
    w = draw.textlength(text, font=font) + 2 * pad
    y1 = image.height - 12
    y0 = y1 - font.size - 2 * pad + 2
    draw.rounded_rectangle((12, y0, 12 + w, y1), radius=8, fill=(255, 255, 255, 225))
    draw.text((12 + pad, y0 + pad - 2), text, fill=(30, 30, 30, 255), font=font)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main_explode(folder, out_path, fps=12, last_hold_ms=2000, text=True):
    """Frames of explode_dwd7 to a GIF; text=True puts the name of the step at the bottom."""
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    font = load_font(16)
    images = []
    for n in names:
        im = Image.open(os.path.join(folder, n)).convert("RGB")
        images.append(label_frame(im, metas[int(n[6:10])]["label"], font) if text else im)
    sample = [images[i] for i in range(0, len(images), max(1, len(images) // 16))]
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
    args = [a for a in sys.argv[1:] if a != "--no-text"]
    main(args[0], args[1], int(args[2]) if len(args) > 2 else 12, text="--no-text" not in sys.argv)
