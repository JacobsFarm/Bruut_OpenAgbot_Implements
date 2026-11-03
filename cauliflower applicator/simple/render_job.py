"""QTimer job: render_all() (previews + FCStd + STEP), result in render_result.json."""
import importlib
import json
import os
import sys
import traceback

sys.dont_write_bytecode = True
FOLDER = r"F:\veldrobot\aanbouwdelen\cauliflower applicator\simple"
if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)


def run():
    out = {}
    try:
        import cfa_params, cfa_calc, cfa_parts, build_cfa
        for m in (cfa_params, cfa_calc, cfa_parts, build_cfa):
            importlib.reload(m)
        out["images"] = build_cfa.render_all()
    except Exception:
        out["error"] = traceback.format_exc()
    with open(os.path.join(FOLDER, "render_result.json"), "w", newline="\n") as f:
        json.dump(out, f, indent=1)


def start():
    from PySide import QtCore
    p = os.path.join(FOLDER, "render_result.json")
    if os.path.exists(p):
        os.remove(p)
    QtCore.QTimer.singleShot(100, run)
