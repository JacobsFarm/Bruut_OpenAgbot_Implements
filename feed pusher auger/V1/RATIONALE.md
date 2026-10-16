# Feed pusher auger (advanced): design rationale

5 October 2026. Model: `Feed_Pusher_Auger.FCStd` (FreeCAD 1.1, generated with `build_fpa.py`).
The figures come from the model, from `fpa_calc.py` and from the animation (`animate_fpa.summary()`).
Where something is assumed or estimated, this is stated.

![on the robot, from the front at an angle](previews/9_on_robot_iso.png)

---

## 1. Assignment

- Develop the advanced design further.
- Replace the round, rolled trough with a square folded sheet-metal hood, as in the simple version.
- Make the mounting fit on the wheel modules, through the four holes.
- Put the motor on its feet on the square plate.
- Put the feed pusher on the agbot, on the side of the fixed motors. The rotating steering mechanisms are then at the
  back.
- Animate the feed pushing: pushing the feed sideways, the forces on the auger and the reaction of the robot.

## 2. What has changed compared with the first advanced design

| Was | Now | Why |
| --- | --- | --- |
| Round hood (rolled, 3 mm) | **One 2 mm sheet with 4 bends** (press brake), blank 1440 × 774 mm | No rolling work. The bends make the sheet stiff enough. Thinner is possible because the hood no longer carries anything (§ 4.2) |
| Separate motor tower on the side plate | **Foot-mounted gearmotor (B3)** on an 8 mm motor plate on top of the hood, with an upstanding edge against the beam | The chain pull goes through the beam into the frame. The motor sits high and dry, out of the feed |
| Arms with a mounting plate on an assumed cross beam | **4 arms on the wheel modules**, each with **4 × M10 through the 4 holes** in the rear flange of the wheel bracket's side plate | Those holes are already in every wheel bracket. Nothing has to be drilled in the robot frame |
| Continuous Ø30 shaft | **Two Ø30 stub shafts**, 70 mm into the core tube, on 2 welded-in discs per side | 6.5 kg lighter. The 60.3 × 4 core tube is stiff enough (§ 5.4) |
| Two identical side plates | **Bearing plate with an open discharge on the right** | The feed must be able to leave on the fence side |
| M10 pins | **M6 4.6 shear bolt on the left**, M10 8.8 on the right | Protection against jamming (§ 5.3) |
| None | **Chain tensioner** (arm + nylon wheel on a rubber torsion element) | The centre distance is fixed by the foot-mounted motor |
| None | **Counterweight 2 × 20 kg** at the front | Without a counterweight too little load remains on the steered wheels (§ 4.7) |

## 3. The design in brief

![side view on the robot](previews/10_on_robot_side.png)

1. **Auger:** Ø320 flight, pitch 260, 5 mm, on a 60.3 × 4 core tube.
   - Right-handed.
   - Turns at 150 rpm, with the front going up. The feed is lifted instead of being pressed under the flight, and goes to +x (the feed fence).
2. **Bearings:** UCF206 on the outside of an 8 mm side plate (left) and an 8 mm bearing plate (right).
3. **Hood:** 2 mm, 4 bends.
   - On the robot side a 10 mm rubber scraper flap hangs down to 5 mm above the floor.
   - On the left there is a PE glide shoe as protection.
4. **Beam:** 80 × 80 × 3 tube on the hood. Welded end plates with 2 × M12 into the side plate and the bearing plate; the nuts are accessible above the beam.
5. **Drive:** 24 V DC gearmotor, 550 W, 300 rpm, with feet.
   - The motor stands with 4 × M10 on an 8 mm motor plate on top of the hood. That plate is fixed to the beam with 2 × M10.
   - Chain 08B-1, 15T → 30T, with tensioner.
   - 2 mm chain guard.
6. **Mounting:** 4 arms of 8 mm, orange in the images. Each arm has:
   - an adapter plate with 4 × M10 on the rear flange of a wheel bracket;
   - a gusset;
   - an end plate with 4 × M12 through the beam, in 30 mm slotted holes. These let you adjust the height by ±15 mm when the glide shoe and the flap wear.
7. **Counterweight:** 2 blocks of 20 kg on the front lower beam, with M10 through the hole grid.

| Characteristic | Value |
| --- | --- |
| Working width | 1440 mm between the plates, flight 1420 mm |
| Feed pusher dimensions | 1600 × 619 × 598 mm (w × l × h), behind the robot: y −566 to −1185 |
| Clearance | hood 48 mm, flap 59 mm and arms 17 mm to the rear tires; flight 15 mm above the floor |
| Mass (model) | 118 kg feed pusher (rotor 28 kg) + 40 kg counterweight |
| Auger | 150 rpm, feed 0.42 m/s along the auger (theoretical 0.65 m/s) |
| Capacity | 13 kg per m of auger, 5.5 kg/s (20 t/h). At 0.30 m/s driving that is up to 18 kg of feed per m of feeding alley |
| Auger torque | 34 Nm nominal, 85 Nm peak at start-up. The shear bolt breaks at 145 Nm |
| Power | 160 W electrical at 5 kg of feed in the auger, 520 W at 20 kg. Maximum 25 A in the animation |

## 4. Design choices

### 4.1 On the side of the fixed wheel motors

The rear wheels are fixed and have no steering stack. There is therefore room behind the wheel brackets, and the
brackets have a flange with holes there. The front wheels have a steering head with a stepper motor, bearings and
threaded rods at (±50, ±75). That head and the steering sweep of ~30° must stay clear (AGENTS.md).

When pushing feed the robot drives with the auger first (towards −y) and the front wheels steer from behind, like a
forklift. The advantage of steering at the back is that the auger stays close to the fence. A small steering
deflection at the back hardly rotates the auger relative to the fence.

### 4.2 Folded hood instead of a round trough

![drive detail](previews/6_drive_detail.png)

- **Sheet:** one sheet of 1440 × 774 mm, 2 mm thick, with 4 bends. The centre line runs from the rear wall (robot side,
  60 to 315 mm high) via an inclined bend to the top plate at 370 mm. Then it slopes down to a lip at
  217 mm, in front of the auger.
- **Clearances:** between flight and hood there is 33 mm or more everywhere. The sloping front bend is 200 mm from the
  centre; the feed rolls against it there and back into the auger.
- **Why 2 mm is enough:** the hood carries nothing. The beam carries the auger via the end plates. The motor plate is
  supported by an upstanding edge against the beam. The hood only holds back the feed and is attached to the plates with
  folded angles. That saves 9 kg compared with 3 mm.

### 4.3 Mounting on the wheel modules, through the four holes

![mounting detail](previews/7_mount_detail.png)

Each side plate of a wheel bracket has an outward-folded 40 × 4 mm flange at the front and the back. In that flange are
**4 M10 holes (Ø10.4) at 100 mm pitch**, at 200, 300, 400 and 500 mm above the ground. The rear flanges of the two
rear wheel modules are at y = −582. That makes 4: inside and outside each rear wheel, at
x = ±283 and ±467.

One arm goes on each flange:
- **Adapter plate:** 50 × 360 × 8 mm, with the 4 M10 × 35 bolts and the nuts on the inside of the flange.
- **Gusset:** 8 mm, on the side of the plate facing away from the tire. 17 mm of clearance to the tire remains.
- **End plate:** 90 × 129 × 8 mm, with 4 × M12 through the beam, in slotted holes.

Why this way:
- **Nothing to drill or weld on the robot:** the same holes are in every wheel bracket. No extra bolts through
  the beams, and the steering heads stay clear.
- **Four arms instead of two:** the load goes into the bracket via both side plates of each wheel bracket. No
  twisting on a single flange.
- **Forces (`fpa_calc.mount_check`):** at 2 × the own weight (shocks) the moment on the flanges together is
  690 Nm. The top bolt gets 516 N of tension. The bearing stress in the 4 mm flange is 3.5 MPa. This is ample.

### 4.4 Foot-mounted motor on the hood

- **Motor:** a coaxial foot-mounted gearmotor (B3), 24 V DC, 550 W, 300 rpm. It stands on the left half of
  the hood, with the output shaft pointing outwards over the side plate. The side plate is only 380 mm high there, so the
  side plate does not need a hole for the shaft. Between motor and auger there is a 15T → 30T chain (i = 2).
- **Motor plate:** 8 mm, with 20 mm slotted holes for aligning the sprockets. The upstanding edge is fixed to the beam with
  2 × M10. This way the chain pull (up to 1.4 kN peak) does not go through the thin hood.
- **Chain tensioner:** the centre distance (300 mm) is fixed. A tensioner on the slack side takes up the stretch: an
  arm on the side plate with a Ø40 nylon wheel inside the loop and a rubber torsion element.
- **Chain guard:** 2 mm, around the sprockets and the chain, on the outside of the left side plate.

### 4.5 Rotor with stub shafts

- **Construction:** the 60.3 × 4 core tube is closed at each end by welding in 2 discs. A 70 mm Ø30 stub shaft goes
  into it, fixed with one pin straight through tube and stub.
  - **Left (drive):** an M6 4.6 shear bolt in a hardened bush, and a keyway for the sprocket.
  - **Right:** M10 8.8.
- **Changing a bearing:** pull the pin, pull out the stub shaft. The rotor does not have to come out of the hood.

### 4.6 Open discharge on the fence side

![open end right (hood hidden)](previews/8_open_end_right.png)

- **Discharge:** on the right there is no full side plate but a bearing plate. It only fills the part behind and above
  the axis, up to under the beam. In front of the axis and below 105 mm height the end is open. The flight runs to 5 mm
  from the plate, so that the feed falls out on the fence side.
- **Feed fence:** in the animation the auger stands 230 mm from the kerb of the feed fence. The feed falls between the
  end of the flight and the fence onto the floor, and forms a new edge there within reach of the cows.
- **Other side of the feeding alley:** with a turnaround at the end of the alley the other fence is on the right side
  of the robot again. One direction of rotation is therefore enough.

### 4.7 Weight, axle loads and counterweight

The feed pusher weighs 118 kg and its centre of gravity hangs 378 mm behind the rear axle (y = −878). The motor is on the
left, so the centre of gravity is also 120 mm to the left of the centre.

| Axle load (kg) | rear | front |
| --- | --- | --- |
| robot alone (assumed 150 kg, centred) | 75.0 | 75.0 |
| with feed pusher | 238.2 | **30.2** |
| with feed pusher + 2 × 20 kg counterweight | 235.1 | 73.5 |

Without a counterweight the front wheels are left with 15 kg per wheel. At a grip of 0.6 they can then take at most 90 N
of side force per wheel. That is too little to steer reliably on a wet, dirty feeding alley. With the
40 kg counterweight on the front lower beam (y = 575) the front axle goes back to 74 kg.

Possible improvement: put the battery or other heavy parts of the robot at the front, then the blocks are not needed.
The right/left load distribution (RL 132, RR 103 kg) comes from the motor being on the left. That is acceptable.

### 4.8 Speed control on motor current

- **Problem:** the capacity is 5.5 kg/s. At 24 kg/m and 0.30 m/s, 7.2 kg/s comes in. That goes well, except
  where the feed lies heavy: then the auger fills up and pushes feed ahead of itself.
- **Control:** the robot measures the auger motor current (filtered, 0.3 s).
  - Below 18 A it drives at 0.30 m/s.
  - Above that it slows down, linearly to 25 % of the driving speed at 30 A.
- **In the animation** the speed drops to 0.18 m/s at the clump and the thick part of the strip. The current then does not
  exceed 25 A, below the motor's nominal 33 A.

## 5. Calculations (`fpa_calc.py`)

### 5.1 Capacity

- **Free cross-section:** π/4 · (0.320² − 0.060²) = 0.078 m².
- **Content per metre of auger:** 0.078 m² × 280 kg/m³ × fill factor 0.6 = **13.0 kg per m of auger**.
- **Speed along the auger:** pitch × speed × transport efficiency = 0.26 × 2.5 × 0.65 = **0.42 m/s**. An open
  auger on the floor does not reach the theoretical 0.65 m/s, because the feed rotates along with it.
- **Capacity:** 13.0 × 0.42 = 5.5 kg/s, or 20 t/h.
- **Per metre of feeding alley:** at 0.30 m/s driving that is **18 kg/m**. More feed per metre means driving slower (§ 4.8).

### 5.2 Torque and power

The feed in the auger (mass m) slides over the floor with velocity (v_ax, −v_robot) relative to the floor.

- **Friction with the floor:** μ·m·g = 0.5·m·g. That friction is divided over two directions:
  - **F_ax:** the side force on the auger, away from the fence. F_ax = μ·m·g · v_ax / |v|.
  - **F_push:** the pushing force against the driving direction. F_push = μ·m·g · v_robot / |v|.
- **Shaft torque:** the power for the transport follows from the CEMA formula P = λ·m·g·v_ax, with λ = 4 for fibrous
  material. From that follows T = T₀ + P / ω.
  - T₀ = 2 Nm for the bearings and the chain.
  - Check: the screw formula F_ax · r_m · tan(α + ρ) gives less. The helix angle at the mean radius is α = 23.5°.
- **Electrical power:** η = 0.9 (gearbox) × 0.97 (chain) × 0.8 (motor) = 0.70.

| feed in the auger | F_ax | F_push | torque | P_el | current at 24 V |
| --- | --- | --- | --- | --- | --- |
| 5 kg | 20 N | 14 N | 7.3 Nm | 164 W | 6.8 A |
| 10 kg | 40 N | 28 N | 12.6 Nm | 282 W | 11.8 A |
| 20 kg | 80 N | 57 N | 23.1 Nm | 520 W | 21.7 A |
| 30 kg | 120 N | 85 N | 33.7 Nm | 757 W | 31.5 A |

The nominal motor (550 W, 17.5 Nm at 300 rpm) gives 34 Nm on the auger. That is enough for about 30 kg of feed in
the auger.

### 5.3 Protection

- **Starting torque:** 2.5 × nominal = 85 Nm. The torsional stress in the Ø30 stub shaft is then 20 MPa (including a
  factor 1.25 for the keyway). C45 allows about 100 MPa.
- **M6 4.6 shear bolt:** sits in double shear on the stub shaft (radius 15 mm) and breaks at 2 × 0.6 × 400 × 20.1 ×
  0.015 = **145 Nm**. That is above the starting torque and far below what the chain and the shaft can take.
  - An M10 8.8 would only break at 835 Nm. That is why it is only on the right, where no torque passes through.
- **Chain 08B-1:** breaking load 18.2 kN. At the starting torque that is a safety factor of 13, at the breaking torque 7.6.
- **Software (recommended, not yet built):** the controller stops the motor if the current stays above 35 A for longer than 2 s.

### 5.4 Rotor deflection

The 60.3 × 4 core tube (I = 2.8·10⁵ mm⁴) spans 1.5 m between the bearings. The load is the own weight plus half
the circumferential force at the starting torque. With a pinned support that gives a deflection of
**0.9 mm** and a bending stress of 23 MPa. A continuous shaft is therefore not needed.

### 5.5 Forces on the robot and the reaction (`robot_reaction`)

The starting point is static equilibrium of robot + feed pusher (+ counterweight).

- **Wheel loads:** from the moments about the x axis (length) and the y axis (transverse), with the weight of all parts.
  - F_push acts 60 mm above the floor. That pushes the nose down slightly.
  - F_ax gives a small transverse load transfer.
  - That transverse load transfer is divided per axle in proportion to the axle load.
- **Side forces:** the side forces of the floor together cancel F_ax. Their moment about the vertical axis cancels the
  moment of F_ax (at 1.1 m behind the robot centre) and of F_push.
  - The auger is far behind the rear axle. The rear axle therefore has to deliver **more** side force than F_ax.
  - The front axle pushes the other way: approximately F_rear ≈ 1.45 · F_ax and F_front ≈ −0.45 · F_ax.
- **Skew and steering:** tires deliver side force through a small slip angle. The tire stiffness is 0.12 per degree
  per N of wheel load.
  - The rear wheels are fixed. The robot therefore runs at a small angle ψ = F_rear / C_rear.
  - The front wheels steer against it with δ = F_front / C_front − ψ.
- **Drive force per wheel:** F_push in proportion to the wheel load, plus 3 % rolling resistance.

**Result of the animation** (24 kg/m feed, 4 m feeding alley):

| | range during the feed pushing |
| --- | --- |
| feed in the auger | 1 – 23 kg, of which up to 15 kg above capacity (pushed ahead of the auger) |
| shaft torque, current | 3 – 27 Nm, 3 – 25 A (max. 598 W) |
| force of feed on auger | up to 105 N sideways (away from the fence), up to 52 N against the driving direction |
| floor side force | rear axle up to 152 N, front axle up to −46 N |
| robot skew / steering correction | up to 0.53° / up to −1.05° |
| grip utilisation (max. over all wheels) | 13 % |
| driving speed | 0.30 m/s, automatically back to 0.18 m/s at the clump |
| picked up and laid against the fence | 92 kg |

What this means:
- **Forces:** the forces on the robot are small. Grip is used for at most 13 %. The feed itself is light; what
  counts is the **leverage**: 105 N at 1.1 m behind the centre demands 150 N from the rear wheels.
- **Skew:** the robot runs about half a degree skew and the front wheels steer one degree against it. A GNSS or
  line follower that holds the course does that automatically.
- **Current:** the auger motor is the limiting factor, not the grip. That is why the speed is controlled on the motor
  current (§ 4.8).

## 6. Assumptions (not measured)

| Assumption | Value | Influence |
| --- | --- | --- |
| Robot | 150 kg, centre of gravity in the middle, 450 mm high | axle loads, counterweight |
| Bulk density of feed | 280 kg/m³ | capacity, height of the strip |
| Friction feed–concrete | 0.5 | F_ax, F_push |
| Auger resistance factor λ | 4 | torque, current |
| Transport efficiency / fill factor | 0.65 / 0.6 | capacity |
| Tire stiffness, grip | 0.12 /° per N, 0.6 | skew, steering correction, grip utilisation |
| Rolling resistance | 3 % | drive force |
| Gearmotor | 14 kg, B3, coaxial, 300 rpm | mass, position |
| Feed in the feeding alley | 24 ± 6 kg/m, 600–950 mm from the fence | animation |

## 7. Open points

- **Measure:** measure the robot weight and centre of gravity. Then determine the counterweight again with `fpa_calc.axle_loads()`,
  or move the battery forward.
- **Calibrate:** calibrate λ and the transport efficiency against the current at a known quantity of feed (scale and a
  current clamp).
- **Height:** determine the right floor clearance of the flight (now 15 mm) and the flap on an uneven floor. It can be adjusted
  with the slotted holes in the end plates.
- **Wheel bracket:** check whether the rear flange of the wheel bracket is straight enough for a flat adapter plate.
  If not, use a 1 mm shim.
- **Safety:** consider a bumper or contact strip on the hood lip (animals, people). The auger leads.
