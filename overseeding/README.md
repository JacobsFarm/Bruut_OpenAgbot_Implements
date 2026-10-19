# Cambridge roll and overseeder

Simple, cheap trailed implements for lawn repair, all on one simple tow hitch (50 mm ball) under the rear of the
Bruut:

| | [Cambridge roll](cambridge%20roll/) | [Overseeder (drop seeder)](overrseeder/) | [Overseeder with Cambridge roll](overseeder%20with%20cambridge%20roll/) |
| --- | --- | --- | --- |
| What | 1 m ring roller, 20 cast-iron rings Ø280 | 1 m drop seeder, fluted roller on a 24 V motor, camera switches it per bare patch | the seeder unit between the arms of the roll: seed, then roll in |
| Rests on | ball + roll | ball + 2 small wheels | ball + roll |
| Mass | 178 kg | 61 kg | 216 kg (234 kg full) |
| Draft | 100 … 250 N | ≈ 60 N | 185 … 310 N |
| Parts | ≈ € 850 incl. hitch | ≈ € 500 | ≈ € 1,200 |
| Prefix | `cbr` | `ovd` | `osr` |

The hitch, the coupling head, the drawbar and the general helpers are in `cambridge roll/` (`cbr_*`); the overseeder
and the combination import them from there (`ovd_params.py` and `osr_params.py` put that folder on `sys.path`).

Not to be confused with the slit seeders in [../overseeder/](../overseeder/), which cut the seed into a closed sward.

![animation](overseeder%20with%20cambridge%20roll/previews/animation_spot_seeding.gif)

![roll](cambridge%20roll/previews/1_iso_on_robot.png)

![overseeder](overrseeder/previews/1_iso_on_robot.png)

![combination](overseeder%20with%20cambridge%20roll/previews/1_iso_on_robot.png)
