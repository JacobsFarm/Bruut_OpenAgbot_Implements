import math
import os
import sys

# =====================================================================
# Three-point hitch, A-frame variant - parameters
# A triangle quick coupler (A-frame, as on the front linkage of a tractor) at the rear of the Bruut OpenAgbot
# (standard robot), scaled to the robot. A Linak LA36 sits in the place of the top link: from a tower on the rear
# toolbar to the apex of the male triangle. The two lower arms, their cross tube, the pitch brace and the male
# triangle form one lift frame that turns about the lower pivots under the toolbar: retracting the LA36 lifts it.
# The rod eye of the LA36 runs in a slot in the tower, so in work the frame floats on the gauge wheels of the
# implement. Implement: the small cultivator of three point hitch/simple with a female triangle instead of pins.
#
# The coupler (male + female triangle), the LA36 and the cultivator are also used by the parallel and lift variants
# (they import this file).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================
FOLDER = os.path.dirname(os.path.abspath(__file__))
TPH_FOLDER = os.path.join(os.path.dirname(FOLDER), "simple")
if TPH_FOLDER not in sys.path:
    sys.path.append(TPH_FOLDER)          # toolbar, hangers, lower lugs and the cultivator of the simple variant

import tph_params as TP                   # noqa: E402

# ---------------------------------------------------------------------
# Robot interface (as three point hitch/simple)
# ---------------------------------------------------------------------
robot_wheel_x = TP.robot_wheel_x
robot_axle_y = TP.robot_axle_y
robot_tire_d = TP.robot_tire_d
robot_tire_w = TP.robot_tire_w
robot_mass = TP.robot_mass
robot_cg_y = TP.robot_cg_y
tb_y = TP.tb_y                           # rear toolbar 80 x 80 x 4 (from simple, same hangers and bolts)
tb_z = TP.tb_z

# ---------------------------------------------------------------------
# A-frame coupler (own size for the robot: about the category 0 frame, 500 between the lower pins, 350..400 high)
# Local frame of the coupler: u = x, v = up along the triangle, w = backwards (normal to the triangle, away from
# the robot). Origin = middle of the lower pin axis. The triangle leans 'cp_lean' (top towards the robot).
# ---------------------------------------------------------------------
cp_lean = 10.0                 # degrees from vertical in work, top forward: the implement hangs into it
cp_tube = 40.0                 # male frame: tube 40 x 40 x 3
cp_wall = 3.0
cp_leg_u = (200.0, 60.0)       # leg centre line: x at v = 0 and at v = cp_leg_v
cp_leg_v = 390.0
cp_top_v = (383.0, 395.0)      # top plate of the male apex (12 mm), carries the female hook
cp_top_u = 95.0
cp_bottom_v = (40.0, 80.0)     # bottom cross tube
cp_pin_d = 16.0                # lower pins (category 0 size)
cp_pin_u = 260.0               # lower pin centre: the arm ends here (500 between the inner faces of the arms)
cp_foot_u = (234.0, 246.0)     # foot lug of the male frame, inside the arm boss (x 250..270)
cp_boss_d = 44.0
# LA36 rod pin on the apex: the rod eye runs in a slot between 2 lugs (the end nearest the tower is cp_act_pin);
# the pitch brace sits lower on the triangle
cp_act_pin = (345.0, -80.0)    # (v, w): 80 mm in front of the triangle, so the LA36 clears the apex when lifted
cp_brace_pin = (200.0, -45.0)  # (v, w)
# latch: spring pin O20 along w through the bottom cross tube into the female lock plate
cp_latch_d = 20.0
cp_latch_v = 60.0
cp_latch_w = (-55.0, 40.0)
# female triangle (on the implement): plates behind the male legs, lips beside them, hook over the apex, lock plate
cf_gap = 2.0                   # play between male and female
cf_t = 6.0                     # plate thickness
cf_plate_w = 50.0
cf_lip_t = 5.0
cf_lip_v = (100.0, 340.0)
cf_lip_w = -15.0               # front edge of the lips (they reach 15 mm over the male legs)
cf_plate_v = (20.0, 380.0)
cf_hook_u = 80.0
cf_hook_w = -30.0
cf_lock_u = 150.0
cf_lock_v = (20.0, 95.0)


def cp_axes(lean=None):
    """Unit vectors (y, z) of v and w for a lean (deg, top forward)."""
    lam = math.radians(cp_lean if lean is None else lean)
    return (math.sin(lam), math.cos(lam)), (-math.cos(lam), math.sin(lam))


def cp_point(base, vw, lean=None):
    """Robot (y, z) of a coupler point (v, w), coupler origin at base (y, z)."""
    ev, ew = cp_axes(lean)
    v, w = vw
    return (base[0] + v * ev[0] + w * ew[0], base[1] + v * ev[1] + w * ew[1])


# ---------------------------------------------------------------------
# Linak LA36 (parts/actuator/linear-actuator-la36-data-sheet-eng.pdf), drawn as in the liquid fertilizer applicator
# advanced V2: reinforced housing, solid back fixture 0 degrees, solid rod eye, motor parallel to the spindle.
# ---------------------------------------------------------------------
ACT_DATASHEET = os.path.join(os.path.dirname(os.path.dirname(FOLDER)), "parts", "actuator",
                             "linear-actuator-la36-data-sheet-eng.pdf")
# 24 V table (p. 14): spindle -> (max load N, self-lock N, gear, speed no load / nominal mm/s, current no load /
# nominal A, end play mm)
LA36_24V = {
    "20F": (1700, 2200, "F 1:18", 72.0, 52.0, 2.4, 10.3, 3.5),
    "16F": (2000, 2600, "F 1:18", 60.0, 43.0, 2.4, 10.3, 2.9),
    "12F": (2600, 3400, "F 1:18", 44.0, 32.0, 2.4, 10.4, 2.6),
    "16G": (3400, 4400, "G 1:31", 35.0, 25.0, 2.4, 10.3, 2.3),
    "12G": (4500, 5800, "G 1:31", 26.0, 19.0, 2.4, 10.2, 2.3),
}
act_bid_base = 200.0           # installation dimension = 200 + stroke (stroke <= 300, solid eyes, p. 21)
act_mass_100 = 4.55            # kg at stroke 100, + 0.24 kg per 50 mm (p. 7, without cable)
act_mass_per_50 = 0.24
act_duty = 0.20
act_pin_d = 12.0
act_eye_hole = 12.2
act_eye_clear = 1.0
act_back_c = 25.2
act_back_d = 13.0
act_back_f = 27.9
act_back_nut = (36.0, 10.0)
act_rod_eye_c = 27.8
act_rod_eye_d = 13.5
act_rod_eye_f = 29.0
act_house_h = 148.0
act_house_below = 37.0
act_house_w = 76.0
act_house_len = 230.0
act_house_start = 24.0
act_gear_len = 62.0
act_motor_d = 72.0
act_tube = 44.5
act_tube_end_gap = 20.0
act_rod_d = 26.0

# this variant: 20 mm spindle, F gear (fast: the load is small), stroke 200
act_variant = "20F"
act_stroke = 200.0
act_retracted = act_bid_base + act_stroke     # 400
act_extended = act_retracted + act_stroke     # 600
act_motor_side = 1             # motor on the upper/rear side, away from the tower post
act_order_code = "36 200 200 0 0 01 B 6 - 6 1 2 F 3 0400 N C S 0 0 0"


def act_mass(stroke=None):
    s = act_stroke if stroke is None else stroke
    return act_mass_100 + act_mass_per_50 * (s - 100.0) / 50.0


def act_speed(force, variant=None):
    """mm/s at a load: linear between no load and the nominal load (datasheet)."""
    d = LA36_24V[variant or act_variant]
    return d[3] - (d[3] - d[4]) * min(abs(force), d[0]) / d[0]


def act_current(force, variant=None):
    d = LA36_24V[variant or act_variant]
    return d[5] + (d[6] - d[5]) * min(abs(force), d[0]) / d[0]


# ---------------------------------------------------------------------
# Lift frame: 2 lower arms on the pivots of the simple hitch (lugs under the toolbar), the male triangle on their
# ends, a cross tube and a pitch brace (turnbuckle) between the cross tube and the triangle.
# ---------------------------------------------------------------------
lower_a = TP.lower_a           # (y, z) pivot (-820, 380)
lower_ax = TP.lower_ax         # 280
arm_h = 50.0                   # flat bar 50 x 20
arm_t = 20.0
lower_b = (-1250.0, 230.0)     # (y, z) lower pins = coupler origin in work
arm_cross_frac = 0.45          # cross tube 40 x 40 x 3 at this fraction from the pivot
arm_cross = 40.0
brace_lug_dz = 45.0            # brace pin above the cross tube centre
brace_d = 26.0                 # turnbuckle tube
brace_eye = (36.0, 20.0)       # eye O and width

# tower on the rear toolbar: the LA36 housing hangs on a clevis behind the post (body pin act_c); the rod eye runs
# in a slot in the apex lugs of the triangle, so the frame floats in work
tower = 60.0                   # post 60 x 60 x 4
tower_y = (-845.0, -785.0)     # rear face 45 mm in front of the body pin: the housing stays clear of the post
tower_top = 1100.0
act_c = (-890.0, 1070.0)       # (y, z) LA36 body pin (back fixture) on the tower clevis
float_slot = 30.0              # +-15 mm along the LA36 around the work pose

lift_work = 0.0
lift_transport = 25.6          # degrees of the frame about the pivots, + = up (lower pins + 200 mm)
lift_float = (-2.0, 2.0)       # within the slot (see tpa_calc.float_range)
LIFT_POSES = (-2.0, 0.0, 2.0, 12.0, 25.6)

# ---------------------------------------------------------------------
# Implement: the cultivator of three point hitch/simple (tines, shares, gauge wheels), 10 mm closer to the robot,
# its mast and lower lugs replaced by a female triangle, a base plate and 2 stays to the toolbar.
# ---------------------------------------------------------------------
cult_dy = 20.0                 # shift of the simple cultivator (its toolbar y -1360..-1300 -> -1340..-1280)
imp_base_t = 8.0               # base plate on the toolbar under the female triangle
imp_stay = (40.0, 10.0)        # flat bar stays from the hook to the toolbar
work_depth = TP.work_depth
wheel_d = TP.wheel_d

# ---------------------------------------------------------------------
# Work, robot (from simple)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
rubber = 1.2e-6
front_share_min = TP.front_share_min
ballast_kg = TP.ballast_kg
ballast_cg_y = TP.ballast_cg_y
imp_cg_behind = TP.imp_cg_behind
# from build_tpa.mass_properties() (update after a change of the model)
MODEL_MASS = {"mount_kg": 26.7, "mount_cg_y": -732.0, "frame_kg": 18.2, "frame_cg": (-1111.0, 349.0),
              "imp_kg": 33.7, "imp_cg": (-1354.0, 212.0), "act_kg": 5.0}


# ---------------------------------------------------------------------
# Kinematics: the lift frame is one rigid body turning about lower_a
# ---------------------------------------------------------------------
def rotate_yz(p, deg, c=lower_a):
    """Point (y, z) of the lift frame turned about the pivot by deg (+ = lifts points behind the pivot)."""
    a = math.radians(deg)
    dy, dz = p[0] - c[0], p[1] - c[1]
    return (c[0] + dy * math.cos(a) + dz * math.sin(a), c[1] - dy * math.sin(a) + dz * math.cos(a))


def act_d(deg=0.0):
    """(y, z) of the slot end on the triangle apex nearest the tower: the rod pin bears here when lifting."""
    return rotate_yz(cp_point(lower_b, cp_act_pin), deg)


def slot_dir(deg=0.0):
    """Unit vector (y, z) of the slot in the apex lugs, away from the tower (along the LA36 in the work pose), turned
    with the frame."""
    d = act_d(0.0)
    dy, dz = d[0] - act_c[0], d[1] - act_c[1]
    n = math.hypot(dy, dz)
    e = rotate_yz((d[0] + dy / n, d[1] + dz / n), deg)
    d1 = act_d(deg)
    return e[0] - d1[0], e[1] - d1[1]


def act_pin(deg, act_len=None):
    """(y, z) of the rod pin. Carrying (act_len None): at the slot end act_d. Floating with a fixed actuator
    length: the pin slides in the slot, clamped to its ends."""
    d = act_d(deg)
    if act_len is None:
        return d
    u = slot_dir(deg)
    cy, cz = d[0] - act_c[0], d[1] - act_c[1]
    b = cy * u[0] + cz * u[1]
    c = cy * cy + cz * cz - act_len * act_len
    s = -b + math.sqrt(max(b * b - c, 0.0))
    s = max(0.0, min(float_slot, s))
    return d[0] + s * u[0], d[1] + s * u[1]


def act_length(deg):
    """Pin-to-pin length of the LA36 with the rod pin at the slot end (lifting / carrying)."""
    d = act_d(deg)
    return math.hypot(act_c[0] - d[0], act_c[1] - d[1])


def act_work_length():
    """Actuator length in work: the rod pin in the middle of the slot at the work pose."""
    return act_length(lift_work) + float_slot / 2.0


def lift_for_length(L):
    """Frame angle (deg) at which the LA36 of length L carries the frame (pin at the slot end)."""
    lo, hi = -10.0, 40.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if act_length(mid) > L:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def lower_pin(deg):
    return rotate_yz(lower_b, deg)


def brace_e():
    """(y, z) of the brace pin on the cross tube (work pose)."""
    a, b = lower_a, lower_b
    f = arm_cross_frac
    return (a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1]) + brace_lug_dz)


def brace_f():
    return cp_point(lower_b, cp_brace_pin)


def brace_len():
    e, f = brace_e(), brace_f()
    return math.hypot(f[0] - e[0], f[1] - e[1])
