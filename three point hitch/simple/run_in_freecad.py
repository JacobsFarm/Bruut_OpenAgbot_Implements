import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\three point hitch\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import tph_params
import tph_parts
import tph_calc
import build_tph

for module in (tph_params, tph_parts, tph_calc, build_tph):
    importlib.reload(module)

doc = build_tph.build()
tph_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
