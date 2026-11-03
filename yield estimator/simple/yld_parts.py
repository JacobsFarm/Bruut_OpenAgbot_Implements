"""Parts of the yield estimator, in robot coordinates. The camera bridge (brackets, posts, bar, stays) is the mole
mapper's (mmp_parts); this file adds the RGB cameras, the depth cameras and the LED flash bars, and the crop rows for
the renders.
"""
import Part
from FreeCAD import Vector as V

import yld_params as P
import pbl_parts as PP
import mmp_parts as MP

box_span = PP.box_span
cyl = PP.cyl

brackets = MP.brackets
bracket_bolts = MP.bracket_bolts
posts = MP.posts
cross_bar = MP.cross_bar
stays = MP.stays


def cameras():
    return Part.makeCompound([MP._cam(x, P.cam_box) for x in P.cam_x])


def tof():
    return Part.makeCompound([MP._cam(x, P.tof_box) for x in P.tof_x])


def leds():
    """LED flash bars 30 x 45 on the front face of the bar, tilted with the cameras."""
    y0 = P.post_y[1]
    top = P.bar_z[1]
    out = []
    for x0, x1 in P.led_x:
        b = box_span((x0, x1), (y0, y0 + 30.0), (top - 45.0, top))
        b.rotate(V(0, y0, top), V(1, 0, 0), P.cam_tilt)
        out.append(b)
    return Part.makeCompound(out)


def crop(y=(-1200.0, 3000.0)):
    """Cauliflower heads in 4 rows (render only): a stem and a half-sphere curd with leaves as a flat disc."""
    leaves, heads = [], []
    for x in P.cam_x:
        yy = y[0]
        i = 0
        while yy < y[1]:
            d = P.head_d[0] + (P.head_d[1] - P.head_d[0]) * ((i * 37) % 10) / 9.0
            leaves.append(cyl(d * 2.4, (x, yy, P.crop_height - 120.0), (x, yy, P.crop_height - 100.0)))
            s = Part.makeSphere(d / 2.0, V(x, yy, P.crop_height - d / 2.0))
            heads.append(s.common(box_span((x - d, x + d), (yy - d, yy + d), (P.crop_height - d / 2.0 - 1.0, P.crop_height))))
            yy += P.plant_spacing
            i += 1
    return Part.makeCompound(leaves), Part.makeCompound(heads)
