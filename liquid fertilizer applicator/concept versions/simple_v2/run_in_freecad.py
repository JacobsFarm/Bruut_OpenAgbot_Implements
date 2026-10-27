import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\liquid fertilizer applicator\simple_v2"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import lfs2_params
import lfs2_kin
import lfs2_parts
import build_lfs2

for module in (lfs2_params, lfs2_kin, lfs2_parts, build_lfs2):
    importlib.reload(module)

doc = build_lfs2.build()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
