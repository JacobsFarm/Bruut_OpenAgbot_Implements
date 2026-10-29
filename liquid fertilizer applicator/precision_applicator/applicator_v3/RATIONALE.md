# Why V3 is built this way

## Trailing instead of raked forward

In V1 and V2 the knife leans 15° forward (tip forward), which made it clear the rear cross tube and pulls it into
the soil. In practice a forward-raked knife lifts the soil, catches stones and roots and tears the sward. A trailing
knife (tip back, top forward) slides over obstacles, presses the soil down beside the slot and leaves a clean slot
for the liquid. Depth control does not need the pull-in: the discs and the actuator set the depth.

## 20 degrees

Turning the knife over moves its top forward and its tip back, both limited by other parts:

| Trail | Tip behind the shaft | Top of the knife | Note |
| --- | --- | --- | --- |
| 15° | 283 | z 292 | close under the rear tube (z 306) |
| **20°** | **307** | **z 282** | 24 under the rear tube, press wheel 93 from the tubes |
| 30° | 365 | z 255 | tip close to the press wheel; bottom edge nearly flat |

20° keeps the knife top clear of the rear tube, leaves the press wheel where V2 has it, and still gives a clear
trailing angle. It is one parameter (`knife_trail`).

## Placement from the outlet, not from the tip

The liquid has to be put 50 mm deep, so the knife is placed by its outlet (centre of the tube end at z −50) and not
by the tip as in V1. Then the knife is moved back along y until its whole outline is 15 mm from the disc rim
(bisection, `knife_origin`). The disc stays at 50 mm, so the slot is open down to where the liquid comes out; the
knife tip cuts the last 16 mm itself, which also makes a small pocket under the outlet.

## Holder under the sleeve

In V1 the holder plate is welded to the rear face of the sleeve and runs back and down to the knife. With the knife
trailing, its top lies under and in front of the rear tube, so that plate ran through the sleeve and the tube
(`check_interference`: 2116 and 613 mm³). Welded under the sleeve it covers the same two knife slots, keeps the
knife in the disc plane and stays 19 mm from the disc.

## Double knife

Two liquids (for example a fertiliser and a biostimulant or nitrification inhibitor) can not always be mixed in one
tank. Two tubes on one knife, each from its own pump section, keep them apart until they are in the slot. The tubes
lie in line behind the blade, not side by side, so the slot stays 10 wide. Tube A stays where it is on the single
knife, so V3 places both knives the same; tube B is 4 mm longer to bring its outlet to the same depth. At the
top the first version bent B parallel to A, so the hose ends touched and there was no room for two hoses; B now
bends 40 mm earlier and at 45° (A 22.6°), which puts the hose ends 61 mm apart. With 2 rows
and a double knife the pump needs 4 sections.

## Reusing V1 and V2

V3 only replaces the knife placement and the holder. Frame, rotor, mast, suspension and the press wheels are
built by the V1 and V2 functions, so changes there show up in V3 after a rebuild. To avoid copying the bolt code,
`pa_parts.knife_point`, `holder` and `knife_bolts` got an optional `place=` argument; without it they work as
before.
