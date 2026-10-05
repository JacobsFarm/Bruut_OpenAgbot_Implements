"""Bodemvolging van de doorzaaimachine, vergeleken met de starre balk van simple_v2.

Werkt met elke Python met matplotlib (ook de Python van FreeCAD):
    python plot_ground_ovs.py      -> previews/13_ground_following.png + kerngetallen in de console
Beide op dezelfde 80 robotposities in werkstand over dezelfde hobbelige strook (ovs_ground.work_positions):
- doorzaaier: ovs_ground.solve() (8 sleeparmen met dieptering, hefraam zwevend op gasveren);
- simple_v2: lfs2_ground.solve() (5 schijven star aan een balk met 2 dieptewielen).
Afwijking van de ingestelde snijdiepte (doorzaaier 15 mm, simple_v2 45 mm).
"""
import os
import sys

sys.dont_write_bytecode = True

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import ovs_params as P
import ovs_ground as GR

FOLDER = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(FOLDER, "previews", "13_ground_following.png")

# referentiepalet (gelijk aan de toedieners): categorisch slot 1 en 3, tekst- en oppervlaktokens
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
OVS = "#2a78d6"
V2 = "#1baf7a"


def data():
    ys = GR.work_positions()
    sol = [GR.solve(y) for y in ys]
    g2 = GR.load_v2()
    import lfs2_params as P2
    v2 = [[r["disc"] - P2.work_depth for r in g2.solve(y)["rows"]] for y in ys]
    ovs = [[r["disc"] - P.disc_depth for r in s["rows"]] for s in sol]
    depth = [[r["disc"] for r in s["rows"]] for s in sol]
    return {"y": ys, "ovs": ovs, "v2": v2, "depth": depth, "sol": sol}


def stats(rows):
    flat = [d for r in rows for d in r]
    mean = sum(flat) / len(flat)
    sd = (sum((d - mean) ** 2 for d in flat) / len(flat)) ** 0.5
    return {"min": min(flat), "max": max(flat), "mean": mean, "sd": sd,
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
    st_o = stats(d["ovs"])
    st_2 = stats(d["v2"])
    dist = [(y - d["y"][0]) / 1000.0 for y in d["y"]]

    fig = plt.figure(figsize=(10.5, 7.6), dpi=150, facecolor=SURFACE)
    gs = fig.add_gridspec(2, 1, height_ratios=(1.25, 1.0), hspace=0.6)
    ax = fig.add_subplot(gs[0])
    style(ax)
    ax.axhspan(-5.0, 5.0, color=GRID, alpha=0.55, linewidth=0)
    ax.axhline(0.0, color=INK_2, linewidth=0.9, linestyle=(0, (4, 3)))
    for rows, color, name, lab, dy in ((d["v2"], V2, "simple_v2", "simple_v2: 5 schijven star aan de balk (ingesteld 45 mm)", -5.0),
                                       (d["ovs"], OVS, "doorzaaier", "doorzaaier: 8 sleeparmen met dieptering (ingesteld 15 mm)", 4.0)):
        lo = [min(r) for r in rows]
        hi = [max(r) for r in rows]
        mean = [sum(r) / len(r) for r in rows]
        ax.fill_between(dist, lo, hi, color=color, alpha=0.18, linewidth=0)
        ax.plot(dist, mean, color=color, linewidth=2.0, label=lab)
        ax.text(dist[-1] + 0.06, mean[-1] + dy, name, color=INK, fontsize=9, va="center")
    ax.text(dist[-1] + 0.06, 9.0, "band ±5 mm", color=INK_2, fontsize=7.5, va="center")
    ax.set_xlim(dist[0], dist[-1] + 0.95)
    ax.set_ylim(-38, 28)
    ax.invert_yaxis()
    ax.set_xlabel("afgelegde weg in werkstand (m)", color=INK_2, fontsize=9)
    ax.set_ylabel("afwijking snijdiepte (mm, + = dieper)", color=INK_2, fontsize=9)
    ax.set_title("Afwijking van de ingestelde snijdiepte langs de hobbelige strook (gemiddelde, band = min-max van alle rijen)",
                 loc="left", color=INK, fontsize=11, fontweight="bold", pad=22)
    legend(ax, 2)

    bx = fig.add_subplot(gs[1])
    style(bx)
    bx.axhspan(P.disc_depth - 5.0, P.disc_depth + 5.0, color=GRID, alpha=0.55, linewidth=0)
    bx.axhline(P.disc_depth, color=INK_2, linewidth=0.9, linestyle=(0, (4, 3)))
    w = 0.42
    for i in range(len(P.row_x)):
        vals = [r[i] for r in d["depth"]]
        mn, mx, me = min(vals), max(vals), sum(vals) / len(vals)
        bx.bar(i + 1, mx - mn, bottom=mn, width=w, color=OVS, alpha=0.88, linewidth=0,
               label="doorzaaier, zaaidiepte per rij" if i == 0 else None)
        bx.plot([i + 1 - w / 2.0, i + 1 + w / 2.0], [me, me], color=SURFACE, linewidth=2.0)
        bx.text(i + 1, mx + 1.0, "%s-%s" % (nl(mn), nl(mx)), ha="center", va="top", fontsize=7.2, color=INK_2)
    bx.text(len(P.row_x) + 0.55, P.disc_depth, "ingesteld\n%d mm" % P.disc_depth, color=INK_2, fontsize=7.5, va="center")
    bx.set_xticks(range(1, len(P.row_x) + 1))
    bx.set_xticklabels(["rij %d\nx = %s" % (i + 1, nl(x, 1)) for i, x in enumerate(P.row_x)], fontsize=8)
    bx.set_xlim(0.4, len(P.row_x) + 1.2)
    bx.set_ylim(0, 30)
    bx.invert_yaxis()
    bx.set_ylabel("snijdiepte schijf (mm)", color=INK_2, fontsize=9)
    bx.set_title("Snijdiepte per rij (balk = min-max, streep = gemiddelde)", loc="left", color=INK, fontsize=10.5,
                 fontweight="bold", pad=20)
    legend(bx, 1)

    line = ("doorzaaier: %s tot %s mm, sd %s, %s%% binnen ±5 mm   |   simple_v2: %s tot %s mm, sd %s, %s%% binnen ±5 mm" % (
        nl(st_o["min"], 1), nl(st_o["max"], 1), nl(st_o["sd"], 1), nl(st_o["share_5"], 1),
        nl(st_2["min"], 1), nl(st_2["max"], 1), nl(st_2["sd"], 1), nl(st_2["share_5"], 1)))
    fig.text(0.125, 0.0, "afwijking   " + line, color=INK_2, fontsize=7.8, va="bottom")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return {"overseeder": st_o, "simple_v2": st_2}


if __name__ == "__main__":
    for k, s in main().items():
        print(k, {a: round(b, 1) for a, b in s.items()})
