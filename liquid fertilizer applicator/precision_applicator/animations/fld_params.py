"""Maten en instellingen van de veldanimaties: de Bruut met de precisie-applicator V2 (5 rijen, rollenpomp) werkt een
heel veld af en wordt bijgevuld door een van de refillers uit "mobile refiller".

Veldcoordinaten (mm): x = dwars op de banen (baan p op x = (p - 1) W), y = langs de banen. Het veld ligt tussen
y = -FIELD_LEN (verre kopakker, "F") en y = 0 (kopakker van de refiller, "R"); de kopakkers liggen daarbuiten.
Robotcoordinaten zoals overal: x = rechts, y = rijrichting, z = omhoog, grond = z 0.
"""

# ---------------------------------------------------------------------
# Veld en banen
# ---------------------------------------------------------------------
N_PASSES = 12                   # een blok van 2N banen in het overslaanpatroon (N = 6)
FIELD_LEN = 40000.0             # kort veld, zodat het hele veld in beeld past (zie RATIONALE: 200 m in het echt)
W = 1000.0                      # werkbreedte: 5 rijen op 200 mm
R = 2400.0                      # draaistraal van de planner (agbot slim: R_min 2107 op de achteras)
Y_TURN = 1800.0                 # begin van de boog vanaf de veldrand (applicator geheven en vrij van het gewas)
YS = Y_TURN + R                 # rechte stuk van de bocht op de kopakker
START_IN = 3500.0               # start en einde: achteras zo ver in de verre kopakker

# ---------------------------------------------------------------------
# Rijden (als mobile refiller/simple/mrs_calc en liquid/mrl_calc)
# ---------------------------------------------------------------------
V_WORK = 750.0                  # mm/s in de baan (2,7 km/h, als combined_v2)
V_HEAD = 500.0                  # bogen op de kopakker
V_REV = 400.0                   # achteruit
V_DOCK = 250.0                  # laatste 2 m naar het station
DOCK_SLOW = 2000.0
ACCEL = 500.0                   # mm/s2
STEER_RATE = 35.0               # graden/s, stuurmotor
WHEELBASE = 1000.0
WHEEL_X = 375.0
AXLE_Y = 500.0
TIRE_R = 215.0

# applicator (combined/animate_cmb: actuator 50 mm/s, geheven 150 mm)
ACT_SPEED = 50.0                # mm/s hefhoogte
RAISE_LEAD = 750.0              # heffen begint als de messen zo ver voor de veldrand zijn: uit de grond op de rand
LOWER_LEAD = 1300.0             # zakken begint zo ver voor de rand: op diepte vlak na de rand
DOSE = 500.0                    # l/ha (combined_v2: 45 omw/min bij 0,75 m/s)

# ---------------------------------------------------------------------
# Werktank met vultrechter op de werkrobot (voor de pomp, tussen de assen)
# Trechter op dezelfde hoogte als de ontvangerkit van de refillers (rand op z 1144), maar 95 mm verder naar voren dan
# daar (0, -35): de rand blijft zo vrij van de verdeelbuis van de pomp. De dokposities rekenen met funnel_xy.
# ---------------------------------------------------------------------
rx_tank_x = 420.0               # half breed (over de bovenste balken, x +-375 +-50)
rx_tank_y = (-150.0, 330.0)     # achter: vrij van de pomp (verdeelbuis y -194); voor: stappenmotorplaten y 405
rx_tank_z0 = 744.0              # op zadelkokers 40 x 40 (699 .. 739) + rubber 5
rx_tank_h = 260.0
rx_tank_r = 50.0
rx_wall = 6.0
cradle_y = (-100.0, 270.0)      # zadelkokers 40 x 40 x 3 op de bovenste balken
cradle_half_len = 460.0
funnel_xy = (0.0, 60.0)
funnel_d = (300.0, 80.0)
funnel_h = 120.0
funnel_neck = 20.0
FUNNEL_RIM_Z = rx_tank_z0 + rx_tank_h + funnel_neck + funnel_h     # 1144
RX_RESERVE_L = 5.0              # niet verder leeg dan dit (zuigleiding)

# ---------------------------------------------------------------------
# Scenario's
# ---------------------------------------------------------------------
SCENARIOS = {
    "simple": {
        "title": "Mobile refiller simple (IBC): passes skipped, top-up in every U-turn",
        "short": "simple IBC refiller",
        "pattern": "skip", "refiller": "simple",
        "rx_start": 80.0, "rx_full": 90.0,
    },
    "liquid": {
        "title": "Mobile refiller liquid (boom + trailer): three-point turns, top-up while reversing",
        "short": "liquid refiller with boom",
        "pattern": "adjacent", "refiller": "liquid",
        "rx_start": 80.0, "rx_full": 90.0,
    },
    "station": {
        "title": "Stationary IBC trailer on the headland: passes skipped, the robot drives to it when low",
        "short": "stationary IBC trailer",
        "pattern": "skip", "refiller": "station",
        "rx_start": 16.0, "rx_full": 90.0,       # laag begonnen: het bezoek valt in de animatie (RATIONALE)
        "dock_from_field": 2000.0,               # station: achteras gedokt zo ver voorbij het eind van de boog (x)
    },
}

# ---------------------------------------------------------------------
# Afspelen en camera
# ---------------------------------------------------------------------
VIDEO_FPS = 25
SIZE = (1280, 720)
DT = 0.02                       # s simulatiestap
S_FAST = 40.0                   # x echte tijd midden in de baan
S_TURN = 3.0                    # bochten (eerste bocht op elke kopakker)
S_TURN_LATER = 10.0             # latere bochten
S_REFILL = 2.0                  # bijvullen (eerste keer)
S_REFILL_LATER = 4.0
PUMP_VIDEO_S = 4.0              # lang pompen (station): hooguit zo veel seconden video, tempo tot S_PUMP_MAX
S_PUMP_MAX = 12.0
SLOW_ZONE = (1500.0, 4000.0)    # afstand robot - veldrand: hieronder bochttempo, hierboven S_FAST
SPEED_RATE = 4.0                # tempo verandert hooguit deze factor per seconde video
HOLD_START = 1.5                # s video stil aan het begin en eind
HOLD_END = 3.5
