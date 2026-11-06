"""Macro: bouwt de toediener advanced V2 opnieuw (F6 in FreeCAD 1.1) en print de kerngetallen.

De controles duren even; draai die apart:
    import build_lfa2; build_lfa2.check_interference(); build_lfa2.check_hoses()
"""
import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\liquid fertilizer applicator\concept versions\advanced_V2"

if FOLDER in sys.path:
    sys.path.remove(FOLDER)
sys.path.insert(0, FOLDER)

import lfa2_params  # noqa: E402
importlib.reload(lfa2_params)
lfa2_params.setup_path()
import ik_params, ik_parts, ikd_params, ikd_parts, rp_params, rp_parts, build_rp  # noqa: E401,E402
for module in (ik_params, ik_parts, ikd_params, ikd_parts, rp_params, rp_parts, build_rp):
    importlib.reload(module)
import lfa2_parts, lfa2_pumpkit, lfa2_calc, build_lfa2  # noqa: E401,E402
lfa2_pumpkit._MODS.clear()
for module in (lfa2_params, lfa2_parts, lfa2_pumpkit, lfa2_calc, build_lfa2):
    importlib.reload(module)
build_lfa2._UNIT_CACHE.clear()

doc = build_lfa2.build()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
