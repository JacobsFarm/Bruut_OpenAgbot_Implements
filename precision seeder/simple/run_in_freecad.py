import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\precision seeder\simple"
TPH = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "three point hitch", "simple")
for p in (TPH, FOLDER):
    if p not in sys.path:
        sys.path.insert(0, p)

import tph_params
import tph_parts
import build_tph
import psd_params
import psd_parts
import psd_calc
import build_psd

for module in (tph_params, tph_parts, build_tph, psd_params, psd_parts, psd_calc, build_psd):
    importlib.reload(module)

doc = build_psd.build()
psd_calc.report()
