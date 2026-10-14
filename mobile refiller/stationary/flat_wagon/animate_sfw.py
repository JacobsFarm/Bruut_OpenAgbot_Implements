"""Animation: a refill visit at the stationary flat wagon (6 IBCs) on the headland.

The station stands on the headland, parallel to the field edge, with its arm pinned out to the left (towards the
field). The working robot finishes pass p, drives along the headland to the station, stops with its funnel under the
nozzle (beside the rear left corner of the wagon, arm reach 840 mm, nozzle at 1270 mm), is topped up with 120 l
(beacon amber), turns round on the headland and drives back into pass p + 1. The 6 IBCs share one suction
header: their levels drop together (20 l each). The scene, the simulation, the checks and the rendering are
shared by all stations: ../stc_anim.py.

Use in FreeCAD (this folder and ../ on sys.path, see run_in_freecad.py):
    import animate_sfw
    animate_sfw.build()                              # build the document Stationary_flat_wagon_on_robot_animation
    animate_sfw.play()                               # play live, animate_sfw.stop()
    animate_sfw.summary()                            # key figures of the run
    animate_sfw.check_docked()                       # station - working robot in the docked pose (must be empty)
    animate_sfw.check_fit()                          # the same for every frame near the station (must be empty)
    animate_sfw.render_all(r"C:\\temp\\sfw_frames")
    import make_gif_sfw; make_gif_sfw.main(r"C:\\temp\\sfw_frames", r"previews\\animation_refill_visit.gif")
"""
import build_sfw as BX
import sfw_calc as CX
import sfw_parts as T
import stc_anim as SA

GIF = "animation_refill_visit.gif"
_visit = {}


def _build_into(doc):
    root, M = BX.build_into(doc, 0.0, SA.IBC_START)
    return [BX.WAGON, BX.ROOT], M


def visit():
    if "v" not in _visit:
        carrier = SA.Carrier("sfw", "flat wagon, 6 IBCs", "Stationary_flat_wagon_on_robot_animation",
                             _build_into, BX.ibc_tags(), CX.pump_geometry,
                             BX.check_docked, BX.OK)
        carrier.dock_view = (7600.0, 1300.0)       # camera at the nozzle: distance, target height (IBCs on the deck)
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
