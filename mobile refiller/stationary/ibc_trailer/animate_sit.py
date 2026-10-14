"""Animation: a refill visit at the stationary IBC trailer (1 or 2 IBCs) on the headland.

The trailer stands on the headland, parallel to the field edge, with its arm pinned out to the left (towards the
field). The working robot finishes pass p, drives along the headland to the trailer, stops with its funnel under the
nozzle, is topped up with 120 l (beacon amber), turns round on the headland and drives back into pass p + 1. The
scene, the simulation, the checks and the rendering are shared by all stations: ../stc_anim.py (see there).

Use in FreeCAD (this folder and ../ on sys.path, see run_in_freecad.py); n = 1 or 2 IBCs:
    import animate_sit
    animate_sit.build(n)                             # build the document Stationary_IBC_trailer_<n>_on_robot_animation
    animate_sit.play(n)                              # play live, animate_sit.stop(n)
    animate_sit.summary(n)                           # key figures of the run
    animate_sit.check_docked(n)                      # station - working robot in the docked pose (must be empty)
    animate_sit.check_fit(n)                         # the same for every frame near the station (must be empty)
    animate_sit.render_all(r"C:\\temp\\sit_frames", n)
    import make_gif_sit; make_gif_sit.main(r"C:\\temp\\sit_frames", r"previews\\animation_refill_visit.gif")
"""
import build_sit as BS
import sit_calc as SC
import sit_params as SP
import sit_parts as T
import stc_anim as SA

GIF = {1: "animation_refill_visit.gif", 2: "animation_refill_visit_2ibc.gif"}
_visits = {}


def _build_into(n):
    def build_into(doc):
        BS.STATE["n"] = n
        root, c, M = BS.build_into(doc, n, 0.0, SA.IBC_START)
        return [BS.ROOT], M
    return build_into


def visit(n=1):
    if n not in _visits:
        title = "IBC trailer, %d IBC%s" % (n, "s" if n > 1 else "")
        carrier = SA.Carrier("sit", title, "Stationary_IBC_trailer_%d_on_robot_animation" % n,
                             _build_into(n), ["ibc%d" % (i + 1) for i in range(n)], lambda: SC.pump_geometry(n),
                             BS.check_docked, BS.OK)
        _visits[n] = SA.Visit(carrier, T.mast_spec(SP.cfg(n)))
    return _visits[n]


def build(n=1):
    return visit(n).build()


def play(n=1, loop=False, follow=True, speed=5.0):
    visit(n).play(loop, follow, speed)


def stop(n=None):
    for v in ([visit(n)] if n else list(_visits.values())):
        v.stop()


def summary(n=1):
    return visit(n).summary()


def check_docked(n=1, doc=None, tol=1.0):
    BS.STATE["n"] = n
    return visit(n).check_docked(doc, tol)


def check_fit(n=1, doc=None, tol=1.0, step=2, gap=400.0, log=None):
    return visit(n).check_fit(doc, tol, step, gap, log)


def render_all(folder, n=1, size=(720, 480)):
    return visit(n).render_all(folder, size)
