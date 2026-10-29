# Why combination V3 is laid out this way

## One pump, two halves

Two liquids that may not be mixed in a tank each need their own supply, but not their own pump: the roller pump is
modular, so 10 sections on one shaft give 5 for A (right) and 5 for B (left). A plug in the middle of the manifold
separates the halves, each half gets its own ½" inlet from its own tank. One motor, one speed control: both liquids
follow the driving speed with the same dose per row. If the ratio has to differ, a different tube bore in one half
is enough (the output per revolution scales with the bore).

The 10-section pump is 945 mm over all; it stands 10 mm left of the centre (pump x −42.5 instead of −32.5) so the
centre section (A0) comes out 12 mm closer to its way past the actuator lugs.

## Right half A, left half B

Rows 0 … 4 run from left to right. Whatever channel feeds whatever row, some hoses of each liquid have to cross
the middle. With A on the right half, the A hoses of rows 0 … 2 go left and the B hoses of rows 3, 4 go right. Keeping
the channel order the same as the row order inside each half keeps the number of crossings low.

## Three layers

A hose that crosses another one in the top view has to pass above or below it. The pump outlets point down and back
at 52°, and the robot beam with the actuator bracket is only 70 mm behind them, so there is no room to sort the
hoses there. They first go straight back over the beam, each in its layer, and only then sideways:

- **B0 … B2 low (714)** and **A0 … A4 above them (736)**: the arc out of the pump flattens at that height (radius 39
  for A, 96 for B).
- **B3, B4 high (770)**: they must cross x 0. Low over x 0 was tried first (B at 714): working, that is fine behind
  y −690, but lifted the actuator tilts up and touches the hoses up to y −790, and from y −782 the lifted mast
  (top z 740) and links are in the way. Over everything (z 770, over the lugs at 755) works at every lift. The hose
  first flattens and then climbs in an S of two 45° arcs (R 30).
- Inside a layer the sideways moves are nested: the hose that has to go furthest goes first. Small shifts (B0, B1, B2,
  A3) go diagonally and are in their lane before y −760, ahead of the lifted mast.
- All hoses stay in their layer up to y −880. When the descent started earlier, an A hose came down through the B
  layer while a B hose was still moving sideways there.

## Lanes

Behind the robot each row has an A and a B lane 26 mm apart (the curve overshoots about 5 mm where it turns into
the lane; 20 was too little). The lanes stay out of the headstocks and mast plates (x ±125 … 175). In row 2 they are
spread further (x −72 and −112): A2 passes the actuator with 63 mm to spare.

## Over the knife

Each hose comes down in the knife plane onto its own tube end: A straight up from the end of tube A, B slanting back
along the 45° end of tube B. The ends of the double knife are 61 mm apart, so the two hoses and their clamps fit.

## Checks

See README: the hoses are swept in short pieces and checked with surface points, because booleans with the swept
hoses took tens of minutes or hung FreeCAD.
