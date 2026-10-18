"""Zet de frames van animate_dwd6 om naar een GIF met bijschrift en een paneel 'wiellasten'.

Werkt in de Python van FreeCAD (Pillow zit erbij) of in een gewone Python met Pillow:
    python make_gif_dwd6.py <map_met_frames> <uit.gif> [fps]
(Andere naam dan make_gif.py in "agbot design", omdat die map voor de animatie ook op sys.path staat.)
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
WHEEL_RANGE = (0.0, 120.0)      # kg
WHEELS = ("FL", "FR", "RL", "RR")


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def nl(value, decimals=1):
    return ("%.*f" % (decimals, value)).replace(".", ",")


def caption(m, speedup):
    spindle = "spil %d rpm · %d W · %s A" % (m["rpm"], m["power"], nl(m["current"])) if m["rpm"] else "spil staat stil"
    pot = "bus op de zode" if m["pot_on_ground"] else "bus hangt"
    depth = "diepte %d mm" % m["depth"] if m["depth"] > 0 else "frees boven de grond"
    act = "actuator %s A" % nl(m["act_a"]) if m["act_a"] > 0 else "actuator staat"
    return [
        m["text"],
        "plant %d/%d · klaar %d · t %s s (%dx versneld)" % (m["plant"], m["n_plants"], m["done"], nl(m["t"]), speedup),
        "X %+d mm · Z %+d mm · %s · %s" % (m["x"], m["z"], depth, pot),
        "%s · Z-kracht %d N · %s" % (spindle, m["fz"], act),
    ]


def panel(draw, m, small, x0, y0):
    w, h = 250, 132
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=(255, 255, 255, 220))
    draw.text((x0 + 10, y0 + 6), "wiellast robot (kg)", fill=(30, 30, 30, 255), font=small)
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
        draw.text((cx, zy(v) - 2), nl(v, 0), fill=(40, 40, 40, 255), font=small, anchor="mb")


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
    panel(draw, m, small, image.width - 262, image.height - 144)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=12, last_hold_ms=1500, sim_dt=0.25):
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    font = load_font(15)
    small = load_font(13)
    speedup = int(round(sim_dt * fps))
    images = [decorate(Image.open(os.path.join(folder, n)), metas[int(n[6:10])], font, small, speedup) for n in names]

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
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12)
