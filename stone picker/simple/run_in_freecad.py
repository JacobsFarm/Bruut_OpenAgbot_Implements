import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\stone picker\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import spk_params
import spk_parts
import spk_calc
import build_spk

for module in (spk_params, spk_parts, spk_calc, build_spk):
    importlib.reload(module)

doc = build_spk.build()
spk_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
