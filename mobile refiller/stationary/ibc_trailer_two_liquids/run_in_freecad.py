"""Macro: rebuilds the IBC trailer with two liquids (F6 in FreeCAD) and prints the key sizes."""
import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\mobile refiller\stationary\ibc_trailer_two_liquids"
STATIONARY = os.path.dirname(FOLDER)
TRAILER = os.path.join(STATIONARY, "ibc_trailer")

for p in (STATIONARY, TRAILER, FOLDER):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)

import stc_params, stc_parts, stc_build  # noqa: E401
import sit_params, sit_parts  # noqa: E401
import sit2_params, sit2_parts, build_sit2  # noqa: E401

for module in (stc_params, stc_parts, stc_build, sit_params, sit_parts, sit2_params, sit2_parts, build_sit2):
    importlib.reload(module)

doc = build_sit2.build()
for key, value in build_sit2.clearance(doc).items():
    print("%-16s %s" % (key, value))

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
