import math
import os
import sys

# =====================================================================
# Three-point hitch, parallel variant - parameters
# The suspension of the liquid fertilizer applicator advanced (V2): a headstock with a parallel linkage (2 pairs of
# links) and a Linak LA36 on the diagonal whose upper pin runs in a slot, so the implement floats in work and stays
# level over the whole lift. Here the headstock is welded on the rear toolbar of three point hitch/simple and the
# rear frame of the linkage is a carrier bolted to the male A-frame triangle of the a_frame variant, so every
# implement with a female triangle (the cultivator is drawn) hangs on it.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot. All dimensions are here; never hardcode.
# =====================================================================
FOLDER = os.path.dirname(os.path.abspath(__file__))
TPA_FOLDER = os.path.join(os.path.dirname(FOLDER), "a_frame")
TPH_FOLDER = os.path.join(os.path.dirname(FOLDER), "simple")
for _f in (TPH_FOLDER, TPA_FOLDER):
    if _f not in sys.path:
        sys.path.append(_f)

import tpa_params as Q                    # noqa: E402  (coupler, LA36 datasheet, cultivator, robot)
import tph_params as TP                   # noqa: E402

robot_wheel_x = Q.robot_wheel_x
robot_axle_y = Q.robot_axle_y
robot_tire_d = Q.robot_tire_d
robot_tire_w = Q.robot_tire_w
robot_mass = Q.robot_mass
robot_cg_y = Q.robot_cg_y
tb_y = Q.tb_y                            # rear toolbar 80 x 80 x 4, y -860..-780, z 450..530
tb_z = Q.tb_z

# ---------------------------------------------------------------------
# Coupler: the male triangle of a_frame, same place in work as there (so the cultivator is in the same place)
# ---------------------------------------------------------------------
cp_base = Q.lower_b                      # (y, z) coupler origin in work: (-1250, 230)
cp_lean = Q.cp_lean

# ---------------------------------------------------------------------
# Parallel linkage: front pins on the headstock, rear pins on the carrier. The rear pins sit along the triangle
# (v direction), the front pins the same vector apart, so the carrier and the triangle translate without turning.
# ---------------------------------------------------------------------
link_x = 110.0                 # centre of each link pair (between the cheeks), clear of the hanger webs (x 155)
link_tube = 30.0               # 30 x 30 x 3
link_wall = 3.0
link_len = 300.0
link_boss_d = 34.0
pin_d = 16.0
cheek_t = 8.0
cheek_gap = 1.0                # link - cheek
rear_pin_lo = (90.0, -75.0)    # (v, w) on the carrier
rear_pin_hi = (370.0, -75.0)
theta_work = -12.0             # link angle in work (rear pins below the front pins), deg
theta_lift = 28.0              # lifted
theta_float = 8.0              # +- around the work pose within the slot
THETA_POSES = (-20.0, -12.0, -4.0, 8.0, 28.0)

# headstock (on the toolbar): 2 cheek pairs, a top cross tube with the slot plates for the LA36 rod eye
hs_y = (-885.0, -775.0)
hs_z_bot = 335.0
hs_cross = 40.0                # top cross tube 40 x 40 x 3
hs_cross_c = (-805.0, 722.0)   # (y, z) centre

# carrier (rear frame): 2 plate pairs on the triangle (bolted to its bottom and middle cross tubes)
cr_v = (55.0, 405.0)
cr_w = (-20.0, -100.0)

# ---------------------------------------------------------------------
# LA36 on the diagonal: body pin on the carrier (lugs on the middle cross tube of the triangle), rod eye in a slot
# in plates under the top cross tube of the headstock (as advanced V2: the slot closes when lifting)
# ---------------------------------------------------------------------
act_variant = "16F"            # 16 mm spindle, gear F: 2000 N, 60 / 43 mm/s (see tpp_calc.actuator)
act_stroke = 150.0
act_retracted = Q.act_bid_base + act_stroke     # 350
act_extended = act_retracted + act_stroke       # 500
act_body_pin = (180.0, -45.0)  # (v, w) on the carrier
act_a = (-780.0, 660.0)        # (y, z) end of the slot nearest the carrier: the rod pin bears here when lifting
act_motor_side = 1             # see check: motor above the spindle


def act_mass():
    return Q.act_mass(act_stroke)


# ---------------------------------------------------------------------
# Work, robot
# ---------------------------------------------------------------------
g = Q.g
steel = Q.steel
rubber = Q.rubber
front_share_min = Q.front_share_min
ballast_kg = Q.ballast_kg
ballast_cg_y = Q.ballast_cg_y
imp_cg_behind = Q.imp_cg_behind
# from build_tpp.mass_properties() (update after a change of the model)
MODEL_MASS = {"mount_kg": 27.9, "mount_cg_y": -737.0, "links_kg": 4.1, "carrier_kg": 14.0,
              "carrier_cg": (-1185.0, 418.0), "imp_kg": 33.7, "imp_cg": (-1354.0, 212.0), "act_kg": 4.8}


# ---------------------------------------------------------------------
# Kinematics
# ---------------------------------------------------------------------
def cp_point(vw, base=None):
    return Q.cp_point(base or cp_base, vw)


def rear_pins0():
    return cp_point(rear_pin_lo), cp_point(rear_pin_hi)


def front_pins():
    """(y, z) of the lower and upper front pins on the headstock."""
    a = math.radians(theta_work)
    lo, hi = rear_pins0()
    d = (link_len * math.cos(a), -link_len * math.sin(a))
    return (lo[0] + d[0], lo[1] + d[1]), (hi[0] + d[0], hi[1] + d[1])


def shift(theta):
    """Translation (dy, dz) of the carrier from the work pose at link angle theta (deg, + = rear pins up)."""
    a0, a = math.radians(theta_work), math.radians(theta)
    return (link_len * (math.cos(a0) - math.cos(a)), link_len * (math.sin(a) - math.sin(a0)))


def body_pin(theta):
    p = cp_point(act_body_pin)
    d = shift(theta)
    return p[0] + d[0], p[1] + d[1]


def act_length(theta):
    """Pin-to-pin length with the rod pin at the slot end (lifting / carrying)."""
    b = body_pin(theta)
    return math.hypot(act_a[0] - b[0], act_a[1] - b[1])


def slot_dir():
    """Unit (y, z) of the slot in the headstock plates: away from the carrier, along the LA36 in the work pose."""
    b = body_pin(theta_work)
    dy, dz = act_a[0] - b[0], act_a[1] - b[1]
    n = math.hypot(dy, dz)
    return dy / n, dz / n


def float_slot():
    """Slot length so that the carrier floats +-theta_float around the work pose."""
    lo = act_length(theta_work - theta_float)
    hi = act_length(theta_work + theta_float)
    return lo - hi


def act_work_length():
    """LA36 length in work: the rod pin at the slot end with the carrier at the bottom of its float."""
    return act_length(theta_work - theta_float)


def act_pin(theta, act_len=None):
    """(y, z) of the rod pin: carrying (None) at act_a, floating at a fixed length: slides in the slot."""
    if act_len is None:
        return act_a
    b = body_pin(theta)
    u = slot_dir()
    cy, cz = act_a[0] - b[0], act_a[1] - b[1]
    bb = cy * u[0] + cz * u[1]
    c = cy * cy + cz * cz - act_len * act_len
    s = -bb + math.sqrt(max(bb * bb - c, 0.0))
    s = max(0.0, min(float_slot(), s))
    return act_a[0] + s * u[0], act_a[1] + s * u[1]


def theta_for_length(L):
    lo, hi = -40.0, 50.0
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if act_length(mid) > L:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def float_limits(act_len):
    """(lowest, highest) link angle with the LA36 at act_len (pin at the slot end / at the far end)."""
    lo = theta_for_length(act_len)
    u = slot_dir()
    s = float_slot()
    e = (act_a[0] + s * u[0], act_a[1] + s * u[1])
    a, b = lo, 60.0
    for _ in range(50):
        mid = (a + b) / 2.0
        bp = body_pin(mid)
        if math.hypot(e[0] - bp[0], e[1] - bp[1]) > act_len:
            a = mid
        else:
            b = mid
    return lo, (a + b) / 2.0
