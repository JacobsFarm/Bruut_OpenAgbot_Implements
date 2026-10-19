"""Model of the simple drop seeder (overseeder) on the Bruut OpenAgbot, trailed on the tow hitch of the Cambridge roll.

Use in FreeCAD (folder on sys.path, or via run_in_freecad.py):
    import build_ovd
    build_ovd.build()                          # saves FCStd and STEP (trailer straight behind the robot)
    build_ovd.set_articulation(35, 0)          # yaw (+ = trailer to the left), pitch (+ = drawbar up)
    build_ovd.check_interference()             # must be empty
    build_ovd.check_poses()                    # over the articulation range, must be empty
    build_ovd.clearance()
    build_ovd.mass_properties()                # mass, centre of gravity, load on the tow ball (hopper empty / full)
    build_ovd.render_all()

The seeder unit (build_unit) is also used by "overseeder with cambridge roll". Tree helpers and checks come from
build_cbr (folder "cambridge roll", put on sys.path by ovd_params).
"""
import os

import FreeCAD as App
from FreeCAD import Vector as V

import ovd_params as P
import ovd_parts as G
import cbr_parts as CG
import build_cbr as B

FOLDER = os.path.dirname(os.path.abspath(__file__))
PREVIEW_DIR = os.path.join(FOLDER, "previews")
DOC_NAME = "Overseeder_Drop"
SAVE_BASE = os.path.join(FOLDER, "Overseeder_Drop")
ROOT = "Overseeder_drop"
TRAILER = "Seeder_trailer"

COLOR = dict(B.COLOR)
COLOR.update({
    "galv": (0.72, 0.75, 0.78),
    "green": (0.15, 0.55, 0.25),
    "roller": (0.85, 0.80, 0.30),
    "rubber": (0.08, 0.08, 0.08),
    "brush": (0.35, 0.30, 0.22),
    "motor": (0.08, 0.08, 0.08),
    "box": (0.55, 0.57, 0.60),
    "camera": (0.10, 0.10, 0.12),
    "wheel": (0.10, 0.10, 0.10),
    "hub": (0.85, 0.75, 0.10),
})


def add(doc, parent, name, label, shape, color, visible=True):
    return B.add_shape(doc, parent, name, label, shape, color, visible, COLOR)


def build_unit(doc, parent, uy=P.unit_y, prefix=""):
    """The seeder unit: hopper, metering, drive, camera, control box. The metering roller is its own sub-Part
    (Meter) so an animation can spin it."""
    unit = B.new_part(doc, parent, prefix + "Seeder_unit", "seeder_unit_drop_1m")
    hop = B.new_part(doc, unit, prefix + "Hopper", "hopper_%dl" % round(hopper_litres()))
    add(doc, hop, prefix + "walls", "hopper_walls_galv_1.5mm", G.walls(uy), "galv")
    add(doc, hop, prefix + "end_plates", "end_plates_5mm", G.end_plates(uy), "frame")
    add(doc, hop, prefix + "lid", "lid_galv_2mm", G.lid(uy), "green")
    add(doc, hop, prefix + "hinge", "lid_hinge_D12", G.hinge(uy), "zinc")
    met = B.new_part(doc, unit, prefix + "Metering", "metering_fluted_roller")
    add(doc, met, prefix + "housing", "meter_housing_galv", G.housing(uy), "galv")
    add(doc, met, prefix + "brush", "brush_strip", G.brush(uy), "brush")
    add(doc, met, prefix + "flaps", "rubber_wind_flaps", G.flaps(uy), "rubber")
    add(doc, met, prefix + "meter_bearings", "meter_flange_bearings_15mm", G.meter_bearings(uy), "bearing")
    spin = B.new_part(doc, met, prefix + "Meter", "meter_roller_rotates")
    add(doc, spin, prefix + "roller", "fluted_roller_D50_12_flutes", G.roller(uy), "roller")
    add(doc, spin, prefix + "meter_shaft", "meter_shaft_D15", G.meter_shaft(uy), "steel")
    drv = B.new_part(doc, unit, prefix + "Drive", "drive_24V_worm_gearmotor")
    add(doc, drv, prefix + "gm_coupling", "jaw_coupling_D25", G.gm_coupling(uy), "red")
    add(doc, drv, prefix + "gearmotor", "worm_gearmotor_24V_20rpm", G.gearmotor(uy), "motor")
    add(doc, drv, prefix + "gm_bracket", "gearmotor_bracket_4mm", G.gm_bracket(uy), "frame")
    sen = B.new_part(doc, unit, prefix + "Sensing", "camera_and_control")
    add(doc, sen, prefix + "mast", "camera_mast_25x25x2", G.mast(uy), "frame")
    add(doc, sen, prefix + "mast_clamps", "camera_mast_brackets", G.mast_clamps(uy), "frame")
    add(doc, sen, prefix + "camera", "camera_bare_soil_detection", G.camera(uy), "camera")
    add(doc, sen, prefix + "control_box", "control_box_IP65_pi_motor_driver", G.control_box(uy), "box")
    add(doc, sen, prefix + "box_brackets", "control_box_brackets", G.box_brackets(uy), "frame")
    return unit


def meter_spin(angle_deg, uy):
    """Placement of the Meter part for a rotation of the roller (+ = seed moves down at the front)."""
    c = V(0, uy, P.roller_z)
    return App.Placement(c, App.Rotation(V(1, 0, 0), -angle_deg)).multiply(App.Placement(-c, App.Rotation()))


def build_trailer(doc, parent, uy=P.unit_y):
    tr = B.new_part(doc, parent, TRAILER, "seeder_trailer")
    build_unit(doc, tr, uy)
    fr = B.new_part(doc, tr, "Seeder_frame", "trailer_frame_wheels")
    add(doc, fr, "cross_bars", "cross_bars_40x40x3", G.cross_bars(uy), "frame")
    add(doc, fr, "forks", "wheel_forks_flat_30x6", G.forks(uy), "frame")
    add(doc, fr, "wheel_axles", "wheel_axles_D20", G.wheel_axles(uy), "zinc")
    add(doc, fr, "wheels", "wheels_solid_200x50", G.wheels(uy), "wheel")
    B.build_drawbar(doc, tr, G.cross_y(uy))
    return tr


def build_into(doc, parent=None):
    root = B.new_part(doc, parent, ROOT, "overseeder_drop_simple")
    B.build_hitch(doc, root)
    build_trailer(doc, root)
    return root


def build(save=True, show_robot=False, step=True):
    if DOC_NAME in App.listDocuments():
        App.closeDocument(DOC_NAME)
    doc = App.newDocument(DOC_NAME)
    doc.Label = "Overseeder drop simple"
    doc.Comment = ("Generated by build_ovd.py from ovd_params.py (+ cbr_params for the hitch). Robot coordinates: "
                   "x = right, y = driving direction (front = +y), z = up, ground = z 0.")
    robot = None
    try:
        robot = B.build_robot(doc)
    except Exception as exc:
        print("robot model not loaded:", exc)
    build_into(doc, robot)
    if robot is not None and not show_robot:
        B.set_robot_visible(False, doc, ROOT)
    doc.recompute()
    if save:
        doc.saveAs(SAVE_BASE + ".FCStd")
    if step:
        B.export_step(doc, SAVE_BASE + ".step", ROOT)
    return doc


def active_doc(doc=None):
    return B.active_doc(doc, ROOT)


def set_articulation(yaw=0.0, pitch=0.0, doc=None):
    B.set_articulation(yaw, pitch, active_doc(doc), TRAILER)


def check_interference(doc=None, tol=1.0):
    return B.check_interference(active_doc(doc), tol, ROOT)


def check_poses(doc=None, tol=1.0):
    return B.check_poses(active_doc(doc), None, tol, ROOT, TRAILER)


def clearance(doc=None):
    return B.clearance(active_doc(doc), ROOT, TRAILER)


MASS_FIXED = dict(B.MASS_FIXED)
MASS_FIXED.update({"bearings": 0.0, "meter_bearings": 2 * 0.25, "gearmotor": P.gm_kg, "control_box": P.box_kg,
                   "camera": 0.25, "wheels": 2 * P.wheel_kg, "flaps": 0.6, "brush": 0.4, "gm_coupling": 0.1})
DENSITY = (("roller", 2.7e-6),)


def hopper_litres():
    tv, ttz, bv, bz = P.throat_v, P.throat_z, P.top_v, P.top_z
    return (2 * tv + 2 * bv) / 2.0 * (bz - ttz) * P.width / 1e6


def mass_properties(doc=None):
    doc = active_doc(doc)
    tr = B.objects_of(doc, TRAILER)
    m, c = B.sum_mass(tr, MASS_FIXED, DENSITY)
    axle_y = P.unit_y + P.wheel_v
    seed = hopper_litres() * P.seed_density
    seed_y = P.unit_y
    mf = m + seed
    cyf = (c.y * m + seed_y * seed) / mf
    mu, _ = B.sum_mass(B.objects_of(doc, "Seeder_unit"), MASS_FIXED, DENSITY)
    return {"trailer_kg": round(m, 1), "cg": (round(c.x), round(c.y), round(c.z)), "unit_kg": round(mu, 1),
            "hopper_l": round(hopper_litres(), 1), "seed_kg": round(seed, 1),
            "ball_load_empty_N": round(B.ball_load(m, c.y, axle_y)),
            "ball_load_full_N": round(B.ball_load(mf, cyf, axle_y))}


def render_all():
    out = []
    doc = build(save=False, show_robot=True, step=False)
    B.add_floor(doc)
    out.append(B.save_view("1_iso_on_robot.png", (1.0, 1.2, -0.7), target=(0, -1000, 350), folder=PREVIEW_DIR))
    out.append(B.save_view("2_side.png", (1.0, 0.0, 0.0), target=(0, -1050, 420), height=1500, folder=PREVIEW_DIR))
    B.remove(doc, [B.GROUND])
    B.set_robot_visible(False, doc, ROOT)
    out.append(B.save_view("3_iso_rear.png", (-1.0, 1.0, -0.6), target=(0, -1500, 350), folder=PREVIEW_DIR))
    section = ("end_plates", "control_box", "gearmotor", "gm_bracket", "gm_coupling",
               "meter_bearings", "forks", "wheels", "wheel_axles")
    B.set_visible(doc, section, False)
    out.append(B.save_view("4_metering_section.png", (-1.0, 0.0, 0.0), target=(0, P.unit_y, 330), height=750,
                           folder=PREVIEW_DIR))
    B.set_visible(doc, section, True)
    out.append(B.save_view("5_drive_detail.png", (-1.0, 0.8, -0.4), target=(560, P.unit_y, 220), height=550,
                           folder=PREVIEW_DIR))
    B.set_robot_visible(True, doc, ROOT)
    App.closeDocument(doc.Name)
    build()
    return out
