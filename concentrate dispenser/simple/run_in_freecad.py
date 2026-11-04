import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\concentrate dispenser\simple"
FPA = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "feed pusher auger", "V3")
for p in (FPA, FOLDER):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
for n in ("fpa_params", "fpa_parts", "build_fpa"):      # another feed pusher version may be loaded (same prefix)
    if n in sys.modules and FPA not in sys.modules[n].__file__:
        del sys.modules[n]

import fpa_params
import fpa_parts
import build_fpa
import cdd_params
import cdd_parts
import cdd_calc
import build_cdd

for module in (fpa_params, fpa_parts, build_fpa, cdd_params, cdd_parts, cdd_calc, build_cdd):
    importlib.reload(module)

doc = build_cdd.build()
cdd_calc.report()
