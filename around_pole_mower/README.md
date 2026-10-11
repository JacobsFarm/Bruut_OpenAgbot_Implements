# Around-pole fence mower for the Bruut

Mows the strip under a fence, in the first place an **electric fence**, and goes around the posts by itself. Grass
that grows into the bottom wire drains the fence; today this strip is done with a brushcutter or a tractor-mounted
fence mower. The robot drives along the fence on RTK; the mower reaches under the wire and swings around each post.

| | Variant | Contents |
| --- | --- | --- |
| [Simple](simple/README.md) | `simple/` | FreeCAD model: trailing swing arm with a spring, string-trimmer head under a PE guard ring, 48 V BLDC motor with a V-belt to a deck spindle; calculations, animation along an electric fence, parts list (≈ €575); why: [RATIONALE](simple/RATIONALE.md) |

![the simple mower on the robot](simple/previews/1_iso_on_robot.png)

![animation: mowing under the fence, around two posts](simple/previews/animation_around_posts.gif)

## Designs found online

| Design | Principle | Notes |
| --- | --- | --- |
| [Fence mower, US 7,287,364](https://patents.google.com/patent/US7287364) | 3-point frame, swing arm on a pivot pin with rollers on a curved track, spring pulls the arm back, **wedge nose** under the bottom rail; PTO → right-angle gearbox → belt → blade | the classic swing-arm principle |
| [Kneilmann "Zaunkönig" (topagrar)](https://www.topagrar.com/technik/aus-dem-heft/unterm-zaun-maehen-wie-ein-koenig-11556852.html) | **star with 3 heads** on a short boom turns around the post by driving on; blades inside a plate plus 4.4 mm nylon strings past the plate; 2900–3000 rpm, hydraulic; bottom wire ≥ 40 cm, head ≈ 15 cm | ≈ €6,390; step-in posts are not stable enough |
| [Tractor-mounted fenceline mowers and trimmers (AgrAbility)](https://www.agrability.org/new-toolbox/2269/) | mower type (blades) and trimmer type (thick cords), both on a spring swing arm | trimmer type ≈ half the price |
| [Fence-row mower (Farm Show)](https://farmshow.com/view_articles.php?a_id=238), [DIY loader-mounted mower](https://farmshow.com/a_article.php?aid=34948) | home-built from a walk-behind mower deck, belt drive | DIY is common |
| [Riding-mower fence trimmers (TractorByNet)](https://www.tractorbynet.com/forums/threads/fence-line-trimmer.356544/post-4434247) | string trimmer on a spring-loaded pivot clipped to the deck | the simplest version that works |
| [Robot weed eater (ArduPilot forum)](https://discuss.ardupilot.org/t/robot-weedeater/122124) | cordless 40 V trimmer head on a rover, pivoting to the side | idea stage |

## Concept

1. **Trailing swing arm** about a vertical axis on the robot, a spring holds it against a rest stop.
2. **Low head with nylon strings** under a round, insulating guard that slides along the post; the strings reach
   past the guard to the post.
3. **Motor away from the head** (inside the fence line), belt in the arm: the part under the wire stays low.
4. **Floating head** on a skid; the robot does not have to follow the ground for it.

## Requirements

| | |
| --- | --- |
| Reach | grass right under the wire and ≥ 150 mm on both sides, up to the post |
| Height | under the bottom wire (cattle 300–400 mm; sheep, goats and wolf fences 150–250 mm: mow offset) |
| Electric | nothing conductive against the wire; the fence must not be damaged |
| Posts | wood, concrete, steel, plastic; Ø 50–150; spacing 3–10 m |
| Robot | 48 V battery, ≤ 1 kW, mounted on the 50 mm hole grid, no changes to the robot |
| Cost / making | laser-cut plates, standard tubes, bought drive parts; < €1,000 |

## Variants (ideas)

| Variant | Difference | Why |
| --- | --- | --- |
| Simple (modelled) | 1 string head on a passive spring arm | cheapest, no software |
| Active arm | small actuator swings the arm out of the way at known post positions (RTK + post map or a camera) | no impact, also for step-in posts |
| Star head | 3 small heads on a free-turning star (Zaunkönig principle), one motor with a belt to all three | gets behind the post, no uncut spot |
| Left / right | mirrored parts | fences on both sides of a path |
| Blade disc | free-swinging blades instead of strings | longer service life in rough grass; only with the energizer off |

## Design decisions

- **String instead of blade:** insulates, does not cut the wire, does not damage posts, cheap.
- **Passive instead of active:** no sensor, no actuator, no code; the price is ≈ 150 cm² uncut per post and a peak
  post force of ≈ 200 N.
- **48 V BLDC from the robot battery** instead of a petrol engine or hydraulics.
