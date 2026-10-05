import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\overseeder\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import ovs_params
import ovs_kin
import ovs_parts
import build_ovs

for module in (ovs_params, ovs_kin, ovs_parts, build_ovs):
    importlib.reload(module)

doc = build_ovs.build()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
