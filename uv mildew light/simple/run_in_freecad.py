import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\uv mildew light\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import uvc_params
import uvc_parts
import uvc_calc
import build_uvc

for module in (uvc_params, uvc_parts, uvc_calc, build_uvc):
    importlib.reload(module)

doc = build_uvc.build()
uvc_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
