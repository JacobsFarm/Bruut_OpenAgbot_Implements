import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\landscaping tools\simple"
ROOT = os.path.dirname(os.path.dirname(FOLDER))
for p in [os.path.join(ROOT, "push blade", "simple"), os.path.join(ROOT, "fence inspector", "simple"), FOLDER]:
    if p not in sys.path:
        sys.path.insert(0, p)

import fin_params
import fin_parts
import build_fin
import hdg_params
import hdg_parts
import hdg_calc
import build_hdg

for module in (fin_params, fin_parts, build_fin, hdg_params, hdg_parts, hdg_calc, build_hdg):
    importlib.reload(module)

doc = build_hdg.build()
hdg_calc.report()
