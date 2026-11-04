# Line marker (simple): rationale

## Where the nozzle sits

The Bruut has fixed rear wheels and steered front wheels. For such a vehicle the middle of the rear axle moves along
its own path without any side slip: in a curve it runs on the circle of radius R = wheelbase / tan(steering). Every other
point of the robot runs on a different radius. With the nozzle **on the rear axle line**, the path planner can plan the
path of the nozzle directly; no offset tracking, no "tail swing" at the start of a curve. A nozzle behind the robot
(like the field marker) would need the controller to plan a path for the axle that puts the nozzle on the line, and on
a tight curve it would swing outward.

Under the rear axle there is room: between the rear tyres (x ±325) and below the spot-sprayer pump (z 480), the
belly is free from z ~400 down. The rear tyres stand beside the line, never on fresh paint, because the line runs
between them (at x 0 ± 170).

## Why a slide

1. **Cross-track error**: RTK and the steering loop keep the robot within a few centimetres of the line; a straight
   line on a pitch must be within ~1 cm. The slide reads the position error at the nozzle and corrects it at 100 Hz,
   far faster than the steering can.
2. **Tight arcs**: at 30° the robot's tightest circle is 1.73 m; the football corner arc is 1 m. With the slide the
   robot drives straight along the chord of the arc and the slide moves the nozzle out by the arc's sagitta. A 90° arc
   of r 1 m has a sagitta of 293 mm; with the chord shifted half of that, the slide moves ±147 mm around its middle and
   the stroke 340 leaves 20 mm per end for the cross-track correction. Arcs between 1.02 and 1.73 m are drawn by
   steering a little and sliding the rest.

The stroke is limited by the wheel brackets (inner face x 261): module, motor and shroud stay inside them over the
whole stroke (checked: `check_poses()`), and the brush keeps 74 mm from the tyres.

## Belt module, upside down, motor folded back

A belt module is fast (1 m/s), cheap and quiet; a ball screw would be more precise than needed (paint lines are
±5 mm) and slower. It hangs upside down, carriage under the body, so the head hangs straight from the carriage. The
motor is folded back in front of the body with a 1:1 belt box: an inline motor would stick out 140 mm beyond the drive
end and hit the wheel bracket.

The chain carries only the paint hose and the valve cable. It lies behind the module, so a drip from the hose never
falls on the module or the belt.

## Paint system: the spot sprayer's

Line paint is a water-based pigment slurry. It settles in the tank within hours, so it must be stirred; the spot
sprayer's diaphragm pump (11 l/min) and pressure regulator send 10 l/min back to the tank through the bypass, which is
enough hydraulic agitation for the low fill. The 50-mesh filter suits pre-diluted line paint. Using the spot sprayer's
complete paint path means no new tank, cradle, pump or control box; only the head, the slide and the rails are new.

The 120 l tank is bigger than needed (a field takes ~10 l). It is filled to ~40 l: 3-4 fields per fill, 52 kg of
paint, and the robot stays at 43 % front axle load. A smaller tank would be the first change for a dedicated machine.

## Nozzle and shroud

An **even** flat-fan tip (E) lays the same amount over the whole fan width, so the line has a sharp edge and constant
whiteness; a normal flat fan tapers off at the edges (for overlapping on a boom). 4002E at 3 bar gives 0.79 l/min: at
1 m/s and 100 mm that is 0.13 l/m², a normal wet film for a fresh line (estimated). The fan lies across the line (along
x), so the line width is the fan width at the tip height: 2 h tan 20°.

The valve sits directly on the nozzle body: the dead volume after the valve is a few ml, so the line ends do not drip.
Its opening delay (~25 ms) would make a line start 25 mm late at 1 m/s; the controller opens it that much earlier
(look-ahead), the remaining jitter is ±3 mm.

The shroud and the brush skirt keep wind away from the fan (a fine fan drifts already at 2 m/s wind) and catch the
edge mist.

## Accuracy

The robot's RTK antenna is 1075 mm in front of the nozzle and 740 mm above the ground. A heading error of 0.15°
moves the nozzle 2.8 mm sideways; a roll of 0.2° after IMU correction moves the antenna 2.6 mm. Uncorrected, a 3° side
slope would move the line 39 mm: the IMU tilt correction is necessary. With RTK 8 mm the total is ~9 mm 1σ, ~18 mm for
95 % of the line. A better result needs a second antenna right above the nozzle (as on the field marker) or a total
station.

## Time

On a football field the robot paints 717 m of line in 27 elements: ~13 min painting, ~4 min line ends (stop, turn,
line up), ~2 min transit, ~19 min in all. Re-marking is usually weekly, so one charge (~14 fields) and one fill
(~4 fields) cover a club with several pitches.
