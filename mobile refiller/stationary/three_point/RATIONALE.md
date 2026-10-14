# Three-point frame station: why it is built like this

Numbers from `s3p_calc.py` and the model (`build_s3p.py`). Estimated values are listed in the [README](README.md).

## 1. Why a three-point frame

Most farms have a tractor with a three-point linkage that drives to the field anyway. A frame needs no axle, tyres,
brakes or lights, is the cheapest carrier (232 kg dry), and stands on its own legs as soon as the tractor lowers it.
One IBC per frame keeps it within the lift capacity and the front-axle load of a mid-size tractor; for more liquid,
take two frames or the [flat wagon](../flat_wagon/).

## 2. The mast is the hitch tower

A three-point frame needs a tower for the top link anyway, and the refill head needs a mast. Here they are one part:
a 100 × 100 × 5 tube on the centre line in front of the IBC, on a foot beam between the two hitch plates. The top
link plates sit at 610 mm above the lower pins (ISO 730 cat. 2 mast height); two round braces from the hitch plates
to the mast make it an A in the front plane. Above the top link the same tube carries the arm at 2 m.

The full frame hangs 645 mm behind the lower pins: top link 15.4 kN. Taken by the mast alone above the platform this
would be 167 MPa (× 2 dynamic, S355 needed); the braces take most of it.

## 3. Front ballast

1,490 kg full, 645 mm behind the lower pins, takes the front axle of a 4.3 t tractor down to 12 % of the total. For
the usual 20 % (steering and braking) the tractor needs about **360 kg front ballast**, or transport the IBC half
full (no front ballast needed up to about 600 l). `s3p_calc.tractor()` takes any tractor.

## 4. IBC on a platform at 650 mm, box underneath

- The platform is high enough for the control box to fit underneath (box 150–603 mm, platform tubes from 610 mm), so
  the box is protected from the tractor, from animals and from rain, and needs no extra footprint.
- The pump then lies 535 mm below the bottom of the IBC: always flooded.
- The IBC is turned with its valve to the right; the suction hose goes down beside the side rail and in under the
  platform to the box. The box is turned with its door to the rear, where it can be opened when the frame stands.
- Legs with 160 mm foot plates at 1.38 × 1.22 m: 30.9° sideways full. On soft ground put boards under the feet.
- The pallet stands on the two side rails (under its edges) and the middle rail; corner guides and two straps hold it.

## 5. Arm and docking

The arm pivots on the mast top: 0° left, 180° right, 90° folded back over the IBC (IBC top 1,830, arm at 1,965). The
drop pipe never passes over the IBC footprint when swinging (the mast stands 670 mm in front of the IBC centre), so
the arm can swing from left to right through the back. On the tractor the arm is folded back: 295 mm behind the
frame, inside the width.

Reach 1,500 mm: the widest part below the arm is the IBC valve elbow on the right (746 mm with the hose) and the feet
on the left (690 mm), + 250 mm gap + half the working robot.
