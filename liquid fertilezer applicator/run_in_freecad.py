import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\liquid fertilezer applicator"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import lfa_params
import lfa_parts
import build_lfa

for module in (lfa_params, lfa_parts, build_lfa):
    importlib.reload(module)

doc = build_lfa.build()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
