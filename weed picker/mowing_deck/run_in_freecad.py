import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\weed picker\mowing_deck"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import wpk_params
import wpk_parts
import wpk_weeds
import wpk_kin
import wpk_calc
import build_wpk

for module in (wpk_params, wpk_parts, wpk_weeds, wpk_kin, wpk_calc, build_wpk):
    importlib.reload(module)

doc = build_wpk.build()
wpk_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
