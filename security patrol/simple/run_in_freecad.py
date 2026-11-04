import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\security patrol\simple"

if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

import scp_params
import pbl_params
import pbl_parts
import build_pbl
import spk_params
import spk_parts
import scp_parts
import scp_calc
import build_scp

for module in (pbl_params, pbl_parts, build_pbl, spk_params, spk_parts, scp_params, scp_parts, scp_calc, build_scp):
    importlib.reload(module)

doc = build_scp.build()
print(build_scp.mass_properties(doc))
scp_calc.report()
