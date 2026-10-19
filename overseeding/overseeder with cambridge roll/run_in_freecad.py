import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\cambridge roll\overseeder with cambridge roll"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import osr_params               # puts "cambridge roll" and "overrseeder" on sys.path
import cbr_params
import ovd_params
import cbr_parts
import ovd_parts
import build_cbr
import build_ovd
import cbr_calc
import ovd_calc
import osr_parts
import osr_calc
import build_osr

for module in (cbr_params, ovd_params, osr_params, cbr_parts, ovd_parts, build_cbr, build_ovd, cbr_calc, ovd_calc,
               osr_parts, osr_calc, build_osr):
    importlib.reload(module)

doc = build_osr.build()
osr_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
