import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\pheromone trap service\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import phs_params
import pbl_params
import pbl_parts
import build_pbl
import fin_params
import fin_parts
import phs_parts
import phs_calc
import build_phs

for module in (pbl_params, pbl_parts, build_pbl, fin_params, fin_parts, phs_params, phs_parts, phs_calc, build_phs):
    importlib.reload(module)

doc = build_phs.build()
print(build_phs.mass_properties(doc))
phs_calc.report()
