import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\weeds burner\propane_hood"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import flw_params
import flw_calc
import flw_parts
import build_flw

for module in (flw_params, flw_calc, flw_parts, build_flw):
    importlib.reload(module)

doc = build_flw.build()
flw_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
