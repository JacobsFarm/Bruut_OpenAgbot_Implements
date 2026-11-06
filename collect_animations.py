"""Copy every animation GIF of the implements into one folder, <repo>/animations/, and every video (MP4, ...) into
<repo>/animations/video's/.

The GIFs and videos stay where their scripts write them (usually <variant>/previews/), and a copy goes to animations/
so all animations are together. animations/, *.gif and the video files are in .gitignore: they are generated and too
large for git.

    python collect_animations.py          copy all GIFs and videos in the repo (only new or changed ones)

make_gif_<p>.py calls collect(out_path) after writing its GIF (make_video_tla.py also after its MP4), so a new
animation lands in animations/ by itself.
Name in animations/: the path from the repo root without "previews", e.g. "dockweed drill v2 - animation_three_plants.gif".
"""
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "animations")
VIDEO_OUT = os.path.join(OUT, "video's")
VIDEO_EXT = (".mp4", ".mov", ".avi", ".mkv", ".webm")
SKIP = {"agbots", "inspiration", ".git", ".claude", "__pycache__"}


def target_name(gif):
    rel = os.path.relpath(os.path.abspath(gif), ROOT)
    parts = [p for p in rel.replace("\\", "/").split("/")[:-1] if p != "previews"]
    return " ".join(parts) + " - " + os.path.basename(gif)


def collect(gif):
    """Copy one GIF to animations/, or one video to animations/video's/ (skipped when the copy is already up to
    date). Returns the copy's path."""
    out = VIDEO_OUT if gif.lower().endswith(VIDEO_EXT) else OUT
    os.makedirs(out, exist_ok=True)
    dst = os.path.join(out, target_name(gif))
    if not (os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(gif)
            and os.path.getsize(dst) == os.path.getsize(gif)):
        shutil.copy2(gif, dst)
    return dst


def collect_all():
    found = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP and os.path.join(d, x) != OUT]
        found += [os.path.join(d, f) for f in files if f.lower().endswith((".gif",) + VIDEO_EXT)]
    for gif in sorted(found):
        collect(gif)
    return found


if __name__ == "__main__":
    found = collect_all()
    n_video = sum(1 for f in found if f.lower().endswith(VIDEO_EXT))
    print(f"{len(found) - n_video} GIFs in {OUT}, {n_video} videos in {VIDEO_OUT}")
