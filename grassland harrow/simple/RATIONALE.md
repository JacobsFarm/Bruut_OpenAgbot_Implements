# Grassland harrow (simple): why it is built this way

## One harrow for three spring jobs

Spreading molehills and dung pats, raking out moss and dead grass, and covering broadcast seed are all done with a
pasture harrow on grassland. A board in front does the levelling, spring tines behind it do the raking. That covers the
*molehill spreader* idea without a separate machine; the *mole mapper* can switch the actuator so the board only works
where there are hills.

## Rear toolbar and lift: the push blade geometry, mirrored

The rear toolbar, the hangers, the pivot forks, the actuator mast and the actuator are the push blade parts mirrored in y
(same lever arm 164..184 mm about the pivot). Front blade and rear harrow can be on the robot at the same time.
The tyre at the rear does not steer, so the clearance is simply 148 mm (work) to 155 mm (transport) to the rear tyres.

## Levelling board

- Angle 100 x 100 x 8, the upright leg in front pushes the soil of a hill forward and sideways, the trailing flat leg
  smooths it. A hill of ~8 kg covers 0.57 m2 at 10 mm, i.e. 0.44 m of the 1.3 m wide board.
- The first concept had the toe forward; in transport it tipped down and left only 48 mm under the board. With the
  flat leg trailing and the board 55 mm further back it clears 114 mm.

## Spring tines

- O8 double tines, 2 rows of 16 (75 mm pitch, offset half a pitch): a track every 37.5 mm, like commercial grass
  harrows. The tips trail 170 mm behind the bar; 15 mm working depth into the thatch.
- The harrow floats: its own weight (60 kg) is shared by the board (11 kg), the tines (27 kg) and the pivot (22 kg).
  That is light (8 N per tine); a pasture harrow works by its weight, so the aggression comes from the tine angle and
  from ballast on the tine bars if needed, not from the actuator (it only lifts, the rod pin floats in the slot).

## Pull force

- A floating harrow can only pull as hard as its weight lets it dig in: tines 1.5 x their load (397 N), board 0.6 x
  its load plus pushing one hill (111 N), rolling resistance of the robot 121 N: 629 N.
- Grip of 4 tyres on grass (0.45 x 205 kg) = 905 N, motors 1100 N continuous: margin 1.44. On wet grass (0.35) the
  margin drops to ~1.1: drive slower or lift the board where there are no hills.
- Power 1.26 kW at 1.5 m/s: within the 4 x 550 W hub motors but not much spare; 1 m/s halves the extra load.

## Axle load

The lifted harrow hangs 1.1 m behind the robot centre: the front keeps 15 % (36 kg). Same remedy as the spreader:
the front counterweight (2 x 20 kg) or the push blade on the front.

## Estimated, not measured

- Robot mass 160 kg and its centre of gravity midway between the axles
- Tyre grip 0.45 on grass, rolling resistance 0.06
- Tine force factor 1.5, board friction 0.6, tine spring rate 1.2 N/mm
- Soil per molehill 8 kg, 300 hills per hectare
- Share of the harrow weight on the board 0.4 of that on the tines
- Actuator 2.6 kg, 10 mm/s at 1000 N
