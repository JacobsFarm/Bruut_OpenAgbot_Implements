import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\cambridge roll\overrseeder"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import ovd_params               # puts "cambridge roll" on sys.path (hitch, coupling, drawbar)
import cbr_params
import cbr_parts
import build_cbr
import ovd_parts
import ovd_calc
import build_ovd

for module in (cbr_params, cbr_parts, build_cbr, ovd_params, ovd_parts, ovd_calc, build_ovd):
    importlib.reload(module)

doc = build_ovd.build()
ovd_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
