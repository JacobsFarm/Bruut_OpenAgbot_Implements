"""Zet de frames van animate_fld om naar een MP4 (1280 x 720) en een GIF, met bijschrift, een kaartje van het veld,
de tankniveaus en het tempo; maakt ook de titelkaarten, een film met alle scenario's en een plaatje van de route.

Werkt in de Python van FreeCAD (Pillow en matplotlib zitten erbij) of in een gewone Python met Pillow. Voor de MP4 is
ffmpeg nodig: op het PATH, in de omgevingsvariabele FFMPEG, of via het pakket imageio-ffmpeg.

    python make_video_fld.py <map_met_frames> <scenario>          # previews/field_run_<scenario>.mp4 en .gif
                                                                    # (GIF: rond het eerste bijvullen)
    python make_video_fld.py --all <map_simple> <map_liquid> <map_station>   # previews/field_runs_all.mp4
"""
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
FONT_PATHS = {"regular": (r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf"),
              "bold": (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf")}
INK = (30, 30, 30, 255)
MUTED = (95, 95, 95, 255)
PANEL = (255, 255, 255, 222)
BLUE = (30, 100, 200, 255)
GREEN = (60, 130, 50, 255)
ORANGE = (230, 110, 20, 255)
REF_COLOR = {"simple": (230, 110, 20, 255), "liquid": (120, 70, 170, 255), "station": (40, 110, 60, 255)}
NAMES = {"simple": "IBC refiller", "liquid": "Refiller + trailer", "station": "IBC trailer"}


def font(size, weight="regular"):
    for path in FONT_PATHS[weight]:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def nl(v, d=0):
    return "%.*f" % (d, v)


def ffmpeg_exe():
    exe = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


# ---------------------------------------------------------------------
# Kaartje van het veld (bovenaanzicht)
# ---------------------------------------------------------------------
class FieldMap:
    """Bovenaanzicht, een kwartslag gedraaid: de banen liggen horizontaal (baan 1 boven), de kopakker van de refiller
    rechts, de verre kopakker links."""

    def __init__(self, plan, box):
        self.plan = plan
        x0, y0, x1, y1 = box
        self.box = box
        w, L = plan["w"], plan["len"]
        # wereldbereik: banen met kopakkers; het station staat links op de kopakker
        self.wx = (plan["station_dock_x"] - 6000.0 if plan["kind"] == "station" else -3500.0,
                   (plan["passes"] - 1) * w + 3500.0)
        self.wy = (-L - plan["ys"] - 1500.0, plan["ys"] + 3500.0)
        sx = (x1 - x0) / (self.wy[1] - self.wy[0])
        sy = (y1 - y0) / (self.wx[1] - self.wx[0])
        self.s = min(sx, sy)
        self.ox = x0 + ((x1 - x0) - self.s * (self.wy[1] - self.wy[0])) / 2.0
        self.oy = y0 + ((y1 - y0) - self.s * (self.wx[1] - self.wx[0])) / 2.0

    def p(self, x, y):
        return self.ox + (y - self.wy[0]) * self.s, self.oy + (x - self.wx[0]) * self.s

    def rect(self, draw, x0, y0, x1, y1, fill):
        a, b = self.p(x0, y0), self.p(x1, y1)
        draw.rectangle((min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])), fill=fill)

    def draw(self, draw, m, small):
        plan = self.plan
        w, L = plan["w"], plan["len"]
        self.rect(draw, self.wx[0], self.wy[0], self.wx[1], self.wy[1], (170, 190, 130, 255))
        self.rect(draw, -w / 2.0, -L, (plan["passes"] - 0.5) * w, 0.0, (122, 160, 80, 255))
        for p, (k0, k1, p0, p1) in m["slots"].items():
            x = (int(p) - 1) * w
            if k0 is not None:
                self.rect(draw, x - w * 0.45, k0, x + w * 0.45, k1, (70, 110, 50, 255))
            if p0 is not None:
                self.rect(draw, x - w * 0.12, p0, x + w * 0.12, p1, (190, 160, 105, 255))
        for k in range(plan["passes"] + 1):
            a, b = self.p((k - 0.5) * w, 0.0), self.p((k - 0.5) * w, -L)
            draw.line((a, b), fill=(150, 185, 110, 255), width=1)
        turn = plan["turns"].get(str(m["pass_pos"]))
        for q in ([self.p(x, y) for x, y in turn][::2] if turn else []):
            draw.ellipse((q[0] - 1, q[1] - 1, q[0] + 1, q[1] + 1), fill=(250, 250, 245, 255))
        # baannummers links van het veld
        every = 1 if w * self.s >= 9.0 else (2 if w * self.s >= 5.0 else 3)
        for p in range(1, plan["passes"] + 1):
            if (p - 1) % every and p != plan["passes"]:
                continue
            x, y = self.p((p - 1) * w, -L - 700.0)
            draw.text((x, y), str(p), fill=(60, 60, 60, 255), font=small, anchor="rm")
        # refiller
        rx, ry = m["ref_pose"]
        col = REF_COLOR[plan["kind"]]
        q = self.p(rx, ry)
        r = max(3.0, 650.0 * self.s)
        draw.rectangle((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=col, outline=(255, 255, 255, 255))
        # werkrobot: driehoek in de rijrichting
        cx, cy = m["centre"]
        a = math.radians(m["psi"])
        hx, hy = -math.sin(a), math.cos(a)
        size = 900.0
        tip = self.p(cx + hx * size, cy + hy * size)
        lft = self.p(cx - hx * size * 0.7 + hy * size * 0.6, cy - hy * size * 0.7 - hx * size * 0.6)
        rgt = self.p(cx - hx * size * 0.7 - hy * size * 0.6, cy - hy * size * 0.7 + hx * size * 0.6)
        draw.polygon((tip, lft, rgt), fill=(250, 200, 30, 255), outline=(40, 40, 40, 255))


# ---------------------------------------------------------------------
# Bijschrift
# ---------------------------------------------------------------------
def bar(draw, x, y, w, h, value, cap, color, label, value_text, small, mark=None):
    draw.text((x, y - 2), label, fill=MUTED, font=small, anchor="ls")
    draw.text((x + w, y - 2), value_text, fill=INK, font=small, anchor="rs")
    draw.rounded_rectangle((x, y + 2, x + w, y + 2 + h), radius=3, fill=(230, 230, 230, 255))
    f = max(0.0, min(1.0, value / cap)) if cap else 0.0
    if f > 0:
        draw.rounded_rectangle((x, y + 2, x + max(6, w * f), y + 2 + h), radius=3, fill=color)
    if mark is not None:
        mx = x + w * max(0.0, min(1.0, mark / cap))
        draw.line((mx, y, mx, y + h + 4), fill=(60, 60, 60, 255), width=2)


def clock(t):
    return "%d:%02d" % (int(t // 60), int(t % 60))


def decorate(image, plan, metas, i, fonts):
    big, reg, small, tiny = fonts
    m = metas[i]
    W, H = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    # titel en status, linksboven
    title = plan["title"]
    lines = [("Working robot", m["w_text"]), (NAMES[plan["kind"]], m["r_text"])]
    tw = max(d.textlength(title, font=big), max(d.textlength(a + ":  " + b, font=reg) for a, b in lines)) + 28
    d.rounded_rectangle((14, 14, 14 + tw, 14 + 98), radius=10, fill=PANEL)
    d.text((28, 24), title, fill=INK, font=big)
    for k, (a, b) in enumerate(lines):
        y = 58 + k * 24
        d.text((28, y), a + ":", fill=MUTED, font=reg)
        d.text((28 + d.textlength(a + ":  ", font=reg), y), b, fill=INK, font=reg)
    # tempo en veldtijd, rechtsboven
    sp = m["speed"]
    txt = "%s× real time" % (nl(sp, 0) if sp >= 2.5 else nl(sp, 1))
    tw = d.textlength(txt, font=big) + 28
    d.rounded_rectangle((W - 14 - tw, 14, W - 14, 14 + 64), radius=10, fill=PANEL)
    d.text((W - 28, 22), txt, fill=INK, font=big, anchor="ra")
    d.text((W - 28, 50), "field time %s" % clock(m["t"]), fill=MUTED, font=reg, anchor="ra")
    # kaartje + meters, rechtsonder
    pw, ph = 390, 308
    x0, y0 = W - 14 - pw, H - 14 - ph
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=10, fill=PANEL)
    fm = FieldMap(plan, (x0 + 10, y0 + 10, x0 + pw - 10, y0 + ph - 122))
    fm.draw(d, m, tiny)
    by = y0 + ph - 106
    bar(d, x0 + 14, by, pw - 28, 10, m["level"], m["tank_cap"], BLUE, "work tank",
        "%s l" % nl(m["level"], 1), small, mark=m["full"])
    rt, rc = m["ref_tank"]
    bar(d, x0 + 14, by + 34, pw - 28, 10, rt, rc, REF_COLOR[plan["kind"]], NAMES[plan["kind"]],
        "%s l" % nl(rt, 0), small)
    flow = m["ref_flow_lpm"]
    d.text((x0 + 14, by + 64), "%s l applied · %d refill%s%s" % (
        nl(m["applied"], 1), m["refills"], "" if m["refills"] == 1 else "s",
        (" · pump %d l/min" % flow) if flow else ""), fill=INK, font=small)
    d.text((x0 + 14, by + 82), "pump %d rpm · %s l/ha · lift %d mm" % (m["rpm"], nl(plan["dose"]), m["lift"]),
           fill=MUTED, font=small)
    # baanvolgorde, linksonder
    order = plan["order"]
    x, y = 28, H - 44
    label = "Pass order:"
    seq_w = d.textlength(label + "  ", font=reg) + sum(d.textlength(str(p) + "  ", font=reg) for p in order) + 14
    d.rounded_rectangle((14, H - 56, 14 + seq_w + 14, H - 14), radius=10, fill=PANEL)
    d.text((x, y), label, fill=MUTED, font=reg)
    x += d.textlength(label + "  ", font=reg)
    done = m["pass_pos"]
    for k, p in enumerate(order):
        col = GREEN if k < done else (ORANGE if k == done else MUTED)
        fnt = fonts[0] if k == done else reg
        d.text((x, y + (-3 if k == done else 0)), str(p), fill=col, font=fnt)
        x += d.textlength(str(p) + "  ", font=fnt)
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def fonts():
    return font(20, "bold"), font(16), font(13), font(10)


def load(folder):
    with open(os.path.join(folder, "frames.json"), encoding="utf-8") as handle:
        data = json.load(handle)
    return data["plan"], data["frames"]


def frame_images(folder, plan, metas, size=None, step=1, window=None):
    fs = fonts()
    names = sorted(n for n in os.listdir(folder) if n.startswith("frame_") and n.endswith(".png"))
    if window:
        names = [n for n in names if window[0] <= int(n[6:10]) < window[1]]
    for n in names[::step]:
        i = int(n[6:10])
        im = decorate(Image.open(os.path.join(folder, n)), plan, metas, i, fs)
        yield i, (im.resize(size, Image.LANCZOS) if size else im)


# ---------------------------------------------------------------------
# Titelkaart en route
# ---------------------------------------------------------------------
SCENARIO_TEXT = {
    "simple": ["Passes worked in the order 1, 7, 2, 8, 3, 9, ... so that every turn is a U-turn (no reversing).",
               "The IBC refiller stands inside the U-turn on the headland; the working robot stops on the straight",
               "with its funnel under the nozzle, is topped up and drives on. The refiller then moves 1 m on."],
    "liquid": ["Passes worked side by side; every turn has three points (arc, reverse along the headland, arc).",
               "The refiller waits beside the headland with its boom out, puts the spout in the funnel and drives",
               "along while the working robot reverses; then it reverses with its trailer two passes on."],
    "station": ["Passes skipped as in the simple variant. An IBC trailer stands still on the headland beside the field.",
                "When the work tank is too low for the next two passes, the robot leaves its turn, drives to the",
                "station, is filled, turns round on the headland and drives back into its next pass."],
}


def title_card(plan, size=(1280, 720), bg=None):
    im = bg.copy() if bg is not None else Image.new("RGB", size, (245, 245, 240))
    im = Image.blend(im, Image.new("RGB", size, (250, 250, 247)), 0.82)
    d = ImageDraw.Draw(im)
    d.text((80, 200), "Precision applicator V2 on the Bruut OpenAgbot", fill=(90, 90, 90), font=font(26))
    d.text((80, 240), plan["title"], fill=(25, 25, 25), font=font(34, "bold"))
    for k, line in enumerate(SCENARIO_TEXT[plan["key"]]):
        d.text((80, 320 + k * 34), line, fill=(50, 50, 50), font=font(22))
    d.text((80, 470), "Field %d passes x %d m, 5 rows at 200 mm, %d l/ha. Time runs faster in the passes, "
           "slower in the turns and while filling." % (plan["passes"], plan["len"] / 1000.0, plan["dose"]),
           fill=(90, 90, 90), font=font(18))
    return im


def route_png(plan, metas, path):
    """Bovenaanzicht met de baanvolgorde en de bochten (matplotlib), banen horizontaal zoals het kaartje."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    w, L = plan["w"] / 1000.0, plan["len"] / 1000.0
    fig, ax = plt.subplots(figsize=(11.0, 5.2), dpi=120)
    ax.add_patch(plt.Rectangle((-L, -w / 2), L, plan["passes"] * w, color=(0.48, 0.63, 0.31)))
    for p in range(1, plan["passes"] + 1):
        x = (p - 1) * w
        ax.plot([-L, 0], [x, x], color=(0.3, 0.45, 0.2), lw=0.8)
        ax.text(-L - 0.6, x, str(p), ha="right", va="center", fontsize=8, color=(0.25, 0.25, 0.25))
    ax.plot([m["centre"][1] / 1000.0 for m in metas[::2]], [m["centre"][0] / 1000.0 for m in metas[::2]],
            color=(0.12, 0.12, 0.12), lw=0.9)
    for k, p in enumerate(plan["order"]):
        ax.annotate(str(k + 1), (-L / 2 + (2.5 if k % 2 else -2.5), (p - 1) * w), ha="center", va="center",
                    fontsize=8, color="white", weight="bold",
                    bbox=dict(boxstyle="circle,pad=0.15", fc=(0.85, 0.40, 0.08), ec="none"))
    if plan["kind"] == "station":
        sx = plan["station_dock_x"] / 1000.0 - 0.56
        ax.plot([plan["ys"] / 1000.0 + 1.2], [sx], "s", color=(0.15, 0.45, 0.2), ms=12)
        ax.text(plan["ys"] / 1000.0 + 2.2, sx, "station", va="center", fontsize=9)
    ax.set_aspect("equal")
    ax.invert_yaxis()
    ax.set_xlabel("along the passes (m); headland of the refiller on the right")
    ax.set_ylabel("across (m)")
    ax.set_title("%s\npath of the working robot; orange: order in which the passes are worked" % plan["title"],
                 fontsize=10)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------
# Uitvoer
# ---------------------------------------------------------------------
def encoder(path, fps, size):
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % size,
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


def write_mp4(path, images, fps, size=(1280, 720)):
    proc = encoder(path, fps, size)
    n = 0
    for im in images:
        proc.stdin.write(im.convert("RGB").tobytes())
        n += 1
    proc.stdin.close()
    proc.wait()
    print("%d frames -> %s (%.1f MB)" % (n, path, os.path.getsize(path) / 1e6))
    return path


def write_gif(path, images, fps, last_hold_ms=2500):
    images = list(images)
    sample = [images[k] for k in range(0, len(images), max(1, len(images) // 16))]
    sheet = Image.new("RGB", (images[0].width, images[0].height * len(sample)))
    for k, im in enumerate(sample):
        sheet.paste(im, (0, k * images[0].height))
    palette = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]
    durations = [int(round(1000.0 / fps / 10.0)) * 10] * len(frames)
    durations[-1] = last_hold_ms
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=False)
    print("%d frames -> %s (%.1f MB)" % (len(frames), path, os.path.getsize(path) / 1e6))
    return path


def gif_window(metas, fps, before=9.0, after=7.0):
    """Frames rond het eerste bijvullen (de GIF; de hele run staat in de MP4)."""
    k = next((i for i, m in enumerate(metas) if m["ref_flow_lpm"] > 0), len(metas) // 2)
    return max(0, k - int(before * fps)), min(len(metas), k + int(after * fps))


def card_frames(card, fps, seconds=3.0):
    for _ in range(int(seconds * fps)):
        yield card


def main(folder, key, out_dir=PREVIEW_DIR, gif_step=2, gif_size=(640, 360)):
    plan, metas = load(folder)
    os.makedirs(out_dir, exist_ok=True)
    fps = plan["fps"]
    first = Image.open(os.path.join(folder, "frame_0000.png"))
    card = title_card(plan, first.size, first)
    card.save(os.path.join(out_dir, "field_run_%s_title.png" % key))

    def stream():
        yield from card_frames(card, fps)
        for _, im in frame_images(folder, plan, metas):
            yield im

    mp4 = write_mp4(os.path.join(out_dir, "field_run_%s.mp4" % key), stream(), fps, first.size)
    gif = write_gif(os.path.join(out_dir, "field_run_%s.gif" % key),
                    (im for _, im in frame_images(folder, plan, metas, gif_size, gif_step, gif_window(metas, fps))),
                    fps / gif_step)
    stills(folder, key, plan, metas, out_dir)
    route_png(plan, metas, os.path.join(out_dir, "route_%s.png" % key))
    return mp4, gif


def stills(folder, key, plan, metas, out_dir):
    """Losse beelden met bijschrift: het eerste bijvullen en het afgewerkte veld."""
    fs = fonts()
    pick = {"refill": next((i for i, m in enumerate(metas) if m["ref_flow_lpm"] > 0), None), "done": len(metas) - 1}
    k = pick["refill"]
    if k is not None:
        k = min(len(metas) - 1, k + 8)
    pick["refill"] = k
    out = []
    for name, i in pick.items():
        if i is None:
            continue
        im = decorate(Image.open(os.path.join(folder, "frame_%04d.png" % i)), plan, metas, i, fs)
        path = os.path.join(out_dir, "field_run_%s_%s.png" % (key, name))
        im.save(path)
        out.append(path)
    return out


def main_all(folders, out_dir=PREVIEW_DIR):
    """Een film met de drie scenario's achter elkaar, elk met zijn titelkaart."""
    keys = ("simple", "liquid", "station")
    size, fps = None, None

    def stream():
        nonlocal size, fps
        for key, folder in zip(keys, folders):
            plan, metas = load(folder)
            first = Image.open(os.path.join(folder, "frame_0000.png"))
            yield from card_frames(title_card(plan, first.size, first), plan["fps"])
            for _, im in frame_images(folder, plan, metas):
                yield im

    plan, _ = load(folders[0])
    first = Image.open(os.path.join(folders[0], "frame_0000.png"))
    return write_mp4(os.path.join(out_dir, "field_runs_all.mp4"), stream(), plan["fps"], first.size)


if __name__ == "__main__":
    if sys.argv[1] == "--all":
        main_all(sys.argv[2:5])
    else:
        main(sys.argv[1], sys.argv[2])
