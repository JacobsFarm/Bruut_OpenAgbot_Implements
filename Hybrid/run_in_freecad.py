import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\Hybrid"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import hyb_params
import hyb_parts
import hyb_calc
import build_hyb

for module in (hyb_params, hyb_parts, hyb_calc, build_hyb):
    importlib.reload(module)

doc = build_hyb.build()
hyb_calc.report()
print("interference:", build_hyb.check_interference(doc))
print("clearance:", build_hyb.clearance(doc))
print("mass/CG:", build_hyb.mass_properties(doc))

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
