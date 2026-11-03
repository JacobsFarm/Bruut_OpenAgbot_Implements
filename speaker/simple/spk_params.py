import os
import sys

# =====================================================================
# Speech speaker (simple) - parameters
# Two weatherproof horn speakers on the Bruut OpenAgbot (standard robot), one looking forward and one back, with a
# 2 x 30 W class-D amplifier and a microphone in a small IP65 box. The robot computer speaks (offline text-to-speech):
# warnings when people come near ('robot is turning', 'please step aside'), status ('tank empty', 'battery low') and
# instructions; an operator can talk through the robot over the radio link and listen with the microphone.
# The volume follows the distance to the nearest detected person, with a ceiling near animals.
# Each horn sits on the middle of a flat bar bolted to the 2 inner upper beams (grid holes x +-325, y +-300); the
# front horn is high enough to pass over the GNSS dome, both stay clear of the steering stacks.
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

PBL_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "push blade", "simple")
if PBL_FOLDER not in sys.path:
    sys.path.append(PBL_FOLDER)

robot_steer_deg = 30.0
upper_beam_top = 699.0
bolt_x = (-325.0, 325.0)                # bolt lines of the inner upper beams
hole_y = 300.0

# Bracket: flat bar 8 mm 700 x 60 across the inner upper beams + an upright plate 8 mm 140 wide for the horn
plate_x = (-345.0, 345.0)
upright_x = (-70.0, 70.0)
plate_w = 60.0
plate_t = 8.0
upright_h = 180.0

# Horn: rectangular mouth 220 x 140, depth 200, driver O100 x 90 behind it
horn_mouth = (220.0, 140.0)
horn_throat = (60.0, 50.0)
horn_depth = 200.0
driver = (100.0, 90.0)
horn_x = 0.0
horn_z = 830.0                  # horn axis: the mouth bottom (760) passes over the GNSS dome (740)

# Amplifier and microphone box on the rear bar (IP65, 160 x 120 x 70)
amp_box = (160.0, 120.0, 70.0)
mic_d = 20.0

# ---------------------------------------------------------------------
# Work (spk_calc)
# ---------------------------------------------------------------------
sensitivity_db = 105.0          # dB SPL at 1 W / 1 m (typical 30 W horn)
amp_w = 30.0
noise_db = {"quiet_field": 45.0, "farmyard": 60.0, "next_to_tractor": 80.0}
speech_margin_db = 10.0         # speech above the noise for good intelligibility
animal_cap_db = 85.0            # ceiling at 5 m near cows and horses (estimated, not to frighten them)
neighbour_cap_db = 55.0         # at the nearest house (estimated)
amp_eff = 0.8
talk_share = 0.05               # share of the time the speaker talks
MODEL_MASS = {"kg": 6.0}
