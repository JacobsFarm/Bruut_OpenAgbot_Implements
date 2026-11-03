"""QTimer job: build with the robot and run all checks, result in check_result.json (MCP timeout workaround)."""
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
        doc = build_cfa.build(save=False, step=False, show_robot=True)
        out["interference"] = str(build_cfa.check_interference(doc))
        out["poses"] = str(build_cfa.check_poses(doc))
        out["clearance"] = str(build_cfa.clearance(doc))
        out["mass"] = str(build_cfa.mass_properties(doc))
        out["size"] = str(build_cfa.size(doc))
    except Exception:
        out["error"] = traceback.format_exc()
    with open(os.path.join(FOLDER, "check_result.json"), "w", newline="\n") as f:
        json.dump(out, f, indent=1)


def start():
    from PySide import QtCore
    p = os.path.join(FOLDER, "check_result.json")
    if os.path.exists(p):
        os.remove(p)
    QtCore.QTimer.singleShot(100, run)
