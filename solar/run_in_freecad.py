import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\solar"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import sol_params
import sol_parts
import sol_calc
import build_sol

for module in (sol_params, sol_parts, sol_calc, build_sol):
    importlib.reload(module)

doc = build_sol.build()
mass, cg, rows = build_sol.mass_properties(doc)
sol_calc.report(canopy_mass=mass, canopy_cg_z=cg[2])
print("interference:", build_sol.check_interference(doc))
print("clearance:", build_sol.clearance(doc))
print("mass/CG:", mass, cg, rows)

try:
    import FreeCADGui as Gui
    Gui.ActiveDocument.ActiveView.viewIsometric()
    Gui.SendMsgToActiveView("ViewFit")
except Exception:
    pass
