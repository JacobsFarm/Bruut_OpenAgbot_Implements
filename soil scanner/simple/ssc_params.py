import os

# =====================================================================
# Soil scanner (simple) - parameters
# Passive gamma-ray spectrometer for the Bruut OpenAgbot (standard robot), as the Interra Scan / SoilOptix sensor that
# is driven over the field on a utility vehicle: a CsI(Tl) crystal in a sealed tube 600 mm above the ground measures
# the natural radiation of Cs-137, U-238, K-40 and Th-232 from the topsoil. Driving lanes 10 m apart at 1.2 m/s with
# one spectrum per second gives blocks of 10 x 1.2 m, ~830 data points per ha. Together with calibration samples
# (at least 4 per field and 2 per ha) the spectra become map layers: texture (lutum, sand), water holding capacity,
# pH, organic matter, P, K, CEC, micronutrients.
#
# The detector tube lies across the robot in front of the front wheels (y 880), in 2 clamp rings with an EPDM liner,
# hung on 4 rubber mounts under 2 steel brackets on the front outer lower beam. A tube guard in front protects it;
# the spectrum processor + 4G logger sits on the right bracket. Optional: the soil sampler in the middle of the
# robot takes the calibration samples in the same run (build(with_sampler=True), animation).
#
# Axes = robot model: x = right, y = driving direction (front = +y), z = up, ground = z 0, mm.
# Origin = centre of the robot (wheel centres (+-375, +-500)). All dimensions are here; never hardcode.
# =====================================================================

SSA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                          "soil sampler", "simple")

# ---------------------------------------------------------------------
# Robot interface (from the robot model in "agbot design", that folder is not in git)
# ---------------------------------------------------------------------
robot_wheel_x = 375.0
robot_axle_y = 500.0
robot_wheelbase = 1000.0
robot_track = 750.0
robot_tire_d = 430.0
robot_tire_top = 480.0          # bounding box top of the tyre with lugs
robot_front_beam_y = (555.0, 595.0)     # front OUTER lower beam (x direction)
robot_lower_beam_z = (619.0, 659.0)
robot_upper_beam_inner_x = 305.0        # inner face of the inner upper beams
robot_gnss = (0.0, 575.0)
robot_steer_deg = 30.0
robot_mass = 160.0              # kg, estimated
m10_hole = 10.4

# ---------------------------------------------------------------------
# Brackets (steel S235, 2 x, welded): base plate on top of the front outer lower beam with 2 M10 into the grid holes,
# a side plate up and forward, and an arm plate on top that carries the rubber mounts over the clamp rings.
# ---------------------------------------------------------------------
bracket_x = 175.0               # bracket centre plane x +-175 (between the GNSS dome x +-75 and the steered stack ~x 251)
bolt_dx = 50.0                  # M10 at x +-125 and +-225 (grid holes of the front beam are at x +-25 + 50 k)
base = (140.0, 60.0, 8.0)       # x, y, t
base_y = (545.0, 605.0)
side_t = 8.0
# side plate outline (y, z), on the bracket centre plane
side_pts = ((545.0, 667.0), (545.0, 751.0), (810.0, 751.0), (810.0, 735.0), (650.0, 667.0))
arm_w = 70.0                    # arm plate across x
arm_y = (545.0, 985.0)
arm_z = (751.0, 759.0)

# ---------------------------------------------------------------------
# Detector: aluminium tube OD 200 x 4 (black), blue aluminium end caps, inside a CsI(Tl) crystal 100 x 100 x 400
# (4 l, 4 x 4 x 16 in) in PE foam, a PMT O76 and the MCA / high-voltage board; cable gland in the right cap.
# ---------------------------------------------------------------------
det_y = 880.0
det_z = 600.0                   # crystal axis 600 mm above the ground (as on the Gator)
tube_d = 200.0
tube_t = 4.0
tube_half = 330.0               # tube x -330..330
cap_d = 226.0
cap_len = 40.0
cap_wall = 6.0
label_d = 170.0                 # silver face plate with the label
crystal = (400.0, 100.0, 100.0)     # x, y, z
crystal_x0 = -270.0
foam_d = 150.0                  # foam sleeve ID around the crystal (diagonal 141)
pmt_d = 76.0
pmt_len = 170.0
mca_d = 160.0
mca_t = 20.0
gland_d = 22.0
gland_len = 28.0
gland_r = 100.0                 # gland off the axis, outside the face plate
cable_d = 9.0

# ---------------------------------------------------------------------
# Clamps and rubber mounts: 2 rings 50 wide, 6 thick, EPDM liner 2 mm; a lug on top with 2 rubber mounts O30 x 20
# (M8, ~40 N/mm each) into the arm plate; a clamp bolt M8 through 2 ears at the bottom.
# ---------------------------------------------------------------------
liner_t = 2.0
ring_t = 6.0
ring_w = 50.0
lug = (50.0, 120.0)             # x, y
lug_z = (702.0, 731.0)
mount_d = 30.0
mount_y = (845.0, 915.0)
ear = (50.0, 26.0, 18.0)        # x, y gap 10, z

# ---------------------------------------------------------------------
# Guard: tube O30 x 2.5 from the front of the arm plates around the front of the detector
# ---------------------------------------------------------------------
guard_d = 30.0
guard_pts = ((-175.0, 965.0, 736.0), (-395.0, 1012.0, 690.0), (-395.0, 1012.0, 520.0), (395.0, 1012.0, 520.0),
             (395.0, 1012.0, 690.0), (175.0, 965.0, 736.0))

# ---------------------------------------------------------------------
# Processor box: IP67 220 x 150 x 90 on the right arm plate (spectrum processor, logger, 4G modem)
# ---------------------------------------------------------------------
ebox = (150.0, 220.0, 90.0)     # x, y, z
ebox_xy = (bracket_x, 720.0)    # centre

# ---------------------------------------------------------------------
# Physics (ssc_calc): gamma lines and mass attenuation coefficients (cm2/g, NIST XCOM for soil ~ SiO2/water mix)
# ---------------------------------------------------------------------
LINES = {   # isotope: (window line keV, mu/rho cm2/g)
    "Cs-137": (662.0, 0.0776),
    "K-40": (1461.0, 0.0526),
    "U-238 (Bi-214)": (1765.0, 0.0478),
    "Th-232 (Tl-208)": (2615.0, 0.0396),
}
soil_rho = 1.45                 # g/cm3 dry bulk density, topsoil
soil_water = 0.20               # g/g water (adds to the attenuating mass)
air_rho = 0.00120               # g/cm3
csi_rho = 4.51                  # g/cm3
# count rate in each window per litre of crystal at 0.6 m per unit of concentration (estimated from portable 0.35 l
# NaI figures scaled by volume and x1.3 for CsI)
SENS = {"K-40": 12.0, "U-238 (Bi-214)": 1.2, "Th-232 (Tl-208)": 0.55}       # cps / l / (% K, ppm eU, ppm eTh)
SOILS = {   # % K, ppm eU, ppm eTh (typical Dutch topsoils, estimated)
    "sand": (0.6, 0.8, 2.5),
    "loess": (1.6, 2.2, 9.0),
    "clay": (2.2, 2.8, 11.0),
}
crystal_options = {"2 l (90 x 310, MS-2000 size)": 2.0, "4 l (100 x 100 x 400, this model)": 4.0}

# ---------------------------------------------------------------------
# Work (ssc_calc)
# ---------------------------------------------------------------------
g = 9.81
steel = 7.85e-6
alu = 2.7e-6
pe_foam = 0.05e-6
epdm = 1.2e-6
lane = 10.0                     # m between lanes (= block width)
speed = 1.2                     # m/s while scanning
spectrum_hz = 1.0               # one spectrum per second -> block length = speed / hz
turn_r = 5.0                    # m headland turn (half the lane distance)
samples_min = 4                 # calibration samples per field
samples_per_ha = 2.0
cores_per_sample = 10           # cores in a 3 m circle per calibration sample (estimated)
t_core = 9.0                    # s per core with the soil sampler (down, up, eject, short move)
crr = 0.06
eta_drive = 0.75
p_scanner = 12.0                # W detector + MCA + HV
p_logger = 15.0                 # W processor, GNSS, 4G
battery_wh = 1900.0
example_field_ha = 18.0         # the maize field from the Interra webinar (pH 4.4 .. 5.1)
example_field = (450.0, 400.0)  # m, length x width
MODEL_MASS = {"total_kg": 45.2, "cg_y": 849.0}     # from build_ssc.mass_properties() (update after a change)


def block_len():
    return speed / spectrum_hz


def mu_soil(mu_rho):
    """Linear attenuation of the moist soil, 1/cm."""
    return mu_rho * soil_rho * (1.0 + soil_water)


def crystal_litre():
    return crystal[0] * crystal[1] * crystal[2] * 1e-6
