# Solar canopy: rationale

## Idea
A flat canopy of 2 (or 3) panels on top of the robot charges the battery during work. It is bigger than the robot
on purpose: panel area is the only thing that gives energy, and the robot is only 0.85 m wide. The panels
sit high (underside z 1530) so implements, crops and the hybrid train stay below them.

## Layout
- **Base** like the hybrid (long tubes on the 50 mm grid, M10 x 130 with spacer sleeves). Posts at x = ±375, between
  the two bolt rows, so the bolt heads stay clear. The base is the same as the hybrid, so the canopy can be seen as
  a roof above it: the hybrid is at most z 1155, the panels start at 1530. Not checked together in one model.
- **Steering stack:** the zone x > 295, |y| > 405 up to z 1032 is kept free: stringers end at y = ±380 and the
  y-braces run inwards (from the stringer middle up to the post), not outwards.
- **Overhang:** panels 2040 wide (±1020). Rails at x = ±375 carry the cross members; the overhang is held by 4 struts
  D25 from the end of the long tubes. Cross members are 40x40x3 and the stress is tiny (4 MPa); the frame is
  sized by stiffness and by the wish for simple parts, not by strength.
- **Panels** are bolted through their long side frames (M8, 15 mm from the edge) into the cross members, 2 per
  panel side, 8 in total.
- **GNSS:** an antenna under the panels sees no sky. So the antenna is on a D25 mast on the front cross member,
  through the 40 mm gap between the panels. The robot's own antenna is hidden in this model only (robot is read only).
- **Flat:** no tilt. The robot drives in all directions, so a tilt towards the south does not work; a flat
  roof loses about 10-15 % in NL compared with the optimum tilt and has no problem with wind.

## Sizing (estimated)
- 2 x 320 Wp. Yield per kWp per day by month (flat, NL): 0.5 (Dec) to 4.8 (Jun), times derate 0.75 for MPPT,
  cables, heat, dirt and shade.
- 640 Wp is only a fraction of what the drive needs (900 W light, 2.2 kW heavy): the canopy extends the battery,
  it does not replace the hybrid. At 900 W a battery of 1.9 kWh lasts 2.1 h, with solar at noon 3.7 h. With a
  3rd panel the area is 4.95 m2 (960 Wp) but the width becomes 3.08 m: only useful on open ground.
- Wind: 20 m/s gust, 245 Pa. Uplift 808 N on the roof against 240 kg of robot + canopy (2.4 kN weight). Side force
  243 N at roof height gives a tipping safety of 1.8 over the outer tire edge. A bigger canopy or higher centre of
  gravity needs ballast low in the robot or tie-down at high wind.

## Choices
- Generic panel, not a brand. Aluminium frame 30 mm wide, cell plates only for the picture.
- MPPT charge controller instead of PWM: panel voltage differs from the 60 V battery, MPPT gets about 20 % more.
- Frame is 40x40x3 for the canopy and 50x50x3 for the base (hybrid parts), welds are not drawn.

## Not modeled
Cables and connectors (MC4), fuses, panel tilt, rain run-off, cleaning access, shade from implements and from the
mast, the roof as a mount for cameras, the hybrid together with the canopy in one model.
