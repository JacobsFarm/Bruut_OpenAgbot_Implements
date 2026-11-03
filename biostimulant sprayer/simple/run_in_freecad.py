import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\biostimulant sprayer\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import bss_params
import ssp_params
import ssp_calc
import ssp_parts
import build_ssp
import bss_parts
import bss_calc
import build_bss

for module in (ssp_params, ssp_calc, ssp_parts, build_ssp, bss_params, bss_parts, bss_calc, build_bss):
    importlib.reload(module)

doc = build_bss.build()
bss_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
