"""Macro to render the two-liquid animations in their own FreeCAD process (no MCP time-out):

    freecad.exe render_tla.py        with environment variables
    TLA_KEY      turn | station | cycle
    TLA_JOB      frames (default) | test | check (3D overlaps between the robots and the trailer near each other)
    TLA_RANGE    frames: only frames a:b (to render one run in parallel processes)
    TLA_STEP     check: every n-th frame (default 3)
    TLA_OUT      folder for frame_0000.png ...
    TLA_FRAMES   test: frame numbers, e.g. "0,300,600" ("auto": a few spread over the run)
    TLA_LOG      log file (progress, errors, "done")

FreeCAD closes itself when done.
"""
import os
import sys
import time
import traceback

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\mobile refiller\two_liquids_animations"
if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

KEY = os.environ.get("TLA_KEY", "turn")
JOB = os.environ.get("TLA_JOB", "frames")
OUT = os.environ.get("TLA_OUT", os.path.join(FOLDER, "frames_" + KEY))
LOG = os.environ.get("TLA_LOG", os.path.join(OUT, "render.log"))
STANDALONE = "TLA_KEY" in os.environ


def log(*args):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(" ".join(str(a) for a in args) + "\n")


def main():
    t0 = time.time()
    import FreeCADGui as Gui
    import tla_plan
    import animate_tla
    run = tla_plan.frames(KEY)
    log("planned", len(run[1]), "frames", round(time.time() - t0, 1), "s")
    animate_tla.build(KEY, run)
    Gui.getMainWindow().showMaximized()
    log("built", round(time.time() - t0, 1), "s")
    if JOB == "check":
        step = int(os.environ.get("TLA_STEP", "3"))
        hits = animate_tla.check_run(step=step, log=LOG)
        log("overlaps", len(hits))
        for h in hits[:200]:
            log("  ", h)
        log("time", round(time.time() - t0, 1), "s")
        return
    only = None
    rng = os.environ.get("TLA_RANGE")
    if rng:
        a, b = (int(v) for v in rng.split(":"))
        only = range(a, min(b, len(run[1])))
    if JOB == "test":
        spec = os.environ.get("TLA_FRAMES", "auto")
        n = len(run[1])
        only = [int(n * k / 6) for k in range(6)] if spec == "auto" else [int(v) for v in spec.split(",")]
    animate_tla.render_all(OUT, log=LOG, only=only)
    log("time", round(time.time() - t0, 1), "s")


try:
    main()
except Exception:
    log(traceback.format_exc())
finally:
    log("done")
    if STANDALONE:
        os._exit(0)
