# Dock weed mill V2: X axis on PTO-shaft tubes

V2 keeps everything from `../V1/dockweed_requirements.md` (process, requirements, Z axis, spindle, pot, control) and changes the **X axis**: instead of 2 aluminium profiles with HGR15 rails and 4 carriages, the slide runs on **2 PTO-shaft profile tubes** (lemon profile). Cheap, available at any agricultural dealer, and made for high load and dirt.

| File | Contents |
|---|---|
| `dockweed_design_v2.py` | Parametric FreeCAD script (all dimensions in `P` at the top), calculations, export |
| `dockweed_drill_v2.FCStd` / `.step` | Model (cutter 150 mm deep) / STEP export |
| `dxf/*.dxf` | 17 laser/plasma contours (new: end plate, support flange, sleeve pad) |

```python
exec(open(r"F:/veldrobot/aanbouwdelen/dockweed drill/V2/dockweed_design_v2.py", encoding="utf-8").read())
```

---

## 1. The X guide, how it works

- **Fixed:** 2 inner tubes (lemon profile 49 × 39.5 × 4.5, L = 1400) at Z = 760 and 1060, 300 apart. Each rests on 2 **support ribs** (10 mm, welded on the back of the tube) with a flange plate on the uprights at X = ±340. The tubes overhang 360 mm each side. At both ends an end plate (steel 12 mm) ties the two tubes together.
- **Moving:** **3 sleeves**, pieces of the matching outer tube (57.5 × 48 × 4): 2 × 100 mm on the upper tube (220 apart), 1 × 140 mm on the lower tube. A flat bar (8 mm) is welded on the front of each sleeve and bolted to the X slide plate (4 × M8 each).
- **Slot in the sleeve:** the back of every sleeve is sawn open (14 mm wide) so the sleeve can pass the support ribs. The lemon shape stays closed around the tube at the top, bottom and front.
- **No over-constraint:** the lower sleeve has slotted bolt holes in the slide plate (±8 mm in Z). The lemon profile locks rotation, so one tube already guides the slide; the second tube only adds stiffness.
- **Dirt:** rubber scrapers (8 mm) on both ends of every sleeve, one grease nipple per sleeve. Use the plastic bushes/strips that come with the PTO tubes inside the sleeve; grease them like a PTO shaft.
- **Drive:** unchanged (HTD-5M belt, NEMA 23 + 5:1). The belt now runs between the two tubes, clamps on brackets on the end plates. Mechanical stops (rubber) on the end plates, inductive limit switch on the left.

## 2. Other changes in V2

| Change | Why |
|---|---|
| Uprights from X = ±250 to **±340** | Shorter overhang of the tubes (270 mm to the outermost sleeve) |
| Spiral cable from X slide to Z slide (bracket on both) | Open point 7 in V1: cables to the moving Z slide |
| Cable chain moved above the sleeves | Space for the sleeves and grease nipples |
| Rubber splash flap (cone) around the top of the pot | Open point 9 in V1: flying pebbles when mowing with the pot raised |
| E-box moved between the uprights (X −300..0) | The uprights moved outward |

## 3. Key figures (from the script)

| Quantity | V2 |
|---|---|
| Tube section | 544 mm², I = 118,700 mm⁴ (bending in Z) / 86,700 mm⁴ (bending in Y). 2 tubes: 12.0 kg |
| Deflection in Z at the outermost position (X slide 62 kg, 31 kg per tube) | 0.28 mm |
| Z force 600 N at 234 mm lever → 468 N in Y per tube (opposite direction) | 0.59 mm per tube, slide twist ≈ 0.23° |
| Friction (μ 0.15, greased) | ≈ 190 N against 895 N holding force of the belt drive |
| Mass of implement | **≈ 100 kg** (V1: 91 kg), X moving mass ≈ 62 kg (V1: 59 kg) |
| Axle load, battery on the far side | 194 kg (driven) / 56 kg (steered). Without moving the battery: 226 / 24 kg ✗ |
| Max. downward force before the axle lifts | 1251 N (limit Z force to 600 N) |

Collision check in FreeCAD at X = −500, 0 and +500 (driving position): no collisions except the intended weld/interference joints.

## 4. Honest remarks

1. **Heavier, not cheaper by much.** +9 kg (steel tubes 12 kg against aluminium + rails 11 kg, plus end plates, ribs, pads, spiral cable). Cost is about the same as V1 for the X axis (the saving on rails and profile is spent on tubes and plates). The gain is robustness and availability, not price. Aluminium end plates and 8 → 6 mm ribs can win back ~2 kg; shortening the stroke to 800 mm ~3 kg.
2. **The tube dimensions are from dealer listings (Sparex 1B inner 49 × 39.5 × 4.5 and 2A outer 57.5 × 48 × 4), not from a drawing.** Buy the inner and outer tube of the **same shaft** (they come as a matching pair with plastic bushes), measure them, then adjust `pto_*` and `huls_*` in `P`. Inner tubes are sold at 1 m; 1.4 m needs a long shaft (harvester class) or a custom piece. Otherwise limit the stroke (`xbalk_L` 1200 → stroke ~800).
3. **Play and wear:** PTO tubes slide with some clearance (0.5–1 mm is normal). For ±2 mm positioning accuracy that is fine, but expect a bit of play at the spindle. Replace the plastic bushes when they wear.
4. **Welding is needed** (ribs on the tubes, pads on the sleeves). V1 needed none on the X axis. Weld with low heat input (short stitches) so the lemon profile does not distort, and check the sleeve still slides afterwards.
5. **Y deflection is the weak point:** 0.6 mm per tube at 600 N Z force. Acceptable, but keep the Z force limit and the spindle close to the tubes (hence the shorter Y build-up in V2).
6. The Z axis still uses HGR15 rails (as in V1).

## 5. X axis parts (indicative, check prices: not verified)

| Part | Quantity |
|---|---|
| PTO inner tube, lemon, ≥ 1.5 m (cut to 1400) | 2 |
| PTO outer tube, ≥ 0.4 m (cut into 2 × 100 and 1 × 140 mm) | 1 |
| Sleeve bushes/strips, scraper rubber, grease nipples M6, grease | 1 set |
| Steel plate for end plates (2), support flanges (4), ribs (4), pads (3) → DXF | 1 set |
| Bolts M8 (12 + 8 for ribs), M10 × 70 (16) | — |
| Dropped from V1: 2 aluminium profiles 40×80, 4 HGR15 rails/8 carriages for X | — |

## 6. Open points

1. Measure the real tubes first (section, wall, clearance) and adjust `P`.
2. Check the weld distortion with a test piece.
3. Hole pattern of motor and Z carriages on the slide plate: from the real parts.
4. All other open points from V1 (measure and weigh the robot, process trial first, cutter shape, stones, software).
