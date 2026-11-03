"""Copy every animation GIF of the implements into one folder: <repo>/animations/.

The GIFs stay where make_gif_<p>.py writes them (usually <variant>/previews/), and a copy goes to animations/ so all
animations are together. Both animations/ and *.gif are in .gitignore: GIFs are generated and too large for git.

    python collect_animations.py          copy all GIFs in the repo to animations/ (only new or changed ones)

make_gif_<p>.py calls collect(out_path) after writing its GIF, so a new animation lands in animations/ by itself.
Name in animations/: the path from the repo root without "previews", e.g. "dockweed drill v2 - animation_three_plants.gif".
"""
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "animations")
SKIP = {"agbots", "inspiration", ".git", ".claude", "__pycache__"}


def target_name(gif):
    rel = os.path.relpath(os.path.abspath(gif), ROOT)
    parts = [p for p in rel.replace("\\", "/").split("/")[:-1] if p != "previews"]
    return " ".join(parts) + " - " + os.path.basename(gif)


def collect(gif):
    """Copy one GIF to animations/ (skipped when the copy is already up to date). Returns the copy's path."""
    os.makedirs(OUT, exist_ok=True)
    dst = os.path.join(OUT, target_name(gif))
    if not (os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(gif)
            and os.path.getsize(dst) == os.path.getsize(gif)):
        shutil.copy2(gif, dst)
    return dst


def collect_all():
    found = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP and os.path.join(d, x) != OUT]
        found += [os.path.join(d, f) for f in files if f.lower().endswith(".gif")]
    for gif in sorted(found):
        collect(gif)
    return found


if __name__ == "__main__":
    n = len(collect_all())
    print(f"{n} GIFs in {OUT}")
