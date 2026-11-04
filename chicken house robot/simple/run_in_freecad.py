import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\chicken house robot\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import chk_params
import bsw_params
import bsw_parts
import build_bsw
import pbl_params
import pbl_parts
import build_pbl
import chk_parts
import chk_calc
import build_chk

for module in (pbl_params, pbl_parts, build_pbl, bsw_params, bsw_parts, build_bsw, chk_params, chk_parts,
               chk_calc, build_chk):
    importlib.reload(module)

doc = build_chk.build()
chk_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
