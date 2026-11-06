"""Macro: rebuilds the mobile refiller with two IBCs (F6 in FreeCAD) and prints the calculation."""
import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\mobile refiller\simple_two_ibc"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import mrd_params
import mrs_params, mrs_calc, mrs_parts, build_mrs  # noqa: E401
import stc_params, stc_parts  # noqa: E401
import mrd_parts, mrd_calc, build_mrd  # noqa: E401

for module in (mrs_params, mrs_calc, mrs_parts, build_mrs, stc_params, stc_parts, mrd_params, mrd_parts, mrd_calc,
               build_mrd):
    importlib.reload(module)

doc = build_mrd.build()
print(mrd_calc.report())

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
