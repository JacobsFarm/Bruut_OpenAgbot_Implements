import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\dumper barrow\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import dmb_params
import dmb_parts
import dmb_calc
import build_dmb

for module in (dmb_params, dmb_parts, dmb_calc, build_dmb):
    importlib.reload(module)

doc = build_dmb.build()
dmb_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
