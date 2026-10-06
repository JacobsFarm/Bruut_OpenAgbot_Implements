"""Bodemvolging van de eenvoudige toediener versie 2 (schijf + mes), vergeleken met versie 1 en de geavanceerde.

Werkt met elke Python met matplotlib (ook de Python van FreeCAD):
    python plot_ground2.py        -> previews/12_ground_following_comparison.png + kerngetallen in de console
Bronnen op dezelfde 80 robotposities in werkstand:
- geavanceerd: ground_advanced_reference.json (uit ../advanced/animate_lfa.prepare())
- versie 1:    ground_simple_v1_reference.json (uit ../simple/lfs_ground.solve())
- versie 2:    lfs2_ground.solve() (dit model, actuator helemaal uit)
"""
import json
import os
import sys

sys.dont_write_bytecode = True

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import lfs2_params as P
import lfs2_ground as GR

FOLDER = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(FOLDER, "previews", "12_ground_following_comparison.png")
V1_JSON = os.path.join(FOLDER, "ground_simple_v1_reference.json")

# referentiepalet: categorisch slot 1-3 (gevalideerd, ook alle paren), tekst- en oppervlaktokens
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
ADV = "#2a78d6"
V1 = "#eb6834"
V2 = "#1baf7a"
CUT = "#8a8984"          # snede van de schijf: neutrale referentielaag


def data():
    adv = GR.load_advanced()
    work = [f for f in adv["frames"] if f["phase"] == "work"]
    ys = [f["y"] for f in work]
    with open(V1_JSON, encoding="utf-8") as handle:
        v1 = {round(f["y"], 1): f["depth"] for f in json.load(handle)["frames"]}
    sol = [GR.solve(y) for y in ys]
    return {"y": ys, "adv": [f["depth"] for f in work], "v1": [v1[round(y, 1)] for y in ys],
            "v2": [[r["depth"] for r in s["rows"]] for s in sol], "cut": [[r["disc"] for r in s["rows"]] for s in sol]}


def stats(rows):
    flat = [d for r in rows for d in r]
    mean = sum(flat) / len(flat)
    sd = (sum((d - mean) ** 2 for d in flat) / len(flat)) ** 0.5
    return {"min": min(flat), "max": max(flat), "mean": mean, "sd": sd,
            "share_25_55": 100.0 * sum(1 for d in flat if 25.0 <= d <= 55.0) / len(flat),
            "out": sum(1 for d in flat if d <= 0.0),
            "per_row": [(min(r[i] for r in rows), sum(r[i] for r in rows) / len(rows), max(r[i] for r in rows))
                        for i in range(len(rows[0]))]}


def style(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def nl(v, dec=0):
    return ("%.*f" % (dec, v)).replace(".", ",")


def legend(ax, ncol):
    leg = ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=ncol, frameon=False, fontsize=8.5,
                    borderaxespad=0.2, handlelength=1.8)
    for t in leg.get_texts():
        t.set_color(INK_2)


def main(out=OUT):
    d = data()
    st = {k: stats(d[k]) for k in ("adv", "v1", "v2", "cut")}
    dist = [(y - d["y"][0]) / 1000.0 for y in d["y"]]

    fig = plt.figure(figsize=(10.5, 7.4), dpi=150, facecolor=SURFACE)
    gs = fig.add_gridspec(2, 1, height_ratios=(1.3, 1.0), hspace=0.58)
    ax = fig.add_subplot(gs[0])
    style(ax)
    for rows, color, name, lab in ((d["cut"], CUT, "snede", "snede van de schijf (gemiddelde, band = min-max)"),
                                   (d["v2"], V2, "mes", "mespunt (gemiddelde, band = min-max)")):
        lo = [min(r) for r in rows]
        hi = [max(r) for r in rows]
        mean = [sum(r) / len(r) for r in rows]
        ax.fill_between(dist, lo, hi, color=color, alpha=0.18, linewidth=0)
        ax.plot(dist, mean, color=color, linewidth=2.0, label=lab)
        ax.text(dist[-1] + 0.06, mean[-1], name, color=INK, fontsize=9, va="center")
    for depth, txt in ((P.work_depth, "schijf\ningesteld %d mm" % P.work_depth),
                       (P.knife_depth, "mes\ningesteld %d mm" % P.knife_depth)):
        ax.axhline(depth, color=INK_2, linewidth=0.9, linestyle=(0, (4, 3)))
    ax.text(dist[-1] + 0.06, P.work_depth + 8.0, "ingesteld:\nschijf %d, mes %d mm" % (P.work_depth, P.knife_depth),
            color=INK_2, fontsize=7.5, va="center")
    ax.set_xlim(dist[0], dist[-1] + 0.95)
    ax.set_ylim(0, 75)
    ax.invert_yaxis()
    ax.set_xlabel("afgelegde weg in werkstand (m)", color=INK_2, fontsize=9)
    ax.set_ylabel("diepte onder maaiveld (mm)", color=INK_2, fontsize=9)
    ax.set_title("Versie 2: snede van de schijf en mespunt langs de hobbelige strook", loc="left", color=INK,
                 fontsize=11.5, fontweight="bold", pad=22)
    legend(ax, 2)

    bx = fig.add_subplot(gs[1])
    style(bx)
    w = 0.25
    series = ((st["adv"], ADV, "geavanceerd (schijf + mes op veerarm)"), (st["v1"], V1, "eenvoudig v1 (alleen mes)"),
              (st["v2"], V2, "eenvoudig v2 (schijf + mes)"))
    for k, (s, color, name) in enumerate(series):
        for i, (mn, me, mx) in enumerate(s["per_row"]):
            x = i + 1 + (k - 1) * w * 1.12
            bx.bar(x, mx - mn, bottom=mn, width=w, color=color, alpha=0.88, linewidth=0, label=name if i == 0 else None)
            bx.plot([x - w / 2.0, x + w / 2.0], [me, me], color=SURFACE, linewidth=2.0)
            bx.text(x, mx + 1.5, "%s-%s" % (nl(mn), nl(mx)), ha="center", va="top", fontsize=6.8, color=INK_2)
    bx.set_xticks(range(1, len(P.row_x) + 1))
    bx.set_xticklabels(["rij %d\nx = %s" % (i + 1, nl(x)) for i, x in enumerate(P.row_x)], fontsize=8.5)
    bx.set_ylim(-5, 78)
    bx.invert_yaxis()
    bx.set_ylabel("mesdiepte (mm)", color=INK_2, fontsize=9)
    bx.set_title("Mesdiepte per rij (balk = min-max, streep = gemiddelde)", loc="left", color=INK, fontsize=10.5,
                 fontweight="bold", pad=20)
    legend(bx, 3)

    lines = []
    for key, name in (("adv", "geavanceerd"), ("v1", "v1"), ("v2", "v2")):
        s = st[key]
        lines.append("%s: %s-%s mm, gem. %s, sd %s, %s%% tussen 25-55" % (
            name, nl(s["min"]), nl(s["max"]), nl(s["mean"]), nl(s["sd"], 1), nl(s["share_25_55"])))
    c = st["cut"]
    lines.append("snede v2: %s-%s mm, gem. %s" % (nl(c["min"]), nl(c["max"]), nl(c["mean"])))
    fig.text(0.125, 0.0, "mesdiepte   " + "   |   ".join(lines[:2]) + "\n" + "   |   ".join(lines[2:]),
             color=INK_2, fontsize=7.8, va="bottom")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return st


if __name__ == "__main__":
    for k, s in main().items():
        print(k, {a: (round(b, 1) if isinstance(b, float) else b) for a, b in s.items() if a != "per_row"},
              [tuple(round(x, 1) for x in r) for r in s["per_row"]])
