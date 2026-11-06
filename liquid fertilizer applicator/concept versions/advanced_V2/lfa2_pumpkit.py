"""Pompset op de robot: de 10-sectie rollenpomp (precision_applicator/roller_pump) met de pompsteun, de prop en
de twee aanvoerstompen in de verdeelbuis en de twee jerrycans met bak, kranen en aanvoerslangen van combined_v3.

Niets gekopieerd: cmb_params/cmb3_params/cmb_parts/cmb3_parts worden als eigen kopie geladen (lfa2_cmb_*), zoals
"agbot slim/slim_lfa.py" dat doet met advanced, en alleen het verschil wordt gezet: de pomp staat pump_riser (100) hoger
(lfa2_params.pump_z_rc), op vier blokken. combined_v3 zelf verandert dus niet.
Alle shapes van cmb3 zijn in robotcoordinaten; to_impl() zet ze in werktuigcoordinaten (y - robot_mount_y).
"""
import importlib.util
import os
import sys

import FreeCAD as App
from FreeCAD import Vector as V

import lfa2_params as P

CMB_FOLDER = os.path.join(P.PA_ROOT, "combined")
CMB3_FOLDER = os.path.join(P.PA_ROOT, "combined_v3")
APP_FOLDERS = tuple(os.path.join(P.PA_ROOT, f) for f in ("applicator", "applicator_v2", "applicator_v3"))
_MODS = {}


def _load(folder, name, alias, deps):
    """Laad folder/<name>.py als module alias, met deps tijdelijk als sys.modules[...] (eigen kopie)."""
    spec = importlib.util.spec_from_file_location(alias, os.path.join(folder, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    saved = {k: sys.modules.get(k) for k in deps}
    sys.modules.update(deps)
    sys.modules[alias] = mod
    try:
        spec.loader.exec_module(mod)
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    return mod


def modules():
    """(cmb3_params-kopie, cmb3_parts-kopie); cmb3_parts importeert ook de applicator-modules (pa_*, ikd_parts),
    daarom staan applicator, _v2 en _v3 achteraan op sys.path (het mes van precision_applicator/parts staat voor)."""
    if not _MODS:
        for folder in APP_FOLDERS:
            if folder not in sys.path:
                sys.path.append(folder)
        cp = _load(CMB_FOLDER, "cmb_params", "lfa2_cmb_params", {})
        cp.pump_z = P.pump_z_rc
        cp.pump_y = P.pump_y_rc
        c3 = _load(CMB3_FOLDER, "cmb3_params", "lfa2_cmb3_params", {"cmb_params": cp})
        c3.pump_z = P.pump_z_rc
        c3.pump_y = P.pump_y_rc
        c3.pump_x = P.pump_x
        cparts = _load(CMB_FOLDER, "cmb_parts", "lfa2_cmb_parts", {"cmb_params": cp})
        g3 = _load(CMB3_FOLDER, "cmb3_parts", "lfa2_cmb3_parts", {"cmb3_params": c3, "cmb_parts": cparts})
        _MODS.update({"C": c3, "G": g3, "cmb": cparts})
    return _MODS["C"], _MODS["G"]


def to_impl(shape):
    s = shape.copy() if not isinstance(shape, (list, tuple)) else None
    if s is None:
        import Part
        s = Part.makeCompound(list(shape))
    s.translate(V(0, -P.robot_mount_y, 0))
    return s


def pump_placement():
    """Placement van de pomp in werktuigcoordinaten."""
    return App.Placement(V(P.pump_x, P.pump_y_rc - P.robot_mount_y, P.pump_z_rc), App.Rotation())


def shapes():
    """Vaste delen van de pompset (zonder de pomp zelf), naam -> (label, shape in werktuigcoordinaten, kleur)."""
    C, G = modules()
    out = {"pump_mount_tubes": ("pump_mount_tubes_40x40", to_impl(G.mount_tubes()), "mount"),
           "manifold_divider": ("manifold_divider_plug_A_B", to_impl(G.manifold_divider()), "divider"),
           "manifold_inlets": ("manifold_inlets_half_inch_B_A", to_impl(G.manifold_inlets()), "mount"),
           "tank_tubes": ("tank_cross_tubes_40x40", to_impl(G.tank_tubes()), "mount"),
           "tank_tray": ("tank_tray_alu_3mm", to_impl(G.tray()), "tray")}
    for liq in C.LIQUIDS:
        body, cap = G.jerrycan(liq)
        out["jerrycan_" + liq] = ("jerrycan_20l_liquid_" + liq, to_impl(body), "can_" + liq)
        out["jerrycan_cap_" + liq] = ("jerrycan_cap_" + liq, to_impl(cap), "cap")
        out["tap_" + liq] = ("tap_half_inch_" + liq, to_impl(G.tap(liq)), "cap")
        out["supply_hose_" + liq] = ("supply_hose_3_4_liquid_" + liq, to_impl(G.supply_hose(liq)), "hose_" + liq)
    return out
