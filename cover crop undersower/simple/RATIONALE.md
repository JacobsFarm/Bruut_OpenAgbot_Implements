# Cover crop undersower (simple) - rationale

## Where the seed goes

The robot straddles a bed of 2 rows, 375 apart, with its wheels in the inter-rows at x +-375. The only inter-row that is
free under the robot is the middle one (x 0). The wheel inter-rows are driven every pass, but a cover crop there still
holds the soil and carries the wheels later; so the side bands are sown behind the rear tyres, where the tines loosen
the track a little. The crop rows themselves (x +-187.5) are never touched: the hoses cross them above 544 mm and the
tine bar at 430 mm, and `check_rows()` tests the whole row space up to 400 mm.

## Bands, not broadcast

Broadcasting over the crop would put seed on the leaves and in the row, where it competes. Bands put the seed on bare
soil between the rows, where 3 light tines can cover it. The seed rate per field area stays as it would be broadcast;
in the bands it is 2.1 x denser, which suits undersown species that must close the inter-row quickly.

## Metering

One shaft with 3 fluted rollers keeps the cells in step. The middle cell feeds a 150 mm band, the side cells 100 mm, so
their outlets get a different share by the slot width per cell (or a narrower roller); the model shows equal rollers,
the calculation the speeds per band share. ~7.5 ml per turn covers clover (2 rpm) up to rye (36 rpm) on one 60 rpm
gearmotor; for clover alone a fine-seed roller gives more even metering.

## Tines

Spring tines O8 on a coil scratch 10-20 mm, ~15 N each: 105 N for 7. They follow the soil without a depth wheel and
spring back over stones. Tines in the wheel bands run behind the tyres, where the soil is firm: if they pull too
little seed in, a small press roller is the next step (advanced).

## Estimated, not measured

- Seed rates and bulk densities of the species, the volume per turn of the fluted roller (~7.5 ml)
- Draft per spring tine (15 N), rolling resistance (0.08), robot mass (160 kg), battery energy (1.9 kWh)
- Highest crop under the bar (400 mm) and the row width kept free (+-80 mm)
- Mass of the gearmotor (0.4 kg) and the hoses (PVC spiral hose 1.2 g/cm3)
- Not modelled: the shutter per cell, a level sensor, the hose clamps
