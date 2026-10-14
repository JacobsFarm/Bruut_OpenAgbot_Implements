import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\mobile refiller\stationary\three_point"
STATIONARY = os.path.dirname(FOLDER)

for p in (STATIONARY, FOLDER):
    if p not in sys.path:
        sys.path.insert(0, p)

import stc_params
import stc_parts
import stc_build
import stc_calc
import s3p_params
import s3p_parts
import s3p_calc
import build_s3p

for module in (stc_params, stc_parts, stc_build, stc_calc, s3p_params, s3p_parts, s3p_calc, build_s3p):
    importlib.reload(module)

doc = build_s3p.build()
print(s3p_calc.report())

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
