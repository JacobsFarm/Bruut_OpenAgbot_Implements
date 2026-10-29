import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\lime spreader\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import lsp_params
import lsp_parts
import lsp_calc
import build_lsp

for module in (lsp_params, lsp_parts, lsp_calc, build_lsp):
    importlib.reload(module)

doc = build_lsp.build()
lsp_calc.report()

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
