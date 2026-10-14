"""Turns the frames of animate_mrs into a GIF with a caption, tank gauges (work tank, IBC, pump) and a map of the
field seen from above (passes, which ones are done, the U-turn, both robots). Also draws the field pattern diagram
(pattern_png).

Works in the Python of FreeCAD (Pillow is included) or in a normal Python with Pillow:
    python make_gif_mrs.py <folder_with_frames> <out.gif> [fps] [--clean]     (--clean: no text in the image)
    python make_gif_mrs.py --pattern previews/pattern_skip_passes.png
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

try:
    import mrs_calc as C
    import mrs_params as P
except ImportError:                                  # run from another folder
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mrs_calc as C
    import mrs_params as P

FONT_PATHS = (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf")
TEXT = (30, 30, 30, 255)
GREY = (90, 92, 96, 255)
LIGHT = (175, 178, 182, 255)
BLUE = (38, 128, 204, 255)
ORANGE = (230, 110, 30, 255)
BROWN = (95, 62, 35, 255)
PANEL = (255, 255, 255, 220)
FIELD = (170, 200, 140, 255)
HEADLAND = (205, 220, 180, 255)


def load_font(size, bold=False):
    paths = (r"C:\Windows\Fonts\segoeuib.ttf",) + FONT_PATHS if bold else FONT_PATHS
    for path in paths:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def clock(t):
    return "%d:%04.1f" % (int(t // 60), t % 60)


def caption(m, speed):
    order = ", ".join(str(p) for p in m["plan"]["order"][:8])
    lines = ["Mobile refiller (IBC): top-up in the middle of the U-turn, the refiller stays on the headland",
             "t %s (%g x speed)  ·  order %s, ...: every turn a U-turn  ·  %d l/ha, field %d m: 2 passes = %.0f l" % (
                 clock(m["t"]), speed, order, m["dose"], m["field_len"], m["need"])]
    if m["skip"]:
        lines += [m["skip_text"], "refiller: %s" % m["r_text"]]
    else:
        lines += ["working robot: %s (%.2f m/s)" % (m["w_text"], abs(m["v_w"]) / 1000.0), "refiller: %s" % m["r_text"]]
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


def tank_panel(draw, m, small, x0, y0, w=200, h=118):
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=PANEL)
    gx = x0 + 22
    top = y0 + 26
    gh = h - 56
    gauge(draw, gx, top, 30, gh, m["rx"], m["rx_cap"], "work tank", small, mark=m["rx_full"])
    gauge(draw, gx + 70, top, 30, gh, m["ibc"], m["ibc_cap"], "IBC", small)
    px = x0 + w - 32
    on = m["pump_lpm"] > 0
    draw.ellipse((px - 11, top + 6, px + 11, top + 28), fill=BLUE if on else (205, 205, 210, 255),
                 outline=(90, 90, 95, 255))
    draw.text((px, top + 34), "pump", fill=TEXT, font=small, anchor="ma")
    draw.text((px, top + 48), "%d l/min" % m["pump_lpm"] if on else "off", fill=TEXT, font=small, anchor="ma")


def _rect(cx, cy, psi, length, width, y0=None):
    """Corners of a rectangle with its centre (or rear at y0 along the heading) at cx, cy."""
    a = math.radians(psi)
    hx, hy = -math.sin(a), math.cos(a)
    rx, ry = hy, -hx
    lo, hi = (-length / 2.0, length / 2.0) if y0 is None else (y0, y0 + length)
    return [(cx + sx * width / 2.0 * rx + sy * hx, cy + sx * width / 2.0 * ry + sy * hy)
            for sx, sy in ((-1, lo), (1, lo), (1, hi), (-1, hi))]


def map_panel(draw, m, small, x0, y0, w=300, h=165):
    """Field seen from above: passes (done / not yet), the U-turn, both robots."""
    pl = m["plan"]
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=PANEL)
    n = pl["passes"]
    xmin, xmax = -1300.0, (n - 1) * pl["w"] + 1300.0
    ymin, ymax = -2800.0, pl["fence"] + 200.0
    sc = min((w - 20) / (xmax - xmin), (h - 40) / (ymax - ymin))
    ox = x0 + (w - (xmax - xmin) * sc) / 2.0

    def p(x, y):
        return ox + (x - xmin) * sc, y0 + h - 22 - (y - ymin) * sc
    draw.rectangle((*p(xmin, 0), *p(xmax, ymin)), fill=FIELD)
    draw.rectangle((*p(xmin, ymax), *p(xmax, 0)), fill=HEADLAND)
    draw.line((p(xmin, 0), p(xmax, 0)), fill=(255, 255, 255, 255), width=2)
    draw.line((p(xmin, pl["fence"]), p(xmax, pl["fence"])), fill=(140, 100, 60, 255), width=2)
    for k in range(1, n + 1):
        x = (k - 1) * pl["w"]
        s = m["slots"].get(str(k))
        draw.line((p(x, ymin), p(x, 0)), fill=LIGHT, width=1)
        if s:
            lo, hi = sorted(s)
            draw.line((p(x, max(lo, ymin)), p(x, min(hi, 0))), fill=BROWN, width=3)
        draw.text((p(x, ymin)[0], p(x, ymin)[1] + 2), str(k), fill=GREY, font=small, anchor="ma")
    pa, pb = m.get("path_pair", m["pair"])
    pts, _ = C.u_turn_points((pa - 1) * pl["w"], (pb - 1) * pl["w"], y_in=-300.0, y_out=-300.0, step=100.0)
    draw.line([p(*q) for q in pts], fill=(110, 110, 110, 255), width=1)
    rx, ry = m["r_pos"]
    draw.polygon([p(*c) for c in _rect(rx - 120.0, ry, -90.0, 1000.0, 1200.0)], fill=BLUE)
    draw.line((p(rx, ry + 600.0), p(rx, ry + P.dock_d)), fill=(30, 60, 110, 255), width=2)
    wx, wy, psi = m["w_pos"]
    draw.polygon([p(*c) for c in _rect(wx, wy, psi, 1430.0, 1000.0)], fill=ORANGE)
    draw.text((x0 + 10, y0 + 5), "from above: passes 1-%d, done = brown" % n, fill=GREY, font=small)


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
    map_panel(draw, m, small, image.width - 310, image.height - 175)
    if m["skip"]:
        big = load_font(22, bold=True)
        txt = "... %s later ..." % m["skip_text"].split(":")[0].replace("time skip ", "")
        tw = draw.textlength(txt, font=big)
        draw.rounded_rectangle(((image.width - tw) / 2 - 12, 150, (image.width + tw) / 2 + 12, 186), radius=8,
                               fill=(255, 255, 255, 230))
        draw.text((image.width / 2.0, 168), txt, fill=TEXT, font=big, anchor="mm")
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def main(folder, out_path, fps=10, last_hold_ms=2500, overlay=True, frame_fps=5, step=2):
    """overlay=False: only the 3D images, without caption and panels. frame_fps = real-time rate of the frames.
    step: use every step-th frame (and fps / step, so the speed stays the same) to keep the file small."""
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        metas = json.load(handle)
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    names = [n for i, n in enumerate(names) if i % step == 0 or metas[int(n[6:10])]["skip"] or i == len(names) - 1]
    font = load_font(13)
    small = load_font(10)
    speed = fps / float(frame_fps)
    fps = fps / float(step)
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
    for i, n in enumerate(names):
        if metas[int(n[6:10])]["skip"]:
            durations[i] = 250                       # the time skip: a bit slower
    durations[-1] = last_hold_ms
    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=False)
    print("%d frames -> %s (%.2f MB)" % (len(frames), out_path, os.path.getsize(out_path) / 1e6))
    return out_path


# ---------------------------------------------------------------------
# Field pattern diagram
# ---------------------------------------------------------------------
def pattern_png(out_path, blocks=2, px_m=46.0, field_m=5.0):
    """Two blocks of 2N passes: the order, the U-turns on both headlands, where the refiller stands for every refill
    (inside the turn, nozzle above the straight) and how far it moves."""
    n = C.skip_n()
    order = C.field_order(blocks, n)
    turns = C.turns(order)
    n_pass = 2 * n * blocks
    wm = C.WORK_WIDTH / 1000.0
    head = C.headland_depth()
    margin = 2.6
    width_m = (n_pass - 1) * wm + 2 * margin
    height_m = 2 * head + field_m
    top_px, left_px = 118, 30
    img = Image.new("RGB", (int(width_m * px_m + 2 * left_px), int(height_m * px_m + top_px + 150)), "white")
    d = ImageDraw.Draw(img)
    title = load_font(22, bold=True)
    font = load_font(15)
    small = load_font(12)
    tiny = load_font(11)

    # field y (m): far headland bottom ... refiller headland top. Pass k at x = (k - 1) wm.
    def p(x_m, y_m):
        return left_px + (x_m + margin) * px_m, top_px + (head + field_m - y_m) * px_m

    d.text((left_px, 14), "Skip pattern: every turn a U-turn, the refiller stays inside the turn", fill=TEXT,
           font=title)
    d.text((left_px, 48), "Order %s, ...  (+%d / -%d passes; every other block mirrored so the block change is a U-turn "
           "too)" % (", ".join(str(k) for k in order[:2 * n + 4]), n, n - 1), fill=GREY, font=font)
    d.text((left_px, 72), "Refiller headland: always U-turns of %d m (arc R %.1f m, %.1f m straight, arc). Far headland: "
           "%d m in odd blocks, %d m in even blocks. The refiller moves 1 m per refill, %d m at a block change." % (
               n, C.R_TURN / 1000.0, n - 2 * C.R_TURN / 1000.0, n - 1, n + 1, n + 1), fill=GREY, font=font)
    xr = (n_pass - 1) * wm + margin
    d.rectangle((*p(-margin, head + field_m), *p(xr, field_m)), fill=HEADLAND[:3])
    d.rectangle((*p(-margin, field_m), *p(xr, 0)), fill=FIELD[:3])
    d.rectangle((*p(-margin, 0), *p(xr, -head)), fill=HEADLAND[:3])
    for y in (field_m, 0.0):
        d.line((p(-margin, y), p(xr, y)), fill=(255, 255, 255), width=3)
    d.text(p(-margin + 0.2, head + field_m - 0.25), "refiller headland", fill=GREY, font=small)
    d.text(p(-margin + 0.2, -head + 0.7), "far headland", fill=GREY, font=small)
    seq = {k: i + 1 for i, k in enumerate(order)}
    for k in range(1, n_pass + 1):
        x = (k - 1) * wm
        d.line((p(x, field_m), p(x, 0)), fill=BROWN[:3], width=3)
        up = seq[k] % 2 == 1
        ya, yb = (0.8, field_m - 0.8) if up else (field_m - 0.8, 0.8)
        xa, ya_, = p(x, ya)
        xb, yb_ = p(x, yb)
        d.polygon([(xb, yb_), (xb - 5, yb_ + (8 if up else -8)), (xb + 5, yb_ + (8 if up else -8))], fill=BROWN[:3])
        cx, cy = p(x, field_m / 2.0)
        d.ellipse((cx - 11, cy - 11, cx + 11, cy + 11), fill="white", outline=BROWN[:3])
        d.text((cx, cy), str(seq[k]), fill=TEXT, font=tiny, anchor="mm")
        d.text((p(x, -head)[0], p(x, -head)[1] + 6), str(k), fill=GREY, font=small, anchor="ma")
    d.text((p(-margin + 0.2, -head)[0], p(0, -head)[1] + 24), "pass number (bottom), order (circles)", fill=GREY,
           font=small)
    # U-turns: refiller headland at the top (y = field_m + ...), far headland at the bottom (mirrored)
    r_m = C.R_TURN / 1000.0
    yt = P.y_turn / 1000.0
    refill = 0
    for i, (a, b, hd, wdt, mid) in enumerate(turns):
        xa_, xb_ = (a - 1) * wm, (b - 1) * wm
        pts, _ = C.u_turn_points(xa_ * 1000.0, xb_ * 1000.0, y_in=0.0, y_out=0.0, step=60.0)
        if hd == "R":
            line = [p(x / 1000.0, field_m + y / 1000.0) for x, y in pts]
            d.line(line, fill=(90, 90, 95), width=1)
            refill += 1
            spot = C.refill_spot(xa_ * 1000.0, xb_ * 1000.0)
            nx, ny = spot["xc"] / 1000.0, field_m + C.YS / 1000.0
            rc = p(spot["xc"] / 1000.0, field_m + spot["yc"] / 1000.0)
            if refill in (1, 2, n + 1):
                poly = [p(x / 1000.0, field_m + y / 1000.0) for x, y in _rect(
                    spot["xc"] + P.IBC_CY, spot["yc"], -90.0, 1000.0, 1200.0)]
                d.polygon(poly, fill=(38, 128, 204) if refill == 1 else (150, 190, 230), outline=(30, 60, 110))
                d.line((rc, p(nx, ny)), fill=(30, 60, 110), width=2)
            d.ellipse((p(nx, ny)[0] - 4, p(nx, ny)[1] - 4, p(nx, ny)[0] + 4, p(nx, ny)[1] + 4), fill=BLUE[:3])
            d.text((p(nx, ny)[0], p(nx, ny)[1] - 7), str(refill), fill=(30, 60, 110), font=tiny, anchor="md")
        else:
            line = [p(x / 1000.0, -y / 1000.0) for x, y in pts]
            change = (i + 1) % (2 * n) == 0
            d.line(line, fill=(200, 60, 40) if change else (90, 90, 95), width=3 if change else 1)
    # moves of the refiller
    s1 = C.refill_spot(0.0, n * C.WORK_WIDTH)
    s2 = C.refill_spot(C.WORK_WIDTH, (n + 1) * C.WORK_WIDTH)
    ya = field_m + s1["yc"] / 1000.0 - 1.2
    d.line((p(s1["xc"] / 1000.0, ya), p(s2["xc"] / 1000.0, ya)), fill=(30, 60, 110), width=2)
    d.text(p(s2["xc"] / 1000.0 + 0.15, ya + 0.15), "+1 m per refill", fill=(30, 60, 110), font=small)
    leg_y = img.height - 62
    d.ellipse((left_px, leg_y, left_px + 10, leg_y + 10), fill=BLUE[:3])
    d.text((left_px + 16, leg_y - 3), "nozzle = where the working robot stops its funnel (numbered: refill 1, 2, ...); "
           "blue block = the refiller with the IBC, its arm reaches over the straight", fill=TEXT, font=small)
    d.line((left_px, leg_y + 30, left_px + 30, leg_y + 30), fill=(200, 60, 40), width=2)
    d.text((left_px + 38, leg_y + 22), "block change on the far headland (%d m U-turn)" % (n + 1), fill=TEXT, font=small)
    img.save(out_path)
    print("pattern ->", out_path)
    return out_path


if __name__ == "__main__":
    if "--pattern" in sys.argv:
        pattern_png(sys.argv[sys.argv.index("--pattern") + 1])
    else:
        args = [a for a in sys.argv[1:] if a != "--clean"]
        main(args[0], args[1], int(args[2]) if len(args) > 2 else 10, overlay="--clean" not in sys.argv)
