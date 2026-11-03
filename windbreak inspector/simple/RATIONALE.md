# Windbreak and tree-row inspector (simple): why it is built like this

## Lidar for the shape, cameras for the state

Photos alone are hard to compare between visits (light, shade, season). A 2D lidar that scans a vertical plane across
the row gives the same numbers every time: height, width, density (share of returns inside the hedge) and gaps,
regardless of light. The cameras add what a lidar cannot see: dead or brown leaves, broken branches, bark damage,
flowering and fruit. Shade at row ends is handled by the stereo cameras' exposure; the lidar does not care.

## Stereo pair for per-tree identification

A tree only gets a status line if it can be found again. The vertical stereo pair measures the distance to each trunk
(+-1 mm at 1 m), which with the robot's GNSS and heading gives every trunk its own position. The next visit matches
trunks by position, not by appearance.

## Head at 2.1 m, nothing in the row

At ~1 m from the row the lidar's 270 degrees reach straight up, so a 6 m tree is scanned to the top (23 mm between
points there). The cameras at 1.9-2.2 m see the hedge from 0.8 m up; below that, the lidar profile covers the base.
Nothing reaches into the row, so branches cannot catch anything.

## Fence-inspector mast

The mast and base plate already stand where a sideways sensor needs to be (right side, between the axles, outside the
steering sweep). An extension tube slides into the mast top; the lead screw and arm stay off.

## Estimated, not measured

- Lidar field of view, resolution and rate, camera fields of view and pixels, stereo disparity error (0.25 px)
- Masses of the head (aluminium box at 25 % fill), lidar (1.2 kg) and cameras
- Row distance (~1 m to the row centre line), tree heights (2-6 m)
- Rolling resistance (0.06), sensor power (40 W), robot mass and battery energy, design wind (15 m/s)
- Not modelled: computer and cables, the image models for the status classes
