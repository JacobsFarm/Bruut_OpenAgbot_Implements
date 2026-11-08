import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\three point hitch\a_frame"

TPH = os.path.join(os.path.dirname(FOLDER), "simple")
for folder in (TPH, FOLDER):
    if folder in sys.path:
        sys.path.remove(folder)
    sys.path.insert(0, folder)

import tph_params
import tph_parts
import tpa_params
import tpa_parts
import tpa_calc
import build_tpa

for module in (tph_params, tph_parts, tpa_params, tpa_parts, tpa_calc, build_tpa):
    importlib.reload(module)

if not globals().get("TPA_NO_BUILD"):
    doc = build_tpa.build()
    tpa_calc.report()
    try:
        import FreeCADGui as Gui
        Gui.ActiveDocument.ActiveView.viewIsometric()
        Gui.SendMsgToActiveView("ViewFit")
    except Exception:
        pass
