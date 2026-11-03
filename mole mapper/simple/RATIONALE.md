# Mole and tunnel mapper (simple): why it is built like this

## Cameras for hills

A molehill is a 250-500 mm mound of bare soil on green grass: easy for a camera. The hard part is *fresh* versus old.
Fresh soil is darker and moister, and has a different temperature than the sward (cooler on a sunny day, warmer on a
cold morning), so a small thermal camera next to the RGB cameras helps. Comparing with the map of the last pass is the
surest sign: a hill that was not there last week is fresh. At 1.33 m height three 50 degree cameras cover 2.5 m, more
than the robot width, at 0.3 mm per pixel; that is far more than needed, so the cameras can be cheap.

## Penetrometer for tunnels

Ground-penetrating radar can see tunnels but is heavy, expensive and poor in wet clay. The soil compaction meter
already pushes a cone into the soil and logs the force every 0.3 mm: a cone that passes through a 50 mm tunnel loses
its resistance for ~170 samples, a clear signal in the 50-250 mm depth where moles dig. The robot stands still while
probing, so its weight is the reaction, as for the compaction map.

A ring of points around a fresh hill finds the tunnels that lead to it. With 16 points 118 mm apart a 50 mm tunnel that
crosses the ring twice is hit ~85 % of the time; 8 points would save half the time but find only ~42 %. Probing is
slow (~7 min per hill), so only one in four fresh hills is probed: the tunnel directions between the probed hills are
enough to place traps.

## Camera bridge on the front beam

The posts stand on the front outer lower beam outside the GNSS dome and inside the steering stacks, the bar at 1.4 m
is above everything on the robot. Aluminium keeps the bridge at ~8 kg.

## Estimated, not measured

- Hill size (250-500 mm), hills per ha (120) and fresh share (30 %), tunnel diameter (50 mm) and depth
- Camera field of view and pixels, camera masses
- Time to drive between probe points (8 s), logging rate (100 Hz)
- Rolling resistance (0.06), camera and computer power (35 W), robot mass and battery energy
- Not modelled: the computer and cables, the image model for fresh hills (needs training data)
