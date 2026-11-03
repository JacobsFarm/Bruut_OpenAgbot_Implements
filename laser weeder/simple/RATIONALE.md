# Laser weeder (simple) - rationale

- **Hood of the drop-on-demand boom**: closed, dark and with constant light, which a class 4 laser needs for safety
  and the camera needs for aiming at the growing point (0.29 mm/px).
- **2 heads of 300 mm**: one head would need +-45 degrees, beyond a normal f-theta lens.
- **Diode lasers, fibre-coupled**: compact and efficient (~35 %); the hot sources stay on top of the robot, only the
  light goes down.
- **Slow and small area**: ~19 J per weed limits the speed to ~0.5 m/s at 20 weeds/m2, and the battery gives ~1000 m2
  per charge. A tool for high-value vegetable beds.

## Estimated, not measured

Energy per weed (8 / 20 / 40 J), laser efficiency (35 %), cooling (60 W), spot size, galvo jump time (5 ms), weed
density and sizes, drive power, robot mass and battery. Not modelled: the interlocks, fume extraction, the optics
inside the heads.
