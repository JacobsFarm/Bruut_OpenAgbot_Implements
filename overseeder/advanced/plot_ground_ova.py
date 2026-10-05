"""Bodemvolging van de geavanceerde doorzaaimachine, vergeleken met de eenvoudige versie en de starre balk van de
toediener simple_v2.

Werkt met elke Python met matplotlib (ook de Python van FreeCAD):
    python plot_ground_ova.py      -> previews/13_ground_following.png + kerngetallen in de console
Alle drie op dezelfde 80 robotposities in werkstand over dezelfde hobbelige strook. Afwijking van de ingestelde
snijdiepte (doorzaaiers 15 mm, simple_v2 45 mm).
"""
import os
import sys

sys.dont_write_bytecode = True

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import ova_params as P
import ova_ground as GR

FOLDER = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(FOLDER, "previews", "13_ground_following.png")

# referentiepalet (gelijk aan de andere grafieken): slot 1-3, gevalideerd op alle paren; tekst- en oppervlaktokens
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
SIMPLE = "#2a78d6"      # eenvoudige doorzaaier: zelfde kleur als in ../simple
ADV = "#eb6834"         # geavanceerde doorzaaier
V2 = "#1baf7a"          # toediener simple_v2: zelfde kleur als in ../simple


def data():
    ys = GR.work_positions()
    adv = [GR.solve(y) for y in ys]
    simple = [GR.SG.solve(y) for y in ys]
    g2 = GR.SG.load_v2()
    import lfs2_params as P2
    return {"y": ys,
            "adv": [[r["disc"] - P.work_depth for r in s["rows"]] for s in adv],
            "simple": [[r["disc"] - 15.0 for r in s["rows"]] for s in simple],
            "v2": [[r["disc"] - P2.work_depth for r in g2.solve(y)["rows"]] for y in ys],
            "depth": [[r["disc"] for r in s["rows"]] for s in adv]}


def stats(rows):
    flat = [d for r in rows for d in r]
    mean = sum(flat) / len(flat)
    sd = (sum((d - mean) ** 2 for d in flat) / len(flat)) ** 0.5
    return {"min": min(flat), "max": max(flat), "mean": mean, "sd": sd,
            "share_3": 100.0 * sum(1 for d in flat if abs(d) <= 3.0) / len(flat),
            "share_5": 100.0 * sum(1 for d in flat if abs(d) <= 5.0) / len(flat)}


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
    st = {k: stats(d[k]) for k in ("adv", "simple", "v2")}
    dist = [(y - d["y"][0]) / 1000.0 for y in d["y"]]

    fig = plt.figure(figsize=(10.5, 7.8), dpi=150, facecolor=SURFACE)
    gs = fig.add_gridspec(2, 1, height_ratios=(1.25, 1.0), hspace=0.62)
    ax = fig.add_subplot(gs[0])
    style(ax)
    ax.axhspan(-5.0, 5.0, color=GRID, alpha=0.55, linewidth=0)
    ax.axhline(0.0, color=INK_2, linewidth=0.9, linestyle=(0, (4, 3)))
    series = ((d["v2"], V2, "simple_v2", "toediener simple_v2: starre balk (ingesteld 45 mm)", -6.0),
              (d["simple"], SIMPLE, "eenvoudig", "doorzaaier eenvoudig: sleeparm, ring op scheve schijf", 0.0),
              (d["adv"], ADV, "geavanceerd", "doorzaaier geavanceerd: parallellogram, ringen aan 2 kanten", 6.0))
    for rows, color, name, lab, dy in series:
        lo = [min(r) for r in rows]
        hi = [max(r) for r in rows]
        mean = [sum(r) / len(r) for r in rows]
        ax.fill_between(dist, lo, hi, color=color, alpha=0.15, linewidth=0)
        ax.plot(dist, mean, color=color, linewidth=1.8, label=lab)
        ax.text(dist[-1] + 0.06, mean[-1] + dy, name, color=INK, fontsize=9, va="center")
    ax.text(dist[-1] + 0.06, 12.5, "band ±5 mm", color=INK_2, fontsize=7.5, va="center")
    ax.set_xlim(dist[0], dist[-1] + 1.05)
    ax.set_ylim(-38, 28)
    ax.invert_yaxis()
    ax.set_xlabel("afgelegde weg in werkstand (m)", color=INK_2, fontsize=9)
    ax.set_ylabel("afwijking snijdiepte (mm, + = dieper)", color=INK_2, fontsize=9)
    ax.set_title("Afwijking van de ingestelde snijdiepte (gemiddelde, band = min-max van alle rijen)",
                 loc="left", color=INK, fontsize=11, fontweight="bold", pad=34)
    legend(ax, 2)

    bx = fig.add_subplot(gs[1])
    style(bx)
    bx.axhspan(P.work_depth - 5.0, P.work_depth + 5.0, color=GRID, alpha=0.55, linewidth=0)
    bx.axhline(P.work_depth, color=INK_2, linewidth=0.9, linestyle=(0, (4, 3)))
    w = 0.42
    for i in range(len(P.row_x)):
        vals = [r[i] for r in d["depth"]]
        mn, mx, me = min(vals), max(vals), sum(vals) / len(vals)
        bx.bar(i + 1, mx - mn, bottom=mn, width=w, color=ADV, alpha=0.88, linewidth=0,
               label="doorzaaier geavanceerd, snijdiepte per rij" if i == 0 else None)
        bx.plot([i + 1 - w / 2.0, i + 1 + w / 2.0], [me, me], color=SURFACE, linewidth=2.0)
        bx.text(i + 1, mx + 1.0, "%s-%s" % (nl(mn), nl(mx)), ha="center", va="top", fontsize=7.2, color=INK_2)
    bx.text(len(P.row_x) + 0.55, P.work_depth, "ingesteld\n%d mm" % P.work_depth, color=INK_2, fontsize=7.5,
            va="center")
    bx.set_xticks(range(1, len(P.row_x) + 1))
    bx.set_xticklabels(["rij %d\nx = %s" % (i + 1, nl(x, 1)) for i, x in enumerate(P.row_x)], fontsize=8)
    bx.set_xlim(0.4, len(P.row_x) + 1.2)
    bx.set_ylim(0, 30)
    bx.invert_yaxis()
    bx.set_ylabel("snijdiepte schijf (mm)", color=INK_2, fontsize=9)
    bx.set_title("Geavanceerd: snijdiepte per rij (balk = min-max, streep = gemiddelde)", loc="left", color=INK,
                 fontsize=10.5, fontweight="bold", pad=20)
    legend(bx, 1)

    parts = []
    for key, name in (("adv", "geavanceerd"), ("simple", "eenvoudig"), ("v2", "simple_v2")):
        s = st[key]
        parts.append("%s: %s tot %s mm, sd %s, %s%% binnen ±3, %s%% binnen ±5" % (
            name, nl(s["min"], 1), nl(s["max"], 1), nl(s["sd"], 1), nl(s["share_3"], 1), nl(s["share_5"], 1)))
    fig.text(0.125, 0.0, "afwijking   " + "\n                 ".join(parts), color=INK_2, fontsize=7.8, va="bottom")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return st


if __name__ == "__main__":
    for k, s in main().items():
        print(k, {a: round(b, 1) for a, b in s.items()})
