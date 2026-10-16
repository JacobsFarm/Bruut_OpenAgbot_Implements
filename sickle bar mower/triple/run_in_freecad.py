import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\sickle bar mower\triple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import sbm_params
import sbm_parts
import sbm_grass
import sbm_calc
import build_sbm

for module in (sbm_params, sbm_parts, sbm_grass, sbm_calc, build_sbm):
    importlib.reload(module)

doc = build_sbm.build()
sbm_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
