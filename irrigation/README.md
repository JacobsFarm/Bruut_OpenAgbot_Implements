# Irrigation for the Bruut

Irrigating grassland with a robot, from a pump at the ditch, by **flooding at low pressure** rather than spraying at
high pressure: little energy, no wind drift, no evaporation in the air.

| | Variant | Contents |
| --- | --- | --- |
| [Stationary pump + hose reel](stationary%20+%20roller/README.md) | `stationary + roller/` | FreeCAD model: reel with 150 m of 3" lay-flat hose on the robot, pinch rollers, outlets every 2 m; hydraulics, cycle and capacity, animation of one strip; why: [RATIONALE](stationary%20+%20roller/RATIONALE.md) |
| Direct pump | `direct pump/` | not worked out yet (pump on the robot, water from a tank or a hydrant) |

![the hose reel on the robot](stationary%20+%20roller/previews/1_full_reel_iso_on_robot.png)

![animation: one strip](stationary%20+%20roller/previews/animation_one_strip.gif)

## Idea

A petrol pump stays at the ditch. The robot carries the hose, lays it out over the length of the field, lets it
irrigate a strip, and winds it up again. Strip by strip it works over the field, day and night, and from one pump it
can serve several fields.

## The problem: water is heavy

Low pressure with a lot of water needs a hose with a big bore, and a big bore holds a lot of water:

| Hose (150 m) | Water inside | Friction loss at 10 m³/h |
| --- | --- | --- |
| PE 40 mm | ≈ 125 l | ≈ 4.7 bar |
| PE 63 mm | ≈ 310 l | ≈ 0.5 bar |
| 3" lay-flat (Ø76) | ≈ 680 l | ≈ 0.1 bar |

The standard robot weighs 161 kg; it cannot carry a full hose, and dragging one over wet grass takes more grip than
it has. So the water must never be on the robot.

## Options considered

| | How | Verdict |
| --- | --- | --- |
| Hose reel with a swivel on the robot | the water flows through the swivel into the coil while winding (as a classic hose reel) | only a short, thin hose fits: ≈ 5 m³/h, 50 m |
| Fixed reel at the pump, robot pulls the hose | classic hose reel turned around, robot carries the distributor | the robot must pull out the hose; reel and pump must be towed to the next field |
| **Lay-flat hose, laid out empty, wound empty** | robot lays the hose, water on, drain, robot winds it up | **chosen**: the robot never carries water, big bore, ≈ 0.1 bar loss |

How the water leaves the lay-flat hose:

| | How | Verdict |
| --- | --- | --- |
| a. Perforated hose (rain hose) | holes over the whole length | narrow strip at low pressure, the end gets less water |
| **b. Outlets every 2 m** | small restrictor + flat drop tail, the water floods out at the ground | **chosen**: even (CU ≈ 99 % on level ground), no drift, closest to flooding |
| c. One outlet at the robot | the robot carries a boom and stands still | water only where the robot stands, moves often |
| d. Flooding from the head of the field | free outflow, water runs over the surface | needs a flat, slightly sloping field |

## How one strip goes

1. The hose is coupled to the hydrant (3-way valve at the pump). The robot drives into the field; the empty hose pays
   out at the rear.
2. The pump starts. Every 2 m an outlet floods ~8 m² (2 m × 4 m) until the 25 mm gift is in: ≈ 100 min at 15 mm/h
   infiltration. Pinch rollers on the robot keep the reel dry.
3. Pump off, valve to drain, the hose runs empty.
4. The robot reverses and winds the flat hose; the pinch rollers squeeze it out.
5. Next strip 4 m further. The first 20 m of hose have no outlets and curve over the headland from the hydrant.

One robot keeps up with 3.5 mm/day of evaporation on about 4 ha (see the
[variant README](stationary%20+%20roller/README.md) for all figures).

## Next steps

- Measure the infiltration and how far the water spreads from one outlet on the real field.
- Build and test the outlets: do they wind flat and stay tight in the pinch rollers?
- Automatic coupling of the hose to the hydrants, so the robot can go to the next field without a person.
- A smaller pump (2" petrol, or electric with solar) at the ditch: the 3" pump runs almost at idle.
