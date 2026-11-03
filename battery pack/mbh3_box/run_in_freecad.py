import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\battery pack\mbh3_box"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import bbx_params
import bbx_parts
import bbx_calc
import build_bbx

for module in (bbx_params, bbx_parts, bbx_calc, build_bbx):
    importlib.reload(module)

CONCEPT = "well"        # top / well / saddle / cabinet_well / cabinet_top / wood_side / wood_side_mu3 (only 2)
N = 2                   # batteries: 2, 3 or 4

doc = build_bbx.build(CONCEPT, N)
bbx_calc.report()
print(build_bbx.mass_properties(doc))

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
