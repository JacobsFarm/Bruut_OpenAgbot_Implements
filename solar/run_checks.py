"""Long run in FreeCAD: build + checks, result in _out.json (the MCP client times out after ~2 minutes).
Start with: exec(open(r"F:\\veldrobot\\aanbouwdelen\\solar\\run_checks.py", encoding="utf-8").read())
"""
import contextlib
import importlib
import io
import json
import os
import sys
import time

sys.dont_write_bytecode = True
FOLDER = r"F:\veldrobot\aanbouwdelen\solar"
if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)
OUT = os.path.join(FOLDER, "_out.json")
if os.path.exists(OUT):
    os.remove(OUT)

import sol_params
import sol_parts
import sol_calc
import build_sol

for module in (sol_params, sol_parts, sol_calc, build_sol):
    importlib.reload(module)


def job():
    t = time.time()
    res = {}

    def log(k):
        res["t_" + k] = round(time.time() - t, 1)
        json.dump(res, open(OUT, "w"), indent=1, default=str)

    try:
        doc = build_sol.build()
        log("built")
        mass, cg, rows = build_sol.mass_properties(doc)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            sol_calc.report(canopy_mass=mass, canopy_cg_z=cg[2])
        res.update({"report": buf.getvalue(), "mass": [mass, cg, rows]})
        log("mass")
        res["interference"] = build_sol.check_interference(doc)
        log("interference")
        res["clearance"] = build_sol.clearance(doc)
        log("done")
    except Exception as exc:
        import traceback
        res["error"] = traceback.format_exc()
        log("failed")


from PySide import QtCore
QtCore.QTimer.singleShot(100, job)
