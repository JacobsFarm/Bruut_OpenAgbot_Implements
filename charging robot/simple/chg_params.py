import os
import sys

# =====================================================================
# Charging robot (simple) - parameters
# A second Bruut OpenAgbot (standard robot) as a mobile charger: it carries 4 battery pods (the 48 V LiFePO4 pod of
# "battery pack/simple", 2.56 kWh each, imported) on a deck on the upper beams, an isolated DC/DC charger (48 V in,
# 54 V CC/CV out, 1.5 kW) and, behind it on an arm under the rear beam, the contact head of the charging dock
# ("charging dock/simple", imported: PE head, 2 copper bars, V-funnel). A working robot with the dock's contact bracket
# on its front beam drives nose-first into the charger's rear, exactly as into the fixed dock, and charges there at the
# field edge or in the headland while the charger waits; then it goes back to work. The charger itself goes back to
# the shed when its pods are low.
# The docked working robot stands dock_d behind the charger (robot centre to robot centre).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the charger robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _f in (os.path.join(ROOT_DIR, "push blade", "simple"), os.path.join(ROOT_DIR, "battery pack", "simple"),
           os.path.join(ROOT_DIR, "charging dock", "simple")):
    if _f not in sys.path:
        sys.path.append(_f)
import bpk_params as B          # noqa: E402  (pod)
import cdk_params as C          # noqa: E402  (contacts)

robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_axle_z = 215.0
robot_tire_d = 430.0
robot_tire_w = 100.0
robot_steer_deg = 30.0
robot_mass = 160.0
robot_cg = (0.0, 95.0, 543.0)
robot_battery_wh = 1900.0       # usable, estimated
upper_beam_top = 699.0
upper_bolt_x = (-425.0, -325.0, 325.0, 425.0)
rear_beam_y = (-595.0, -555.0)  # rear outer lower beam (mirror of the front one), z 619..659
lower_beam_z = (619.0, 659.0)

# ---------------------------------------------------------------------
# Deck: 3 cross bars (flat bar 60 x 8) on the 4 upper beams in the grid holes, aluminium deck plate 6 mm
# ---------------------------------------------------------------------
bar_y = (-625.0, -275.0, 275.0)  # clear of the wheel-unit frame bolts at y +-425 / +-575 (up to z 705)
bar = (60.0, 8.0)
bar_x = (-450.0, 450.0)
deck_x = (-450.0, 450.0)
deck_y = (-660.0, 330.0)
deck_t = 6.0

# 4 pods standing on the deck, long side along y, handles to +x
pods_n = 4
pod_pitch = 210.0
pod_x0 = -400.0                 # inner face of the first pod
strap = (40.0, 4.0)             # 2 hold-down straps across the pods (width, thickness)
strap_y = (-170.0, 170.0)

# DC/DC charger 1.5 kW on the deck behind the pods
dcdc = (420.0, 200.0, 160.0)    # x, y, z
dcdc_y1 = -310.0                # front face
# main switch / fuse box beside it
fuse_box = (160.0, 120.0, 120.0)

# ---------------------------------------------------------------------
# Rear contact head (cdk head, bars and funnel, moved back by dock_d) on an arm under the rear lower beam
# ---------------------------------------------------------------------
dock_d = 1550.0                 # working robot centre is at y -dock_d when docked
arm = C.arm                     # 60 x 40 tube
arm_z = C.arm_z
bk_x = 170.0                    # bracket plate half width, on the rear face of the rear lower beam
bk_t = 6.0
bk_z0 = 465.0
bk_bolt_x = (-125.0, 125.0)

# ---------------------------------------------------------------------
# Work (chg_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
pod_wh = B.cells_n * B.cell_v * B.cell_ah       # 2560
pod_dod = B.dod
dcdc_w = 1500.0
dcdc_eff = 0.94
contact_r = C.r_contact
v_charge = C.v_charge
cv_share = C.cv_share
work_soc = (0.2, 1.0)           # the working robot is charged from 20 to 100 %
work_loads_w = {"inter_row_hoe": 1018.0, "grassland_harrow": 1260.0, "grass_meter": 239.0}
shed_km = 1.0                   # field to shed, one way
speed = 1.2                     # m/s transport
crr = 0.06
eta_drive = 0.75
dock_s = 60.0                   # s manoeuvre into the dock
shed_charger_w = 4000.0         # 4 pods charged in parallel at the shed (4 x 1 kW)
tyre_rating_kg = 230.0          # per tyre, 16 x 6.50-8 class (estimated, as other heavy implements)
# from build_chg.mass_properties() (update after a change of the model)
MODEL_MASS = {"kg": 134.5, "cg": (6.0, -93.0, 779.0)}
