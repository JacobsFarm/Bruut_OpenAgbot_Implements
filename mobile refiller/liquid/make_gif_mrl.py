"""Turns the frames of animate_mrl into a GIF with a caption, tank gauges (work tank, refiller tank, trailer tank,
pump flow) and a small map of the headland seen from above.

Works in the Python of FreeCAD (Pillow is included) or in a normal Python with Pillow:
    python make_gif_mrl.py <folder_with_frames> <out.gif> [fps] [--clean]     (--clean: no text in the image)
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (90, 92, 96, 255)
BLUE = (38, 128, 204, 255)
ORANGE = (230, 110, 30, 255)
PANEL = (255, 255, 255, 220)


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def caption(m, speed):
    return ["Mobile refiller: topping up the working robot in the straight part of its turn",
            "t %.1f s (%g x speed)   ·   dose %d l/ha, field %d m: 2 passes used %.0f l" % (
                m["t"], speed, m["dose"], m["field_len"], m["need"]),
            "working robot: %s (%.2f m/s)" % (m["w_text"], abs(m["v_w"]) / 1000.0),
            "refiller: %s" % m["r_text"]]


def gauge(draw, x, y, w, h, value, cap, label, small, color=BLUE, mark=None):
    draw.rectangle((x, y, x + w, y + h), outline=(120, 120, 125, 255), fill=(240, 242, 245, 255))
    f = max(0.0, min(1.0, value / cap))
    draw.rectangle((x + 1, y + h - (h - 2) * f, x + w - 1, y + h - 1), fill=color)
    if mark is not None:
        ym = y + h - (h - 2) * mark / cap
        draw.line((x - 3, ym, x + w + 3, ym), fill=(200, 40, 40, 255), width=1)
    draw.text((x + w / 2.0, y + h + 3), label, fill=TEXT, font=small, anchor="ma")
    draw.text((x + w / 2.0, y - 3), "%.0f l" % value, fill=TEXT, font=small, anchor="md")


def tank_panel(draw, m, small, x0, y0, w=250, h=118):
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=PANEL)
    gx = x0 + 22
    top = y0 + 26
    gh = h - 56
    gauge(draw, gx, top, 30, gh, m["rx"], m["rx_cap"], "work tank", small, mark=m["rx_full"])
    gauge(draw, gx + 70, top, 30, gh, m["mr"], m["mr_cap"], "refiller", small)
    gauge(draw, gx + 140, top, 30, gh, m["tr"], m["tr_cap"], "trailer", small)
    px = x0 + w - 30
    on = m["pump_lpm"] > 0
    draw.ellipse((px - 11, top + 6, px + 11, top + 28), fill=BLUE if on else (205, 205, 210, 255),
                 outline=(90, 90, 95, 255))
    draw.text((px, top + 34), "pump", fill=TEXT, font=small, anchor="ma")
    draw.text((px, top + 48), "%d l/min" % m["pump_lpm"] if on else "off", fill=TEXT, font=small, anchor="ma")
    if on and abs(m["lag"]) > 1.0:
        draw.text((x0 + 10, y0 + h - 15), "refiller lags %.0f mm: the boom follows, spout on the funnel" % abs(m["lag"]),
                  fill=GREY, font=small)


def map_panel(draw, m, small, x0, y0, w=250, h=150):
    """Headland seen from above: field edge, fence, paths, both robots."""
    pl = m["plan"]
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=PANEL)
    xmin, xmax = -3200.0, 7600.0
    ymin, ymax = -2500.0, pl["fence"] + 300.0
    sc = min((w - 20) / (xmax - xmin), (h - 28) / (ymax - ymin))

    def p(x, y):
        return x0 + 10 + (x - xmin) * sc, y0 + h - 8 - (y - ymin) * sc
    fx = p(xmin, ymin)
    draw.rectangle((fx[0], p(xmin, 0)[1], p(xmax, 0)[0], fx[1]), fill=(170, 200, 140, 255))
    draw.line((p(xmin, 0), p(xmax, 0)), fill=(255, 255, 255, 255), width=2)
    draw.line((p(xmin, pl["fence"]), p(xmax, pl["fence"])), fill=(140, 100, 60, 255), width=2)
    # planned path of the working robot (rear axle)
    pts = [p(pl["x_a"], ymin), p(pl["x_a"], pl["y_turn"])]
    for i in range(1, 19):
        a = math.radians(180.0 - 90.0 * i / 18.0)
        pts.append(p(pl["x_a"] + pl["r"] + pl["r"] * math.cos(a), pl["y_turn"] + pl["r"] * math.sin(a)))
    pts.append(p(pl["x_b"] - pl["r"], pl["ys"]))
    for i in range(1, 19):
        a = math.radians(90.0 - 90.0 * i / 18.0)
        pts.append(p(pl["x_b"] - pl["r"] + pl["r"] * math.cos(a), pl["y_turn"] + pl["r"] * math.sin(a)))
    pts.append(p(pl["x_b"], ymin))
    draw.line(pts, fill=(120, 120, 120, 255), width=1)
    # robots as rectangles
    def robot(cx, cy, psi, color, length=1430.0, width=980.0):
        a = math.radians(psi)
        hx, hy = -math.sin(a), math.cos(a)
        rx, ry = hy, -hx
        corners = [(cx + sx * width / 2.0 * rx + sy * length / 2.0 * hx, cy + sx * width / 2.0 * ry + sy * length / 2.0 * hy)
                   for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        draw.polygon([p(*c) for c in corners], fill=color)
        nose = p(cx + hx * length / 2.0, cy + hy * length / 2.0)
        draw.ellipse((nose[0] - 2, nose[1] - 2, nose[0] + 2, nose[1] + 2), fill=(30, 30, 30, 255))
    wx, wy, psi = m["w_pos"]
    robot(wx, wy, psi, ORANGE)
    rx, ry = m["r_pos"]
    robot(rx + 2280.0 - 200.0, ry, 90.0, (90, 140, 200, 255), length=1200.0)     # trailer behind (+x)
    robot(rx, ry, 90.0, BLUE)
    draw.text((x0 + 10, y0 + 5), "from above: field edge, headland, fence", fill=GREY, font=small)


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
    tank_panel(draw, m, small, 10, image.height - 128)
    map_panel(draw, m, small, image.width - 260, image.height - 160)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=10, last_hold_ms=2500, overlay=True, frame_fps=5):
    """overlay=False: only the 3D images, without caption and panels. frame_fps = real-time rate of the frames."""
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
