import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\arena leveller\simple"
GHA = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "grassland harrow", "simple")
for p in (GHA, FOLDER):
    if p not in sys.path:
        sys.path.insert(0, p)

import gha_params
import gha_parts
import build_gha
import arl_params
import arl_parts
import arl_calc
import build_arl

for module in (gha_params, gha_parts, build_gha, arl_params, arl_parts, arl_calc, build_arl):
    importlib.reload(module)

doc = build_arl.build()
arl_calc.report()
