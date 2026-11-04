import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\charging robot\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import chg_params
import pbl_params
import pbl_parts
import build_pbl
import bpk_params
import cdk_params
import bpk_parts
import cdk_parts
import chg_parts
import chg_calc
import build_chg

for module in (pbl_params, pbl_parts, build_pbl, bpk_params, cdk_params, bpk_parts, cdk_parts, chg_params, chg_parts, chg_calc, build_chg):
    importlib.reload(module)

doc = build_chg.build()
print(build_chg.mass_properties(doc))
chg_calc.report()
