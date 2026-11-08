import importlib
import os
import sys

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\three point hitch\lift"

ROOT3 = os.path.dirname(FOLDER)
for folder in (os.path.join(ROOT3, "simple"), os.path.join(ROOT3, "a_frame"), FOLDER):
    if folder in sys.path:
        sys.path.remove(folder)
    sys.path.insert(0, folder)

import tph_params
import tph_parts
import tpa_params
import tpa_parts
import build_tpa
import tpl_params
import tpl_parts
import tpl_calc
import build_tpl

for module in (tph_params, tph_parts, tpa_params, tpa_parts, build_tpa, tpl_params, tpl_parts, tpl_calc, build_tpl):
    importlib.reload(module)

if not globals().get("TPL_NO_BUILD"):
    doc = build_tpl.build()
    tpl_calc.report()
