"""Macro om de veldanimaties in een eigen FreeCAD-proces te renderen (los van de MCP en zonder time-out):

    freecad.exe render_fld.py            met omgevingsvariabelen:
    FLD_JOB    frames | test | check | fit   (alle frames, losse frames, controle van de werktank, of overlap
               refiller - werkrobot in alle frames waarin ze dicht bij elkaar staan)
    FLD_KEY    simple | liquid | station
    FLD_OUT    map voor de frames (frames: frame_0000.png ... + frames.json), of voor de testbeelden
    FLD_FRAMES bij test: framenummers, bijv. "0,400,900"
    FLD_LOG    logbestand (voortgang, fouten, "done")
    FLD_ONLY   far | near: alleen de frames met de camera ver weg / dichtbij opnieuw

FreeCAD sluit zichzelf af als het klaar is. Ook vanuit de GUI te draaien (F6) met FLD_JOB=check als standaard.
"""
import json
import os
import sys
import time
import traceback

sys.dont_write_bytecode = True

try:
    FOLDER = os.path.dirname(os.path.abspath(__file__))
except NameError:
    FOLDER = r"F:\veldrobot\aanbouwdelen\liquid fertilizer applicator\precision_applicator\animations"
if FOLDER not in sys.path:
    sys.path.insert(0, FOLDER)

JOB = os.environ.get("FLD_JOB", "check")
KEY = os.environ.get("FLD_KEY", "simple")
OUT = os.environ.get("FLD_OUT", os.path.join(FOLDER, "previews"))
LOG = os.environ.get("FLD_LOG", os.path.join(OUT, "render_%s_%s.log" % (JOB, KEY)))
STANDALONE = "FLD_JOB" in os.environ


def log(*args):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(" ".join(str(a) for a in args) + "\n")


def main():
    t0 = time.time()
    import FreeCADGui as Gui
    import fld_plan
    import build_fld
    import animate_fld
    if JOB == "check":
        doc = build_fld.build_tank_check(0.0)
        out = {"interference": build_fld.check_interference(doc), "clearance": build_fld.clearance(doc),
               "outline_work": build_fld.worker_outline(doc), "outline_lifted": build_fld.worker_outline(doc, 150.0)}
        log(json.dumps(out))
        return
    run = fld_plan.simulate(KEY)
    log("simulated", len(run["frames"]), "frames", round(time.time() - t0, 1), "s")
    animate_fld.build(KEY, run)
    Gui.getMainWindow().showMaximized()
    log("built", round(time.time() - t0, 1), "s")
    if JOB == "fit":
        only = os.environ.get("FLD_FRAMES")
        hits, n = animate_fld.check_fit(step=int(os.environ.get("FLD_STEP", "4")), log=LOG,
                                        only=[int(v) for v in only.split(",")] if only else None)
        log("check_fit", n, "frames checked, overlaps:", json.dumps({str(k): v for k, v in hits.items()}))
    elif JOB == "test":
        spec = os.environ.get("FLD_FRAMES", "auto")
        if spec == "auto":
            fr = run["frames"]
            pick = lambda cond: next((i for i, f in enumerate(fr) if cond(f)), 0)      # noqa: E731
            idx = [pick(lambda f: f["speed"] > 30.0), pick(lambda f: f["ref"]["state"] in ("pumping",)),
                   pick(lambda f: f["piece"] == "arc" and f["centre"][1] < -40000.0), len(fr) - 1]
        else:
            idx = [int(v) for v in spec.split(",")]
        os.makedirs(OUT, exist_ok=True)
        view = Gui.ActiveDocument.ActiveView
        view.setCameraType("Perspective")
        for i in idx:
            i = min(i, len(run["frames"]) - 1)
            animate_fld.apply_frame(i)
            animate_fld.track_camera(i)
            animate_fld.set_detail(i)
            Gui.updateGui()
            view.saveImage(os.path.join(OUT, "test_%s_%04d.png" % (KEY, i)), 1280, 720, "White")
            log("frame", i, run["frames"][i]["w_text"], "|", run["frames"][i]["ref"]["text"])
        close = os.environ.get("FLD_CLOSE")
        if close:
            from pivy import coin
            x, y = (float(v) for v in close.split(","))
            cam = view.getCameraNode()
            cam.position.setValue(coin.SbVec3f(x + 1500.0, y - 2500.0, 2500.0))
            cam.pointAt(coin.SbVec3f(x, y, 0.0), coin.SbVec3f(0, 0, 1))
            Gui.updateGui()
            view.saveImage(os.path.join(OUT, "test_%s_close.png" % KEY), 1280, 720, "White")
            doc = animate_fld._s["doc"]
            for n in ("anim_closed_1", "anim_flow_1", "anim_slot_1", "anim_band_1"):
                o = doc.getObject(n)
                log(n, o.ViewObject.ShapeColor, len(o.ViewObject.DiffuseColor), o.ViewObject.DiffuseColor[:1],
                    round(o.Shape.Volume))
    else:
        animate_fld.render_all(OUT, log=LOG, only=os.environ.get("FLD_ONLY") or None)
    log("time", round(time.time() - t0, 1), "s")


try:
    main()
except Exception:
    log(traceback.format_exc())
finally:
    log("done")
    if STANDALONE:
        os._exit(0)
