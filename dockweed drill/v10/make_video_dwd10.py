"""Frames of the v10 animations -> MP4 video (1280 x 720, 25 fps, H.264), no text added.

Render the frames at the video frame rate first, in FreeCAD:
    import animate_dwd10, explode_dwd10, make_video_dwd10 as MV
    animate_dwd10.build()
    animate_dwd10.render_all(r"C:\\temp\\dwd10_video", size=MV.SIZE, dt=MV.DT)      # three plants, 2x speed
    MV.main(r"C:\\temp\\dwd10_video", "plants")         # -> previews/animation_three_plants.mp4
    explode_dwd10.build()
    explode_dwd10.render_all(r"C:\\temp\\dwd10_explode_video", size=MV.SIZE, fps=MV.FPS)   # real time
    MV.main(r"C:\\temp\\dwd10_explode_video", "exploded")  # -> previews/exploded_assembly_linear_guide.mp4

ffmpeg: environment variable FFMPEG, the PATH, or Kdenlive's copy (as make_video_tla.py).
The MP4 is also copied to <repo>/animations/video's/ (collect_animations.py).
"""
import glob
import os
import shutil
import subprocess
import sys

from PIL import Image

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
FPS = 25
SPEED = 2.0                          # three-plant animation: x real time (the exploded one runs in real time)
DT = SPEED / FPS                     # s simulated per frame (0.08)
SIZE = (1280, 720)
HOLD_END_S = 1.5                     # last frame held
NAMES = {"plants": "animation_three_plants.mp4", "exploded": "exploded_assembly_linear_guide.mp4"}
FFMPEG_PATHS = (r"C:\Program Files\kdenlive\bin\ffmpeg.exe",)


def ffmpeg_exe():
    exe = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    for p in FFMPEG_PATHS:
        if os.path.isfile(p):
            return p
    raise RuntimeError("ffmpeg not found: set FFMPEG or put ffmpeg on the PATH")


def _to_animations(path):
    d = FOLDER
    while not os.path.isfile(os.path.join(d, "collect_animations.py")) and os.path.dirname(d) != d:
        d = os.path.dirname(d)
    if d not in sys.path:
        sys.path.insert(0, d)
    import collect_animations
    collect_animations.collect(path)


def main(folder, key, fps=FPS, size=SIZE):
    files = sorted(glob.glob(os.path.join(folder, "frame_*.png")))
    if not files:
        raise RuntimeError("no frames in " + folder)
    out_path = os.path.join(PREVIEW_DIR, NAMES[key])
    tmp = out_path + ".tmp.mp4"         # write next to it and replace at the end (a player may have it open)
    cmd = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % size,
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", tmp]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    last = None
    for f in files:
        im = Image.open(f).convert("RGB")
        if im.size != size:
            im = im.resize(size, Image.LANCZOS)
        last = im.tobytes()
        proc.stdin.write(last)
    for _ in range(int(HOLD_END_S * fps)):
        proc.stdin.write(last)
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg failed for " + out_path)
    os.replace(tmp, out_path)
    _to_animations(out_path)
    print("%d frames -> %s (%.1f MB, %.1f s)" % (len(files), out_path, os.path.getsize(out_path) / 1e6,
                                                 len(files) / fps + HOLD_END_S))
    return out_path


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
