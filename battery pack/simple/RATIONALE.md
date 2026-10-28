# Battery pack (simple): why it is built this way

## Where: under the upper beams, between the wheels

- The space between the front and rear wheels under the upper beams (x 300..470, y -255..255, z 320..600) is free on
  both sides: the tyres start at y +-285 (the steered front tyre at y 289), the wheel brackets sit at the axles. Weight
  there is low (cg 438 mm) and right between the axles: it does not change the front / rear split and adds grip.
- Hanging the pods on the upper beams keeps the lower beams, the top of the robot and the rear / front toolbars free:
  the pods combine with the push blade, the toolbar implements, the crate carrier and the counterweights.
- Not with the grassland aerator: its roller frame uses the same space between the axles.

## Pod

- 16 prismatic LiFePO4 cells 50 Ah in one row (16S, 51.2 V, 2.56 kWh), a 16S BMS, Anderson SB50 connector: the same
  48 V as the robot. LiFePO4 because it is safe outdoors and tolerates the vibration; 98 Wh/kg for the whole pod.
- 26 kg: two handles, a pod is lifted by one person (or two) and hung on two hangers with hook strips, then locked with
  two over-centre latches. No tools, a swap takes ~5 minutes; a second set charges in the shed (1 kW: ~2.8 h).
- Hangers: flat bar 40 x 8 with spacer blocks, 2 x M10 up through the two upper beams of that side. The hooks go up
  beside the bar and over it, so the pod cannot slide off sideways.

## Runtime

With the robot's own ~1.9 kWh usable (2.4 kWh, as assumed for the solar canopy) and the two pods (2 x 2.3 kWh usable):

| Implement | Load | Robot only | With pods |
| --- | --- | --- | --- |
| Inter-row hoe | 1.08 kW | 1.8 h | 6.0 h |
| Grassland harrow | 1.32 kW | 1.4 h | 4.9 h |
| Grassland aerator | 0.58 kW | 3.3 h | 11.2 h (not together, see above) |
| Three-point hitch + cultivator | 1.14 kW | 1.7 h | 5.7 h |
| Push blade | 0.94 kW | 2.0 h | 6.9 h |
| Crate carrier shuttle | 0.31 kW | 6.1 h | 21.0 h |

The extra 52 kg add ~230 N of grip (and ~30 N rolling resistance on grass): the hoe and the cultivator get a better
pull margin.

## Estimated, not measured

- The robot's own battery 2.4 kWh (1.9 usable, as in solar/) and its base load 60 W (not in the model)
- Implement loads taken from their own calcs (drive + implement at their working speed)
- Cell 148 x 27 x 130 mm, 1.05 kg; usable depth of discharge 90 %; charger 1 kW
- Combining the pods with the robot's battery through a pack combiner (diodes or a DC/DC per pod): to be chosen with
  the robot's power electronics
