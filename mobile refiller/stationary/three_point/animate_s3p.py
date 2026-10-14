"""Animation: a refill visit at the stationary three-point frame on the headland.

The station stands on the headland, parallel to the field edge, with its arm pinned out to the left (towards the
field). The working robot finishes pass p, drives along the headland to the station, stops with its funnel under the
nozzle (on the left side of the frame), is topped up with 120 l (beacon amber), turns round on the headland and
drives back into pass p + 1. The scene, the simulation, the checks and the rendering are shared by all stations:
../stc_anim.py.

Use in FreeCAD (this folder and ../ on sys.path, see run_in_freecad.py):
    import animate_s3p
    animate_s3p.build()                              # build the document Stationary_three_point_on_robot_animation
    animate_s3p.play()                               # play live, animate_s3p.stop()
    animate_s3p.summary()                            # key figures of the run
    animate_s3p.check_docked()                       # station - working robot in the docked pose (must be empty)
    animate_s3p.check_fit()                          # the same for every frame near the station (must be empty)
    animate_s3p.render_all(r"C:\\temp\\s3p_frames")
    import make_gif_s3p; make_gif_s3p.main(r"C:\\temp\\s3p_frames", r"previews\\animation_refill_visit.gif")
"""
import build_s3p as BX
import s3p_calc as CX
import s3p_parts as T
import stc_anim as SA

GIF = "animation_refill_visit.gif"
_visit = {}


def _build_into(doc):
    root, M = BX.build_into(doc, 0.0, SA.IBC_START)
    return [BX.ROOT], M


def visit():
    if "v" not in _visit:
        carrier = SA.Carrier("s3p", "three-point frame", "Stationary_three_point_on_robot_animation",
                             _build_into, ["ibc1"], CX.pump_geometry,
                             BX.check_docked, BX.OK)
        _visit["v"] = SA.Visit(carrier, T.mast_spec())
    return _visit["v"]


def build():
    return visit().build()


def play(loop=False, follow=True, speed=5.0):
    visit().play(loop, follow, speed)


def stop():
    visit().stop()


def summary():
    return visit().summary()


def check_docked(doc=None, tol=1.0):
    return visit().check_docked(doc, tol)


def check_fit(doc=None, tol=1.0, step=2, gap=400.0, log=None):
    return visit().check_fit(doc, tol, step, gap, log)


def render_all(folder, size=(720, 480)):
    return visit().render_all(folder, size)
