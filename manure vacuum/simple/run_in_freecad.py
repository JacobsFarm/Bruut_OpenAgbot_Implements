import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\manure vacuum\simple"
ROOT = os.path.dirname(os.path.dirname(FOLDER))
for p in [os.path.join(ROOT, f, "simple") for f in ("push blade", "broom sweeper", "magnet sweeper", "debris vacuum")] + [FOLDER]:
    if p not in sys.path:
        sys.path.insert(0, p)

import dvc_params
import dvc_parts
import build_dvc
import mvc_params
import mvc_parts
import mvc_calc
import build_mvc

for module in (dvc_params, dvc_parts, build_dvc, mvc_params, mvc_parts, mvc_calc, build_mvc):
    importlib.reload(module)

doc = build_mvc.build()
mvc_calc.report()
