# Soil moisture sensor placer (simple) - rationale

## Why the soil sampler's Z axis

Pushing a sensor 300 mm into the soil is the same job as pushing a gouge: a stiff vertical axis between the wheels,
where the whole weight of the robot is available as reaction. The soil sampler has exactly that (ball screw, NEMA23,
SBR20 rails); its carriage takes a gripper instead of the gouge. The idea list suggested the field marker's XYZ stage,
but that has no push force.

## Sensor

- **Stem O20 x 300 with a cone**: the push force grows with the tip area; O25 needed ~1200 N in moist grass, more than
  the weight gives. O20 needs ~850 N (moist grass) to ~1320 N (dry grass). Two rings at 100 and 250 mm give the root
  zone of grass and of most arable crops.
- **Knob on top**: one simple shape for the gripper, both for placing and for picking up. A magnet or a tether
  (idea list) would need a second mechanism; with GNSS (RTK, 2 cm) the robot stands over the knob again.
- **Radio and battery**: LoRa to a farm gateway (~2 km in open field) or to the robot when it passes; measuring every
  30 min and sending 4 times a day uses ~0.6 mAh/day, so 2 AA lithium cells last longer than their shelf life.

## Magazine

A star of 6 fork arms behind the Z axis, turning about its own shaft from the rear bridge. The sensors hang in the
forks by their caps; the slots open outward, so the gripper lifts the whole sensor out (stem included) before the
star turns half a step (30 degrees) and leaves a gap under the gripper for the push. With the gripper parked the star
can turn freely. 6 sensors per trip (3 ha at 2 per ha) keeps the star within the wheels (47 mm to the rear wheel
bracket); 2 per ha is one per management zone, the usual density for irrigation and N advice.

## Push force

70 % of the weight of robot and placer (~1350 N) may be used before the wheels unload; the ball screw gives ~1470 N
at the NEMA23's torque. That covers all four soil states of the soil sampler; dry grass is the limit, so placing is
done in spring when the soil is moist (when the sensors are needed). The pull-out at the end of the season needs
only the side friction (~380 N).

## Estimated, not measured

- Cone resistance per soil state and side friction (from the soil sampler), 70 % weight use
- Sensor: currents (sleep 8 uA, measure 12 mA x 2 s, transmit 45 mA x 1.5 s), sends per day, mass (0.35 kg),
  radio range (2 km), shelf life of lithium AA (10 years)
- Gripper mass (0.6 kg), magazine motor (0.4 kg), push speed (10 mm/s), star step time (3 s), GNSS settle (2 s)
- Sensor density (2 per ha), robot mass (160 kg)
- Not modelled: the sensor electronics, the gripper mechanism inside its body, the wiring, the LoRa gateway
