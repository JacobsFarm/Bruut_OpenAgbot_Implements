# Yield estimator (simple): why it is built like this

## Size from RGB, height from depth, light from flashes

A head's weight follows its size (roughly d^2.5 for a cauliflower curd). At 0.25 mm per pixel the diameter is known to
better than 1 %, so the error per head is the natural spread of weight at a given size (~12 %). Over a row or a field
those errors average out: the sum of 1000 heads is known to ~0.4 % once the size-to-weight curve is calibrated with a
few weighed heads. The ToF cameras give the height of each head above the leaves, which separates a curd from leaves
of the same colour and helps the ripeness class. LED flashes, much brighter than the sun during their ~1 ms, give the
same images in sun, shade and dusk.

## One camera per row

Four 50 degree cameras at 1.33 m cover 0.96 m each at the crop, more than the 450 mm row spacing, so each row is seen
by its own camera and overlaps its neighbour. With 10 frames per second each plant is in ~5 frames at 1 m/s; the best
frame is used, the others confirm the count.

## Mole-mapper bridge

The bridge is already a light, stiff aluminium bar at 1.4 m in front of the robot, clear of the GNSS dome and the
steering stacks. Only the sensors differ.

## Estimated, not measured

- Head size-to-mass curve (a = 2.5e-3 g/mm^2.5) and its spread (12 %), head diameters and crop height
- Camera and ToF fields of view, pixels and depth noise, frame rate, sensor and LED power (120 W)
- Row spacing (450 mm) and plant spacing (500 mm)
- Rolling resistance (0.06), robot mass and battery energy
- Not modelled: computer and cables, the image model per crop (needs training data)
