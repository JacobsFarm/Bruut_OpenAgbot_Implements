import math

# =====================================================================
# Counterweights (simple) - parameters
# Stackable steel ballast plates of 11 kg (one person lifts one) on the lower cross beams of the Bruut OpenAgbot
# (standard robot), front and rear, both sides of the centre line. Each stack: a 15 mm base plate bolted on the two lower
# beams (4 x M10 in the hole grid) with 2 studs M16, plates with open slots that slide onto the studs from the outside,
# a clamp bar and 2 knob nuts on top (quick release). Up to 4 plates per stack: 0..99 kg per axle end.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

# ---------------------------------------------------------------------
# Robot interface (from "agbot design/agbot_params.py" and the model, that folder is not in git)
# ---------------------------------------------------------------------
robot_axle_y = 500.0
robot_wheel_x = 375.0
robot_beam_y = (425.0, 575.0)           # centres of the 2 lower cross beams at each end (40 x 40), mirrored at the rear
robot_lower_beam_z = (619.0, 659.0)
robot_steer_x = 295.0                   # steering plates of the front units start here (x 295..455, z 699..1032)
robot_gnss = (75.0, 740.0)              # half width and top of the GNSS dome (x +-75, y 500..650)
robot_mass = 160.0                      # kg, estimated
robot_cg_y = 0.0
m10_hole = 10.4

# ---------------------------------------------------------------------
# Stack (one per side and per end): x from stack_x[0] to stack_x[1], y around the end's beam pair
# ---------------------------------------------------------------------
stack_x = (100.0, 280.0)                # between the GNSS dome (75) and the steering plates (295)
stack_y = (400.0, 600.0)                # front; rear = mirrored
base_t = 15.0                           # 15: the nuts of the push blade / rear toolbar hanger bolts (x 175, 225) sit in
                                        # O32 holes in it, so both can be fitted together
hanger_bolt_x = (175.0, 225.0)
base_bolt_x = (125.0, 275.0)            # grid holes used (the push blade hangers use 175 / 225 from below)
stud_d = 16.0
stud_y = (440.0, 560.0)
stud_x = 190.0
stud_len = 240.0                        # above the base plate: 4 plates + clamp + knob
plate = (170.0, 200.0, 50.0)            # x, y, z of a ballast plate (11 kg with slots and grip)
plate_x0 = 105.0                        # inner edge of the plates
slot_w = 18.0                           # open slot from the outer edge to the stud
grip = (24.0, 100.0)                    # hand grip slot near the outer edge (x, y)
clamp = (40.0, 12.0)                    # flat bar over both studs (x width, thickness)
knob_d = 50.0
knob_h = 35.0
plates_max = 4

# what is drawn: plates per stack (front, rear)
DRAW = {"front": 2, "rear": 2}

# ---------------------------------------------------------------------
# Work (cwt_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
front_share_min = 0.20                  # least share on the front axle to steer (estimated)
rear_share_min = 0.25                   # least share on the rear axle for traction with a front tool (estimated)
lift_limit_kg = 15.0                    # comfortable single-person lift, often and from a low height (estimated)
# implements whose axle loads need ballast: (kg, cg y) of the parts that hang on the robot in transport, from their
# own *_params.MODEL_MASS / calc (copied here; update when those change)
IMPLEMENTS = {
    "grassland_harrow": [(22.4, -712.0), (60.4, -1144.0)],
    "inter_row_hoe": [(22.4, -724.0), (93.6, -1161.0)],
    "three_point_hitch_cultivator": [(25.8, -733.0), (10.5, -1046.0), (28.3, -1400.0)],
    "fertilizer_spreader_full": [(130.2, -834.0)],
    "push_blade": [(22.4, 712.0), (56.0, 1197.0)],
}
# from build_cwt.mass_properties() (update after a change of the model)
MODEL_MASS = {"plate_kg": 11.0, "base_kg": 5.5}       # base: plate with studs, clamp, knobs, bolts


def end_y(y, end):
    """A y value (front side) moved to 'front' or 'rear' (mirror)."""
    return y if end == "front" else -y


def end_span(span, end):
    return span if end == "front" else (-span[1], -span[0])
