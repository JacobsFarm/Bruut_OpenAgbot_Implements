import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\barn pressure washer\simple"
ROOT = os.path.dirname(os.path.dirname(FOLDER))
for p in [os.path.join(ROOT, "push blade", "simple"), os.path.join(ROOT, "fence inspector", "simple"),
          os.path.join(ROOT, "landscaping tools", "simple"), FOLDER]:
    if p not in sys.path:
        sys.path.insert(0, p)

import fin_params
import fin_parts
import build_fin
import hdg_params
import hdg_parts
import build_hdg
import bpw_params
import bpw_parts
import bpw_calc
import build_bpw

for module in (fin_params, fin_parts, build_fin, hdg_params, hdg_parts, build_hdg, bpw_params, bpw_parts, bpw_calc, build_bpw):
    importlib.reload(module)

doc = build_bpw.build()
bpw_calc.report()
