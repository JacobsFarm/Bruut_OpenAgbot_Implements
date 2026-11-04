import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\insect vacuum\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import isv_params
import ssp_params
import ssp_parts
import build_ssp
import ddb_params
import ddb_parts
import isv_parts
import isv_calc
import build_isv

for module in (ssp_params, ssp_parts, build_ssp, ddb_params, ddb_parts, isv_params, isv_parts, isv_calc, build_isv):
    importlib.reload(module)

doc = build_isv.build()
isv_calc.report()
