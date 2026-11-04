import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\calf milk taxi\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import cmt_params
import cmt_parts
import cmt_calc
import build_cmt

for module in (cmt_params, cmt_parts, cmt_calc, build_cmt):
    importlib.reload(module)

doc = build_cmt.build()
cmt_calc.report()
