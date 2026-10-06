import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\liquid fertilizer applicator\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import lfs_params
import lfs_kin
import lfs_parts
import build_lfs

for module in (lfs_params, lfs_kin, lfs_parts, build_lfs):
    importlib.reload(module)

doc = build_lfs.build()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
