"""Parts of the security patrol. Fixed parts are in robot coordinates. The pan/tilt head moves: pan_*() parts are
drawn in the pan frame (origin on the mast axis at z 0, so the Pan sub-Part is placed at (mast_x, mast_y, 0) and turns
about z), tilt_*() parts in the tilt frame (origin on the tilt axis, the Tilt sub-Part turns about x).
"""
import Part
from FreeCAD import Vector as V

import scp_params as P
import pbl_parts as PP
import spk_parts as SP
S = P.S

box_span = PP.box_span
cyl = PP.cyl
fuse_all = PP.fuse_all

MX, MY = P.mast_xy
H = P.mast_w / 2.0
Z0 = P.upper_beam_top


# ---------------------------------------------------------------------
# Base plate, mast, gussets
# ---------------------------------------------------------------------
def base_plate():
    p = box_span(P.plate_x, P.plate_y, (Z0, Z0 + P.plate_t))
    for x in P.bolt_x:
        for y in P.hole_y:
            p = p.cut(cyl(10.5, (x, y, Z0 - 1), (x, y, Z0 + P.plate_t + 1)))
    return p


def base_bolts():
    return Part.makeCompound([PP.bolt_z(10.0, x, y, Z0 - 40.0, Z0 + P.plate_t)
                              for x in P.bolt_x for y in P.hole_y])


def mast():
    z = (Z0 + P.plate_t, P.mast_top)
    t = PP.tube_span((MX - H, MX + H), (MY - H, MY + H), z, P.mast_wall, "z")
    a, t2 = P.top_flange
    fl = box_span((MX - a / 2, MX + a / 2), (MY - a / 2, MY + a / 2), (P.mast_top, P.mast_top + t2))
    return fuse_all([t, fl])


def _tri_xz(x0, x1, y, z0, h, t):
    """Triangular gusset in the x-z plane: along the plate from x0 (mast face) to x1, up the mast face to z0 + h."""
    w = Part.makePolygon([V(x0, y - t / 2, z0), V(x1, y - t / 2, z0), V(x0, y - t / 2, z0 + h), V(x0, y - t / 2, z0)])
    return Part.Face(w).extrude(V(0, t, 0))


def _tri_yz(y0, y1, x, z0, h, t):
    w = Part.makePolygon([V(x - t / 2, y0, z0), V(x - t / 2, y1, z0), V(x - t / 2, y0, z0 + h), V(x - t / 2, y0, z0)])
    return Part.Face(w).extrude(V(t, 0, 0))


def gussets():
    z0 = Z0 + P.plate_t
    out = []
    for s in (-1, 1):
        out.append(_tri_xz(MX + s * H, MX + s * P.gusset_reach_x, MY, z0, P.gusset_h, P.gusset_t))
        out.append(_tri_yz(MY + s * H, MY + s * P.gusset_reach_y, MX, z0, P.gusset_h * 0.6, P.gusset_t))
    return Part.makeCompound(out)


# ---------------------------------------------------------------------
# Pan base (fixed) and the pan / tilt head
# ---------------------------------------------------------------------
def pan_base():
    z = P.mast_top + P.top_flange[1]
    return cyl(P.pan_base_d, (MX, MY, z), (MX, MY, z + P.pan_base_h))


def pan_z0():
    return P.mast_top + P.top_flange[1] + P.pan_base_h


def pan_yoke():
    """U-yoke in the pan frame: bottom plate on the pan base, 2 arms up past the tilt axis."""
    z0 = pan_z0()
    w, d, t = P.yoke_w, P.yoke_d, P.yoke_t
    bottom = box_span((-w / 2, w / 2), (-d / 2, d / 2), (z0, z0 + t))
    top = P.tilt_z + 45.0
    arms = [box_span((s * w / 2 - (t if s > 0 else 0), s * w / 2 + (0 if s > 0 else t)), (-d / 2, d / 2), (z0, top))
            for s in (-1, 1)]
    out = bottom.fuse(arms[0]).fuse(arms[1])
    return out.cut(cyl(P.tilt_axle_d + 1.0, (-w, 0, P.tilt_z), (w, 0, P.tilt_z))).removeSplitter()


def pan_motor():
    """Tilt motor box on the outside of the right arm."""
    x0 = P.yoke_w / 2
    return box_span((x0, x0 + 45.0), (-35.0, 35.0), (P.tilt_z - 35.0, P.tilt_z + 35.0))


def _cam(body, lens, x_side):
    bx, by, bz = body
    xs = (P.cam_gap, P.cam_gap + bx) if x_side > 0 else (-P.cam_gap - bx, -P.cam_gap)
    b = box_span(xs, (-by / 2, by / 2), (-bz / 2, bz / 2))
    xc = (xs[0] + xs[1]) / 2
    l = cyl(lens[0], (xc, by / 2, 0), (xc, by / 2 + lens[1], 0))
    return b.fuse(l)


def tilt_vis():
    return _cam(P.cam_vis, P.cam_vis_lens, -1)


def tilt_ir():
    return _cam(P.cam_ir, P.cam_ir_lens, 1)


def tilt_axle():
    """2 stub axles from the hubs of the camera bracket through the yoke arms."""
    w = P.yoke_w / 2
    x0 = P.cam_gap + max(P.cam_vis[0], P.cam_ir[0]) + 1.0
    return Part.makeCompound([cyl(P.tilt_axle_d, (s * x0, 0, 0), (s * w, 0, 0)) for s in (-1, 1)])


def tilt_frame():
    """Bracket plate under the 2 cameras, hubs on the axle."""
    w = P.yoke_w / 2 - P.yoke_t - 4.0
    bz = max(P.cam_vis[2], P.cam_ir[2]) / 2
    plate = box_span((-w, w), (-60.0, 60.0), (-bz - 6.0, -bz))
    hubs = [cyl(40.0, (s * w, 0, 0), (s * (P.cam_gap + max(P.cam_vis[0], P.cam_ir[0]) + 1.0), 0, 0))
            for s in (-1, 1)]
    webs = [box_span(sorted((s * w, s * (w - 6.0))), (-25.0, 25.0), (-bz - 6.0, 0.0)) for s in (-1, 1)]
    out = fuse_all([plate] + hubs + webs)
    return out.cut(cyl(P.tilt_axle_d, (-P.yoke_w, 0, 0), (P.yoke_w, 0, 0)))


def tilt_illum():
    x, y, z = P.illum
    bz = max(P.cam_vis[2], P.cam_ir[2]) / 2
    return box_span((-x / 2, x / 2), (0.0, y), (bz, bz + z))


# ---------------------------------------------------------------------
# Fixed cameras, horns, beacon, microphone, electronics box
# ---------------------------------------------------------------------
def fixed_cams():
    out = []
    n, a, h = P.fixed_cam
    z = P.ring_z
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if dx:
            x0 = MX + dx * H
            b = box_span(sorted((x0, x0 + dx * n)), (MY - a / 2, MY + a / 2), (z, z + h))
            l = cyl(P.fixed_lens[0], (x0 + dx * n, MY, z + h / 2), (x0 + dx * (n + P.fixed_lens[1]), MY, z + h / 2))
        else:
            y0 = MY + dy * H
            b = box_span((MX - a / 2, MX + a / 2), sorted((y0, y0 + dy * n)), (z, z + h))
            l = cyl(P.fixed_lens[0], (MX, y0 + dy * n, z + h / 2), (MX, y0 + dy * (n + P.fixed_lens[1]), z + h / 2))
        out.append(b.fuse(l))
    return Part.makeCompound(out)


def horns():
    out = []
    for sy in (-1, 1):
        throat_y = MY + sy * (H + 5.0 + S.driver[1])       # driver back on the 5 mm clamp band
        out.append(SP.horn((MX, throat_y, P.horn_z), sy))
    return Part.makeCompound(out)


def horn_clamps():
    """Flat band clamp around the mast with a round pad for each driver back."""
    z = P.horn_z
    band = PP.tube_span((MX - H - 5, MX + H + 5), (MY - H - 5, MY + H + 5), (z - 30, z + 30), 5.0, "z")
    return band


def beacon_bracket():
    bx, by, t = P.beacon_bracket
    y0 = MY - H
    return box_span((MX - bx / 2, MX + bx / 2), (y0 - by, y0), (P.beacon_z - t, P.beacon_z))


def beacon():
    d, h = P.beacon
    y = MY - H - P.beacon_bracket[1] + d / 2 - 5.0
    return cyl(d, (MX, y, P.beacon_z), (MX, y, P.beacon_z + h))


def mic():
    d, l = P.mic
    return cyl(d, (MX + H, MY, P.mic_z), (MX + H + l, MY, P.mic_z))


def elec_box():
    x, y, z = P.box
    y0 = MY - H - 5.0      # behind the horn clamp band thickness
    return box_span((MX - x / 2, MX + x / 2), (y0 - y, y0), (P.box_z, P.box_z + z))


def antennas():
    x, y, z = P.box
    y0 = MY - H - 5.0 - y / 2
    zt = P.box_z + z
    d, h = P.antenna
    return Part.makeCompound([cyl(d, (MX + s * (x / 2 - 30.0), y0, zt), (MX + s * (x / 2 - 30.0), y0, zt + h))
                              for s in (-1, 1)])
