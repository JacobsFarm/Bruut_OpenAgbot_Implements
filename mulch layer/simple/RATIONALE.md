# Mulch layer (simple): why it is built this way

## On the three-point hitch

- A foil layer needs downforce on the press wheels and the discs and has to be lifted at every bed end. The
  [three-point hitch](../../three%20point%20hitch/simple/) already gives both: two lower links with electric lift rods
  and a top link, with a float slot so the implement rides on its own wheels in work. The mulch layer is a category 0
  implement for it; `build_mly` imports `build_tph` from that folder, so the hitch is the same model, not a copy.
- The implement frame is the cultivator's: a 60 x 60 toolbar with the hitch lugs and an A-frame mast, here with two
  50 x 50 side beams to the rear that carry the roll, the press wheels and the discs.

## Foil, press wheels, discs

- Foil 1.2 m wide over a bed between the wheel tracks (the robot straddles the bed; the foil edges at x +-600 lie
  just outside the tracks, behind the robot, so the tyres never run on the foil).
- Roll O200 on a core O76 (PE 25 um: 1075 m, 30 kg; biodegradable 15..20 um rolls are longer and lighter) in open
  V-holders: lift the shaft out to change the roll. A band brake on a drum keeps ~25 N/m web tension.
- The foil runs under a guide bar 110 mm above the bed and lies down 60 mm behind it, ahead of the press wheels.
- Press wheels O250 x 80 (semi-pneumatic tyre on a steel rim) run on the edges, 55 mm inside, and push them into the
  soil; concave discs O350 at 22 degrees to the travel, tilted 15 degrees, 50 mm deep just outside the edge throw a
  ridge of soil onto it. This is the usual light plastic mulch layer, without a bed shaper.

## Ballast: the weak point

- The implement weighs 94 kg with a full roll and its cg is 1.6 m behind the robot centre. Lifted, the robot alone
  would tip backwards (front axle share -13 %). With **3 plates per front stack of the
  [counterweights](../../counterweights/simple/) (154 kg)** the front axle keeps 26 %; with an empty roll 2 plates
  are enough. In work the press wheels carry part of the implement, so the lifted case is the one that counts.
- The hitch lift rods (2 x 3000 N) need 1071 N each with a full roll: fine.
- An advanced version should move the roll forward (onto the robot) or shorten the frame; the foil web then has to
  pass the lift rods of the hitch, which is why the roll stays on the implement here.

## Capacity

At 0.5 m/s with 90 s per bed end (stop, lift, cut the foil, turn, start a new end by hand) a 100 m bed takes 290 s:
12 beds (1.2 km, 1490 m2 of foil) per hour, a roll lasts ~10 beds (50 min). Pull 730 N (discs 360, rolling 312),
grip margin 1.51 with the ballast, ~27 Wh per bed. Foil cost ~10 EUR per 100 m (PE 25 um, estimated).

## Estimated, not measured

- Robot mass 160 kg, cg (0, 0, 380); hitch masses from three point hitch/simple
- Draft of a covering disc 180 N at 50 mm in light soil, press wheel load 120 N and rolling resistance 0.12
- Web tension 25 N/m, foil density 920 kg/m3, foil price 0.08 EUR/m2
- Half the implement weight on its press wheels in work; 90 s per bed end
- Ballast position (y 500) and plate masses from counterweights/simple
