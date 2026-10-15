import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\bandrake\electric"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import brk_params
import brk_calc
import brk_parts
import build_brk

for module in (brk_params, brk_calc, brk_parts, build_brk):
    importlib.reload(module)

doc = build_brk.build()
brk_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
