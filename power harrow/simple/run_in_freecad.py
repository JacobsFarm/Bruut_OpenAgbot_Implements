import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\power harrow\simple"
TPH = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "three point hitch", "simple")
for p in (TPH, FOLDER):
    if p not in sys.path:
        sys.path.insert(0, p)

import tph_params
import tph_parts
import build_tph
import pwh_params
import pwh_parts
import pwh_calc
import build_pwh

for module in (tph_params, tph_parts, build_tph, pwh_params, pwh_parts, pwh_calc, build_pwh):
    importlib.reload(module)

doc = build_pwh.build()
pwh_calc.report()
