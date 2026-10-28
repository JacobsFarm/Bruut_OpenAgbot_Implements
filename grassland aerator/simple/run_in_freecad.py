import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\grassland aerator\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import gae_params
import gae_parts
import gae_calc
import build_gae

for module in (gae_params, gae_parts, gae_calc, build_gae):
    importlib.reload(module)

doc = build_gae.build()
gae_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
