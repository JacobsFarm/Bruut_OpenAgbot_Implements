# Crate carrier (simple): why it is built this way

## A deck between the steering stacks and over the rear wheels

- The front wheel units carry the steering stack (bearing plates, gearbox and stepper up to z 1032) from y 405; the GNSS
  dome sits between them. The deck stops at y 380 with a headboard in front of the crates, and reaches back to y -620
  over the rear wheel units. 1300 x 1000 mm, loading height 757 mm (about a table: pickers put a crate on it without
  bending deep).
- Three bearers 40 x 40 across the upper beams (4 x M10 each), placed between the frame bolts of the rear units
  (they stick out to z 705: 34 mm under the deck). Side rails 40 x 40 at the edges, 18 mm film-faced plywood on top.
- 2 x 2 crates of 600 x 400 per layer, 2 layers: 8 crates. Angle guides at the sides and rear and a flat divider keep
  them in place, the headboard stops them sliding forward onto the steering motors, 2 ratchet straps hold the stack.

## Payload and stability

- The crates sit nearly centred over the axles (cg y -47): with any crop 47..49 % stays on the front axle.
- The rated payload on top is taken as 150 kg (estimated): 8 crates of apples (141 kg) or cabbage (125 kg) fit,
  potatoes (157 kg) are just over: 7 crates.
- With 2 layers of apples the cg is at 714 mm: static tip angle 27.7 degrees sideways (track 750), 34 degrees
  backwards. Fine on field roads; across steep slopes drive with 1 layer.
- A 10 % / 10 degree slope with apples needs 802 N, the motors give 1100 N continuous (margin 1.37).

## Follow-me and GNSS

- Two UWB anchors at the top corners of the headboard give range and bearing to a tag on the picker (follow at a set
  distance); fixed shuttle routes run on RTK. A stop / go / follow button box sits at the rear corner, where the picker
  stands.
- A loaded stack (top at 1357 mm) shades the GNSS dome (z 740) towards the rear. The antenna is moved to a O30 mast on
  the headboard at 1500 mm.

## Tool and material cart

The same deck carries tools, stakes, nets or a 200 l IBC-style water tank (200 kg is over the payload: 150 l). The
divider and straps are removable. That covers the *tool and material cart* idea.

## Shuttle

150 m to the field edge at 1.2 m/s loaded, 1 min to unload, back at 1.8 m/s: 268 s per trip, 107 crates per hour
(1.7 t of apples), ~19 Wh per trip: ~100 trips on the robot battery.

## Estimated, not measured

- Robot mass 160 kg, cg midway between the axles at 380 mm high; payload rating 150 kg on top
- Net crop per crate: strawberries 4.5, apples 16, potatoes 18, cabbage 14 kg; crate 1.6 kg empty
- Rolling resistance 0.06, grip 0.45; usable robot battery 1.9 kWh (as in solar/)
- Unloading 60 s per trip, trip length 150 m
