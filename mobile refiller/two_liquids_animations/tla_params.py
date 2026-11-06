"""Settings of the four two-liquid refill animations (no text in the picture):

  turn      the mobile refiller with two IBCs (../simple_two_ibc) stands inside the U-turn of the precision applicator
            V4 (combined_v4) and fills both work tanks in one stop on the straight of the turn
  station   the precision applicator V4 drives to the IBC trailer with two liquids (../stationary/
            ibc_trailer_two_liquids), is filled with both liquids, reverses and turns into its next pass
  cycle     the mobile refiller drives along the headland to the IBC trailer, the trailer lifts its arm and fills both
            IBCs, the refiller reverses to the spot of the next turn and fills the working robot there
  rounds    two refills in the turn, the refiller reloads at the trailer, one more refill in the turn

Field coordinates (mm): x along the headland (pass p at x = (p - 1) * W), y = 0 on the field edge, field at y < 0,
headland at y > 0. Robot poses: rear-axle centre and heading psi (deg, 0 = +y, 90 = -x, -90 = +x; as
mobile refiller/simple/mrs_calc.heading).
"""
import os

FOLDER = os.path.dirname(os.path.abspath(__file__))
REFILLER = os.path.dirname(FOLDER)
ROOT = os.path.dirname(REFILLER)
MRD_FOLDER = os.path.join(REFILLER, "simple_two_ibc")
SIT2_FOLDER = os.path.join(REFILLER, "stationary", "ibc_trailer_two_liquids")
CMB4_FOLDER = os.path.join(ROOT, "liquid fertilizer applicator", "precision_applicator", "combined_v4")

# ---------------------------------------------------------------------
# Field and turns (as mobile refiller/simple: skip pattern, every turn a U-turn of 6 passes)
# ---------------------------------------------------------------------
W = 1000.0                      # pass width (5 rows at 200)
N_PASSES = 12
R = 2400.0                      # turning radius of the rear axle
Y_TURN = 1800.0                 # start of the arc from the field edge
YS = Y_TURN + R                 # 4200: straight of the U-turn (rear axle / centre line of the working robot)
SKIP = 6
FIELD_Y = (-14000.0, 0.0)       # field shown
HEADLAND_Y = (0.0, 7600.0)
TRACK_Y = (7600.0, 8800.0)      # farm track behind the headland
X_RANGE = (-60000.0, 80000.0)     # wide, so that the camera never looks past the ground

# ---------------------------------------------------------------------
# Robots
# ---------------------------------------------------------------------
WORKER_AXLE = 500.0             # standard Bruut: rear axle 500 behind the centre
WORKER_WB = 1000.0
REFILLER_AXLE = 1100.0          # lengthened Bruut (wheelbase 2200)
REFILLER_WB = 2200.0
WHEEL_X = 375.0
TIRE_R = 215.0
FUNNEL_Y = 170.0                # working robot: funnels at local y 170 (x +-227.5, A right)
FILL_Y = -70.0                  # mobile refiller: nozzles and fill funnels at local y -70
DOCK_D = 1450.0                 # mobile refiller centre line -> working robot centre line
REFILL_DX = 3230.0              # refiller centre this far along +x from the pass the working robot leaves
                                # (refiller 2.6 m long inside a 6 m U-turn: clear of both arcs, see RATIONALE)

V_WORK = 750.0                  # mm/s in the pass
V_HEAD = 500.0                  # on the headland
V_REV = 400.0
V_SLOW = 250.0                  # last metres to a stop under a nozzle
V_REFILLER = 500.0              # mobile refiller with liquid
ACCEL = 500.0
STEER_RATE = 35.0               # deg/s

# applicator (as the field runs: actuator 50 mm/s, lifted 150)
LIFT_MAX = 150.0
ACT_SPEED = 50.0
KNIFE_BEHIND = 800.0            # knives behind the rear axle (mm, applicator V3: knives at robot y -1300)
RAISE_LEAD = 750.0              # lifting starts when the knives are this far before the field edge
LOWER_LEAD = 1300.0             # lowering starts this far before the knives reach the edge

# pumps and amounts
Q_PUMP = 120.0 / 60.0           # l/s per pump (each liquid its own pump)
T_CHECK = 0.5
T_CLOSE = 1.0
ARM_LIFT_SPEED = 40.0           # mm/s, trailer arm actuator
WORKER_TANK_L = 78.4            # combined_v4
WORKER_FULL_L = 76.0            # level sensor stops the pump here

# ---------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------
TURN = {"pass_from": 3, "worker_l": (40.0, 36.0), "refiller_l": (420.0, 380.0), "done": (1, 7, 2, 8)}
STATION = {"pass_from": 6, "pass_to": 12, "worker_l": (14.0, 11.0), "trailer_l": (760.0, 690.0),
           "trailer_dx": 9000.0,    # trailer axle this far right of the pass the robot leaves: the turn into
                                    # pass_to clears the trailer by 845 mm (tla_plan.trailer_gap)
           "done": (1, 7, 2, 8, 3, 9, 4, 10, 5, 11)}
CYCLE = {"pass_from": 4, "refiller_l": (60.0, 45.0), "refiller_fill_to": (560.0, 560.0),
         "trailer_l": (900.0, 880.0), "worker_l": (38.0, 33.0), "trailer_x": 14000.0,
         "done": (1, 7, 2, 8, 3, 9)}
# rounds: the refiller fills the working robot in two turns (moving 1 m on in between), reloads at the trailer, and
# fills it once more in the third turn; between the turns the working robot works a pass down and the next one up
ROUNDS = {"pass_from": 2, "worker_l": ((40.0, 36.0), (36.0, 32.0), (38.0, 33.0)), "refiller_l": (150.0, 140.0),
          "refiller_fill_to": (560.0, 560.0), "trailer_l": (900.0, 880.0), "trailer_x": 14000.0,
          "done": (1, 7)}
Y_FAR = -16000.0                # the working robot turns at the far end out of sight (rear axle y)
Y_HIDE = -12000.0               # and is hidden beyond this
CAM_WORKER_Y = (-8000.0, -5000.0)   # the camera lets go of the working robot between these y (going down its pass)
ARM_MARGIN = 500.0              # the trailer arm is up before the refiller comes this close to the drop pipes

# ---------------------------------------------------------------------
# Playback: video 25 fps; real seconds per video second per phase (no caption, so the pace is told by the picture)
# ---------------------------------------------------------------------
FPS = 25
DT = 0.02                       # simulation step (s)
SPEED = {"drive": 2.5, "refill": 2.0, "transfer": 4.0, "fill_ibc": 30.0, "away": 6.0, "hold": 1.0}
HOLD_START = 1.0                # s of still picture at the start and the end
HOLD_END = 1.5
VIDEO_SIZE = (1280, 720)
GIF_SIZE = (640, 360)
GIF_FPS = 12.5

COLOR = {"field": (0.42, 0.58, 0.28), "headland": (0.55, 0.66, 0.38), "track": (0.62, 0.58, 0.50),
         "edge": (0.90, 0.88, 0.80), "worked": (0.36, 0.30, 0.20), "seam": (0.62, 0.50, 0.34),
         "stream_A": (0.20, 0.45, 0.95), "stream_B": (0.98, 0.55, 0.10), "beacon_off": (0.35, 0.30, 0.20)}
