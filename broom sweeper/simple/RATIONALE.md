# Broom / sweeper (simple) - rationale

## Why on the push-blade toolbar

The push blade already has a front toolbar, lift arms, a float slot for the actuator and a king pin with angle lock.
An angle broom needs exactly that: a lift, a float so it follows the floor, and an angle to throw the material aside.
So the broom is a second head on the same king pin; the push-blade files are imported, not copied, and a change there
(toolbar, arms) comes through here.

## Brush

- **O400 x 1000**: the common size of compact angle brooms; 1000 mm covers the robot track (850 over the tyres) at
  25 degrees (906 mm across). A larger brush (O500+) would not fit between the king pin head plate and the floor without
  moving it further forward.
- **400 rpm, 8.4 m/s tip speed**: within the usual 6-10 m/s for road and yard brooms; faster throws dust, slower leaves
  wet material.
- **PP bristles**: wear-resistant, not rusting, fine on concrete and pavers. Steel-wire strips for moss and ice are an option.
- **Bottom turns forward**: the brush lifts the material forward and, angled, to the side; the reaction pushes the
  robot back by ~75 N, small for the hub motors.

## Castors and float

The head runs on 2 castors and the actuator floats (rod in the slot of the carrier lug, as on the push blade), so the
bristle deflection (10 mm) is set by the castor height, not by the actuator. Castors swivel, so the angled head does not
scrub. Wear of the bristles: change the spacer under the castor plate (20 mm in steps).

## Weight and ballast

The head (83 kg) hangs ~1.3 m in front of the robot centre, 0.8 m in front of the front axle. Lifted, this is more
moment than the robot (160 kg at the centre) gives back: the rear axle goes to -4 kg, the robot would tip on its front
wheels. Working, the castors carry ~130 kg and the rear axle has 54 %, so sweeping and driving with the head down are
fine. Choices:
- normal: drive with the head down and the brush stopped; the castors are rated for this;
- short lift over a kerb: 4 counterweight plates (44 kg) on the rear stacks, rear share 12 %;
- lifted transport: 9 plates (99 kg, the most the rear stacks take), rear share 25 %.
A lighter head (aluminium end plates, plastic core) would help but not solve it; an advanced variant could put the
brush under the robot or pull it from a rear hitch.

## Drive

1000 W BLDC at 48 V from the robot battery, with a 1:5 gearbox and a 1:1.5 HTD belt. The belt allows a different brush
speed by changing one pulley, and slips less than a V-belt in wet conditions. The motor sits inside the end plate above
the hood (out of the dust, and the head stays 1185 mm wide).

## Power

Bristle friction (150 N at mu 0.5, 15 Nm at 400 rpm) is ~630 W, throwing the material is small (8-24 W), windage
~100 W: ~740 W mechanical, ~910 W electric. With ~220 W for driving, 1.9 kWh lasts ~1.7 h, ~4900 m2 angled.

## Estimated, not measured

- Bristle force on the floor at 10 mm deflection (150 N per m), friction of PP on concrete (0.5), windage (100 W)
- Bulk density of the bristle body (13 % fill of PP) and so the brush mass (26 kg)
- Throw speed of the material (half the tip speed) and the material loads per m2
- Rolling resistance of the robot (0.03) and the castors (0.04) on a yard floor
- Robot mass (160 kg) and centre of gravity (centre), usable battery energy (1.9 kWh)
- Motor and gearbox mass (6.5 kg), actuator mass (3.4 kg) and speed of the 3000 N version
- Least rear-axle share for a short lift (10 %) and for transport (25 %)
- Not modelled: castor and guard bolts in detail, dust suppression (a water spray bar is an option), a collector bin
