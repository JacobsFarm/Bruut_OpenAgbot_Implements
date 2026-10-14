"""Turns the frames of a refill-visit animation (stc_anim.py, via animate_<p>.py) into a GIF with a caption, a panel
with the tanks (work tank, IBCs), the pump flow, the beacon and the time at the nozzle, and a map of the headland
seen from above (station, path, working robot). Each carrier has a thin make_gif_<p>.py that calls main().

Works in the Python of FreeCAD (Pillow is included) or in a normal Python with Pillow.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (90, 92, 96, 255)
LIGHT = (175, 178, 182, 255)
BLUE = (38, 128, 204, 255)
ORANGE = (230, 110, 30, 255)
GREEN_ST = (26, 115, 64, 255)
BROWN = (95, 62, 35, 255)
PANEL = (255, 255, 255, 220)
FIELD = (170, 200, 140, 255)
HEADLAND = (205, 220, 180, 255)
LAMP = {"green": (25, 205, 65, 255), "amber": (255, 140, 15, 255)}


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def clock(t):
    return "%d:%04.1f" % (int(t // 60), t % 60)


def caption(m, gif_fps):
    pl = m["plan"]
    speed = gif_fps / float(m["fps"])
    lines = ["Stationary refill station (%s): a refill visit of the working robot on the headland" % pl["title"],
             "t %s (%g x speed)  ·  %d l/ha, field %d m: every %d passes %.0f l at %.0f l/min  ·  visit %.0f s "
             "(%.1f %% of the time, field %d m wide)" % (
                 clock(m["t"]), speed, pl["dose"], pl["field_len"], pl["passes"], pl["litres"], pl["flow"],
                 pl["visit_s"], 100.0 * pl["share"], pl["field_w"]),
             "working robot: %s (%.2f m/s)" % (m["w_text"], abs(m["v"]) / 1000.0),
             "station: %s" % m["s_text"]]
    return lines


def gauge(draw, x, y, w, h, value, cap, label, small, color=BLUE, mark=None):
    draw.rectangle((x, y, x + w, y + h), outline=(120, 120, 125, 255), fill=(240, 242, 245, 255))
    f = max(0.0, min(1.0, value / cap))
    draw.rectangle((x + 1, y + h - (h - 2) * f, x + w - 1, y + h - 1), fill=color)
    if mark is not None:
        ym = y + h - (h - 2) * mark / cap
        draw.line((x - 3, ym, x + w + 3, ym), fill=(200, 40, 40, 255), width=1)
    draw.text((x + w / 2.0, y + h + 3), label, fill=TEXT, font=small, anchor="ma")
    draw.text((x + w / 2.0, y - 3), "%.0f l" % value, fill=TEXT, font=small, anchor="md")


def tank_panel(draw, m, small, x0, y0, w=250, h=140):
    pl = m["plan"]
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=PANEL)
    gx = x0 + 20
    top = y0 + 38
    gh = h - 78
    gauge(draw, gx, top, 30, gh, m["rx"], m["rx_cap"], "work tank", small, mark=m["rx_low"])
    label = "IBC" if m["n_ibc"] == 1 else "%d IBCs" % m["n_ibc"]
    gauge(draw, gx + 64, top, 30, gh, m["ibc"], m["ibc_cap"], label, small)
    px = x0 + 150
    on = m["pump_lpm"] > 0
    draw.ellipse((px - 11, top + 2, px + 11, top + 24), fill=BLUE if on else (205, 205, 210, 255),
                 outline=(90, 90, 95, 255))
    draw.text((px, top + 28), "pump", fill=TEXT, font=small, anchor="ma")
    draw.text((px, top + 41), "%d l/min" % m["pump_lpm"] if on else "off", fill=TEXT, font=small, anchor="ma")
    bx = x0 + 212
    lit = "amber" if m["s_state"] == "pumping" else "green"
    for i, name in enumerate(("amber", "green")):
        c = LAMP[name] if name == lit else tuple(int(0.35 * v) for v in LAMP[name][:3]) + (255,)
        draw.rectangle((bx - 9, top + 2 + i * 14, bx + 9, top + 14 + i * 14), fill=c, outline=(60, 60, 60, 255))
    draw.text((bx, top + 34), "beacon", fill=TEXT, font=small, anchor="ma")
    stand = m["stand"]
    if stand is not None:
        txt = "at the nozzle %.1f s of %.1f s, %.0f l in" % (stand, pl["refill_s"], m["pumped"])
    elif m["pumped"] > 0:
        txt = "topped up: %.0f l in %.1f s" % (m["pumped"], pl["refill_s"])
    else:
        txt = "at the station: %.1f s standstill planned" % pl["refill_s"]
    draw.text((x0 + 128, y0 + h - 12), txt, fill=TEXT, font=small, anchor="ms")
    draw.text((x0 + 10, y0 + 5), "tanks, pump, beacon", fill=GREY, font=small)


def _rect(cx, cy, psi, length, width, y0=None):
    a = math.radians(psi)
    hx, hy = -math.sin(a), math.cos(a)
    rx, ry = hy, -hx
    lo, hi = (-length / 2.0, length / 2.0) if y0 is None else (y0, y0 + length)
    return [(cx + sx * width / 2.0 * rx + sy * hx, cy + sx * width / 2.0 * ry + sy * hy)
            for sx, sy in ((-1, lo), (1, lo), (1, hi), (-1, hi))]


def map_panel(draw, m, small, x0, y0, w=300, h=150):
    """Headland seen from above: field edge, passes, the station with its arm, the path and the working robot."""
    pl = m["plan"]
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=PANEL)
    xmin, xmax = min(-18500.0, pl["station_bb"][0] - 1500.0), 3500.0
    ymin, ymax = -3000.0, pl["fence"] + 300.0
    sc = min((w - 20) / (xmax - xmin), (h - 30) / (ymax - ymin))
    ox = x0 + (w - (xmax - xmin) * sc) / 2.0

    def p(x, y):
        return ox + (x - xmin) * sc, y0 + h - 8 - (y - ymin) * sc
    draw.rectangle((*p(xmin, 0), *p(xmax, ymin)), fill=FIELD)
    draw.rectangle((*p(xmin, ymax), *p(xmax, 0)), fill=HEADLAND)
    draw.line((p(xmin, 0), p(xmax, 0)), fill=(255, 255, 255, 255), width=2)
    draw.line((p(xmin, pl["fence"]), p(xmax, pl["fence"])), fill=(140, 100, 60, 255), width=2)
    for xs, s in m["slots"].items():
        x = float(xs)
        if s and xmin < x < xmax:
            lo, hi = sorted(s)
            draw.line((p(x, max(lo, ymin)), p(x, min(hi, 0))), fill=BROWN, width=2)
    draw.line([p(*q) for q in pl["path"]], fill=(110, 110, 110, 255), width=1)
    bx0, bx1, by0, by1 = pl["station_bb"]
    mx, my = pl["mast"]
    nx, ny = pl["nozzle"]
    draw.rectangle((*p(bx0, by1), *p(bx1, by0)), fill=GREEN_ST)
    draw.line((p(mx, my), p(nx, ny)), fill=(20, 70, 40, 255), width=2)
    draw.ellipse((p(nx, ny)[0] - 2, p(nx, ny)[1] - 2, p(nx, ny)[0] + 2, p(nx, ny)[1] + 2), fill=BLUE)
    wx, wy, psi = m["w_pos"]
    draw.polygon([p(*c) for c in _rect(wx, wy, psi, 2532.0, 1000.0, y0=-1767.0)], fill=ORANGE)
    draw.text((x0 + 10, y0 + 5), "from above: headland, station (green), working robot", fill=GREY, font=small)


def decorate(image, m, font, small, gif_fps):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    lines = caption(m, gif_fps)
    pad = 8
    line_h = font.size + 5
    width = max(draw.textlength(line, font=font) for line in lines) + 2 * pad
    draw.rounded_rectangle((10, 10, 10 + width, 10 + line_h * len(lines) + 2 * pad - 4), radius=8,
                           fill=(255, 255, 255, 215))
    for i, line in enumerate(lines):
        draw.text((10 + pad, 10 + pad + i * line_h), line, fill=TEXT, font=font)
    tank_panel(draw, m, small, 10, image.height - 150)
    map_panel(draw, m, small, image.width - 310, image.height - 160)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=10, last_hold_ms=2500, overlay=True):
    """fps: GIF frame rate. The frames are 2 per real second (0.5 while pumping), so 10 fps = 5 x speed (20 x while
    pumping); the caption says which."""
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    font = load_font(12)
    small = load_font(10)
    if overlay:
        images = [decorate(Image.open(os.path.join(folder, n)), metas[int(n[6:10])], font, small, fps) for n in names]
    else:
        images = [Image.open(os.path.join(folder, n)).convert("RGB") for n in names]
    sample = [images[i] for i in range(0, len(images), max(1, len(images) // 12))]
    sheet = Image.new("RGB", (images[0].width, images[0].height * len(sample)))
    for i, im in enumerate(sample):
        sheet.paste(im, (0, i * images[0].height))
    palette = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]
    durations = [int(round(1000.0 / fps))] * len(frames)
    durations[-1] = last_hold_ms
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=False)
    print("%d frames -> %s (%.2f MB)" % (len(frames), out_path, os.path.getsize(out_path) / 1e6))
    return out_path


if __name__ == "__main__":                                 # python stc_gif.py <frames> <out.gif> [fps] [--clean]
    args = [a for a in sys.argv[1:] if a != "--clean"]
    main(args[0], args[1], int(args[2]) if len(args) > 2 else 10, overlay="--clean" not in sys.argv)
