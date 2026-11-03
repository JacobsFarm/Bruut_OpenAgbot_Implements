# Battery rack MBH3+: why it is built this way

## The battery

- MBH3+ (offer 46325020: 14S 48 V 50 Ah, normally-off BMS): 51.1 V nominal, 2.56 kWh, 60 A continuous / 100 A peak,
  up to 16 in parallel with master/slave hot-swap over CAN (normally-off type only). Same 48 V as the robot.
- Size from the vendor STEP: 265 x 82 x 383 body, 409.6 with the handle; the AS150U socket sits beside the handle on
  the top face. The placeholder keeps only that outer shape, so it is light to use in other models.

## Open rack, no box

- The MBH3+ is a drop-in battery: its own PC/ABS / alu housing (IP53-64 depending on options), a handle on top, the
  connector on a cable. A closed box around it adds weight, hides the status LEDs and traps heat; it only needs to be
  held. So: a tray, guides and a hold-down bar.
- The tray holds the bottom (side lips 40, rubber mat), the side guides at 190 mm and the HDPE separators keep the
  batteries upright and apart, the end frames stop them along the rack, the hold-down bar on the tops (rubber strip)
  keeps them from jumping out on bumps. One star knob opens the bar for all slots.
- The bar lies right of the handles (x 95..125, handles x +-61, socket at x -94): it does not cover the handle or the
  plug, so a battery is unplugged and lifted straight out.
- Rain: the battery is not watertight (IP53 is the low end). With the well concept the frame and an implement above
  give some cover; for top or saddle a simple rain cap over the rack (or the IP64 option from BatteryLabs) is wise.

## Or a closed cabinet, batteries lying

For when the batteries must be out of rain, dust and sight (or locked), a closed alu cabinet is the alternative:

- **Lying flat** (82 high per battery) instead of upright (410): a level per battery of 100 mm, so the cabinet grows
  in height, not in footprint. The mount (rails at y +-200 under the beams, or y +-150 over them) stays the same for
  2, 3 and 4; the levels bolt on top of each other with a flange ring.
- **A door per level**, hinged at the bottom: open it and it is the ramp the battery slides out on by its handle,
  plug first. Only one battery is open at a time, the others stay closed and connected (hot-swap).
- Handle and AS150U plug face the door, so the combiner box sits on the side wall close to the doors (the battery
  cable is 500 mm).
- **cabinet_well** hangs in the centre with its roof just under the top of the frame (z 664) and grows downwards:
  2 batteries leave 458 mm ground clearance, 4 still 258. The doors face right: you reach in from the side between
  the right wheels (the tyres start at y 285, the cabinet is y +-143) and slide the battery out under the upper beams
  (the top battery is 12 mm under them). Low cg (566 -> 466 mm) and nothing on top.
- **cabinet_top** stands on the frame with the doors to the rear: easiest to reach, but the cg goes up with every
  level (818 -> 915 mm) and it takes the top deck.
- Heat: the losses in the batteries are small (at an average 20 A per pack and ~40 mOhm a few W per battery), the
  3 mm alu walls get rid of that. In full sun a white or reflective coat keeps the cabinet under the 45 C charging
  limit; for charging inside the cabinet leave a vent with a filter in the back wall.
- Rain: doors with a rubber seal and the latch on top, the hinges at the bottom with a drain gap.

## Or a wooden box on one side (2 batteries)

The simplest to build with hand tools: 18 mm multiplex, 2 compartments, on the two upper beams of the right side.

- **Upright, plugs up**: the battery comes out by its own handle and the plug stays reachable without taking anything
  apart; 110 mm above the batteries leaves room for the AS150U plug and the bend of its cable. The cables go out
  through a slot at the top of the rear wall, under the 10 mm lid overhang, so rain does not run in.
- **Battery width along y, thickness along x**: the two batteries side by side make the box 238 wide, so it stands on
  both beams of one side (x 305..445) with 54 mm overhang inside and 44 outside; it stays inside the wheel units
  (x 489). Across (width along x) it would stick out 44 mm past them.
- **Between the axles at y 0**: clear of the stepper motors above the front wheels (y 405..595) and of the GNSS; the
  other side of the top deck stays free for an implement or a second box.
- **Weight off-centre**: 34.9 kg at x +370 moves the cg of robot + box ~66 mm to the right (with the 160 kg robot)
  and puts ~35 kg more on the right wheels than the left. For two-sided balance: a second box on the left (4
  batteries) or something of similar weight there. The cg of the box itself is high (936 mm).
- **Wood**: cheap, easy to change and an insulator, but it must be sealed (paint / epoxy, edges too) against water;
  it is not fire resistant. The MBH3+ has its own BMS and housing; keep the compartment clean and dry.

## The same wooden box for the MU3+

- The MU3+ (MegaUMPF3+, 48 V 14S 50 Ah) has the same energy as the MBH3+ (2.56 kWh), the same AS150U and the same
  CAN hot-swap, but it is a short block (167 x 197 x 292.4, 301.9 with the handle) with an IP67 housing and rubber
  bumpers, instead of a thin slab. The runtimes and the hot-swap margin are the same as for the MBH3+.
- Side by side across the robot the box would be 408 wide (x 166..574), far past the wheel units (x 489). So the two
  batteries stand **one behind the other along the beams**: the box is 213 wide (x 264..477, over both right upper
  beams with 41 / 32 mm overhang) and 468 long (y +-234), still clear of the stepper motors above the front wheels.
- Plug at the rear for both: the cable of the front battery runs over the divider to the slot in the rear wall.
- Lower than the MBH3+ box (lid top 1142 instead of 1258 mm, cg 889 instead of 936 mm) and as heavy (34.5 kg); the
  load still sits 370 mm to the right (cg of robot + box ~66 mm to the right, see above).
- IP67 means the MU3+ itself does not mind rain; the wooden box is then mostly a holder and protection against
  knocks and sun. A slatted or open version would also do.

## Modular

- One tray segment per battery, 100 mm long, with a joint strip under each seam; the end frames bolt to the outer
  segments. 100 = 82 battery + 12 HDPE separator + 6 play.
- 100 mm is two steps of the 50 mm hole grid: with one battery more the rack grows 50 mm at each end, and each cross
  rail moves one hole out. The rails and bolts stay the same; the side guides and the hold-down bar are bars of the
  rack length (cheap to cut a longer one).
- Combiner box on the rear end frame: an AS150U-F socket per slot (the battery cable is 500 mm), main fuse, CAN to the
  robot. With normally-off BMS's the key pin turns each battery on.

## Three places

| | top | well | saddle |
| --- | --- | --- | --- |
| Mount | 2 tubes 40 x 40 over the inner upper beams, 4 x M10 | same tubes under the inner upper beams, rack hangs on 2 ears | per side 2 flat bars under both upper beams, cradle on star knobs |
| Swap | lift out from above, easiest | lift out from above through the frame opening (x +-305, y +-405) | open the retaining bars, slide out sideways (the outer one first) |
| cg (2 batteries) | 903 mm: high | 502 mm: low, centred | 486 mm: low, between the axles |
| Ground clearance | robot unchanged | 279 mm under the rack | ~310 mm under the cradles |
| Conflicts | top deck taken (solar canopy, hydraulic pack, crate carrier) | centre under the frame taken (aerator, sledge meter, UV hood, soil sampler) | same space as the simple battery pack and the aerator |
| 3 batteries | fine | fine | 1 + 2: 108 mm cg to one side |

- **well** is the recommended start: low cg, nothing above the frame or outside the robot's outline, the top deck
  stays free, and a battery comes straight up by its handle. Price: 279 mm ground clearance in the middle, and the
  mid-mounted implements cannot be used at the same time.
- **top** keeps everything under the robot free and is the easiest to reach, but puts 35..63 kg at ~0.9 m: on a side
  slope that matters (check with the robot's tipping angle before choosing it).
- **saddle** keeps top and centre free, but 4 batteries make 2 cradles of 2 that are fiddly to swap (sideways, inner
  one behind the outer one) and 3 batteries are not symmetric. The cradles stay inside the wheel units (974 mm over
  all, the robot is 978).

## Hot-swap margin

With one battery out, the others must carry the robot: (n - 1) x 60 A continuous against an estimated 90 A peak of
the 4 hub motors at full pull. 2 batteries: -30 A (one battery alone must not be asked for full pull: stop or drive
gently during the swap, the 100 A peak is only 3 s); 3: +30 A; 4: +90 A.

## Estimated, not measured

- MBH3+ mass 11.8 kg (sheet: 10.5 - 11.8 kg, the MBH3 33.8 Ah is 10.2 kg); 90 % usable
- Robot peak current 90 A and base load 60 W; implement loads from the simple battery pack (their own calcs)
- Combiner box 1.5 kg and size 140 x 70 x 90; the AS150U-F panel socket for it is to be confirmed with BatteryLabs
- Whether the normally-off BMS limits the inrush when a full battery is added to a lower bus (questions in
  `Battery Labs/README.md`)
- That the hold-down bar with rubber strip is enough on rough ground (no vibration test)
- Internal resistance of the MBH3+ (~40 mOhm) and the cabinet temperature in the sun (not calculated)
- That BatteryLabs allows the MBH3+ to be used lying flat (the sheet says mounting in any orientation)
- MU3+: mass 11.5 kg (flyer: 7.3 - 11.8 kg over the whole range), the bumper / top frame heights, the handle and
  socket position: estimated from the flyer pictures (no vendor STEP for the MU3+ yet)
- Multiplex density 0.68 kg/dm3; 110 mm above the batteries for the AS150U plug and cable bend (plug not measured)
- Robot mass 160 kg (for the cg effect)
