"""Frames of the two-liquid animations -> MP4 (1280 x 720, 25 fps) and GIF (640 x 360, 12.5 fps), no text added.

    "C:/Program Files/FreeCAD 1.1/bin/python.exe" make_video_tla.py <frames folder> <turn|station|cycle>

ffmpeg: environment variable FFMPEG, the PATH, or Kdenlive's copy (C:/Program Files/kdenlive/bin/ffmpeg.exe).
The GIF is also copied to <repo>/animations/ (collect_animations.py).
"""
import glob
import os
import shutil
import subprocess
import sys

from PIL import Image

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)
import tla_params as P      # noqa: E402

NAMES = {"turn": "refill_in_the_turn", "station": "refill_at_the_trailer", "cycle": "refiller_reloads_at_trailer",
         "rounds": "two_refills_reload_one_refill"}
FFMPEG_PATHS = (r"C:\Program Files\kdenlive\bin\ffmpeg.exe",)


def ffmpeg_exe():
    exe = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    for p in FFMPEG_PATHS:
        if os.path.isfile(p):
            return p
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _to_animations(gif):
    d = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isfile(os.path.join(d, "collect_animations.py")) and os.path.dirname(d) != d:
        d = os.path.dirname(d)
    if d not in sys.path:
        sys.path.insert(0, d)
    import collect_animations
    collect_animations.collect(gif)


def frame_files(folder):
    return sorted(glob.glob(os.path.join(folder, "frame_*.png")))


def write_mp4(files, path, fps=P.FPS, size=P.VIDEO_SIZE):
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % size,
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", path + ".tmp.mp4"]
    # write next to it and replace at the end: an MP4 overwritten while a player has it open came out corrupt
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in files:
        im = Image.open(f).convert("RGB")
        if im.size != size:
            im = im.resize(size, Image.LANCZOS)
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed for " + path)
    os.replace(path + ".tmp.mp4", path)
    _to_animations(path)                # copy to <repo>/animations/video's/
    print("%d frames -> %s (%.1f MB)" % (len(files), path, os.path.getsize(path) / 1e6))
    return path


def write_gif(files, path, step=2, size=P.GIF_SIZE, last_hold_ms=1500):
    images = [Image.open(f).convert("RGB").resize(size, Image.LANCZOS) for f in files[::step]]
    sample = [images[k] for k in range(0, len(images), max(1, len(images) // 16))]
    sheet = Image.new("RGB", (size[0], size[1] * len(sample)))
    for k, im in enumerate(sample):
        sheet.paste(im, (0, k * size[1]))
    palette = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]
    durations = [int(round(1000.0 * step / P.FPS / 10.0)) * 10] * len(frames)
    durations[-1] = last_hold_ms
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=False)
    _to_animations(path)
    print("%d frames -> %s (%.1f MB)" % (len(frames), path, os.path.getsize(path) / 1e6))
    return path


def stills(files, key, picks=(0.5,)):
    out = []
    for k, fr in enumerate(picks):
        src = files[min(len(files) - 1, int(fr * len(files)))]
        dst = os.path.join(PREVIEW_DIR, "%s_%d.png" % (NAMES[key], k + 1))
        shutil.copyfile(src, dst)
        out.append(dst)
    return out


def main(folder, key, still_picks=(0.5,)):
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    files = frame_files(folder)
    base = os.path.join(PREVIEW_DIR, NAMES[key])
    write_mp4(files, base + ".mp4")
    write_gif(files, base + ".gif")
    return stills(files, key, still_picks)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
