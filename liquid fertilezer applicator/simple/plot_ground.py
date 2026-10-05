"""Vergelijkt de bodemvolging van de eenvoudige en de geavanceerde toediener op dezelfde strook.

Werkt met elke Python met matplotlib (ook de Python van FreeCAD):
    python plot_ground.py              -> previews/12_ground_following_comparison.png + tabel in de console
De geavanceerde variant komt uit ground_advanced_reference.json (gemaakt met ../advanved/animate_lfa.prepare()).
De eenvoudige variant wordt op dezelfde robotposities doorgerekend (lfs_ground.solve, actuator helemaal uit).
"""
import os
import sys

sys.dont_write_bytecode = True

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import lfs_params as P
import lfs_ground as GR

FOLDER = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(FOLDER, "previews", "12_ground_following_comparison.png")

# kleuren: referentiepalet (categorisch slot 1 en 2, gevalideerd paar), tekst- en oppervlaktokens
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
ADV = "#2a78d6"
SIM = "#eb6834"


def data():
    adv = GR.load_advanced()
    work = [f for f in adv["frames"] if f["phase"] == "work"]
    ys = [f["y"] for f in work]
    adv_rows = [f["depth"] for f in work]
    sim_rows = [[r["depth"] for r in GR.solve(y)["rows"]] for y in ys]
    return ys, adv_rows, sim_rows


def stats(rows):
    flat = [d for r in rows for d in r]
    mean = sum(flat) / len(flat)
    sd = (sum((d - mean) ** 2 for d in flat) / len(flat)) ** 0.5
    in_band = 100.0 * sum(1 for d in flat if 25.0 <= d <= 55.0) / len(flat)
    return {"min": min(flat), "max": max(flat), "mean": mean, "sd": sd, "share_25_55": in_band,
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


def main(out=OUT):
    ys, adv_rows, sim_rows = data()
    sa, ss = stats(adv_rows), stats(sim_rows)
    dist = [(y - ys[0]) / 1000.0 for y in ys]

    fig = plt.figure(figsize=(10.5, 7.2), dpi=150, facecolor=SURFACE)
    gs = fig.add_gridspec(2, 1, height_ratios=(1.35, 1.0), hspace=0.55)
    ax = fig.add_subplot(gs[0])
    style(ax)
    for rows, color, name in ((adv_rows, ADV, "geavanceerd"), (sim_rows, SIM, "eenvoudig")):
        lo = [min(r) for r in rows]
        hi = [max(r) for r in rows]
        mean = [sum(r) / len(r) for r in rows]
        ax.fill_between(dist, lo, hi, color=color, alpha=0.18, linewidth=0)
        ax.plot(dist, mean, color=color, linewidth=2.0, label=name + ": gemiddelde van 5 rijen, band = min-max")
        ax.text(dist[-1] + 0.06, mean[-1], name, color=INK, fontsize=9, va="center")
    ax.axhline(P.work_depth, color=INK_2, linewidth=1.0, linestyle=(0, (4, 3)))
    ax.text(dist[-1] + 0.06, P.work_depth + 7.0, "ingesteld\n40 mm", color=INK_2, fontsize=8, va="center")
    ax.set_xlim(dist[0], dist[-1] + 0.75)
    ax.set_ylim(0, 70)
    ax.invert_yaxis()
    ax.set_xlabel("afgelegde weg in werkstand (m)", color=INK_2, fontsize=9)
    ax.set_ylabel("mesdiepte onder maaiveld (mm)", color=INK_2, fontsize=9)
    ax.set_title("Mesdiepte langs de hobbelige strook (zelfde maaiveld en rijplan)", loc="left", color=INK,
                 fontsize=11.5, fontweight="bold", pad=22)
    leg = ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2, frameon=False, fontsize=8.5,
                    borderaxespad=0.2, handlelength=1.8)
    for t in leg.get_texts():
        t.set_color(INK_2)

    bx = fig.add_subplot(gs[1])
    style(bx)
    w = 0.32
    for k, (st, color, name) in enumerate(((sa, ADV, "geavanceerd"), (ss, SIM, "eenvoudig"))):
        for i, (mn, me, mx) in enumerate(st["per_row"]):
            x = i + 1 + (k - 0.5) * w * 1.15
            bx.bar(x, mx - mn, bottom=mn, width=w, color=color, alpha=0.85, linewidth=0,
                   label=name if i == 0 else None)
            bx.plot([x - w / 2.0, x + w / 2.0], [me, me], color=SURFACE, linewidth=2.0)
            bx.text(x, mx + 1.5, "%s-%s" % (nl(mn), nl(mx)), ha="center", va="top", fontsize=7.5, color=INK_2)
    bx.axhline(P.work_depth, color=INK_2, linewidth=1.0, linestyle=(0, (4, 3)))
    bx.set_xticks(range(1, len(P.row_x) + 1))
    bx.set_xticklabels(["rij %d\nx = %s" % (i + 1, nl(x)) for i, x in enumerate(P.row_x)], fontsize=8.5)
    bx.set_ylim(0, 75)
    bx.invert_yaxis()
    bx.set_ylabel("mesdiepte (mm)", color=INK_2, fontsize=9)
    bx.set_title("Bereik per rij (balk = min-max, streep = gemiddelde)", loc="left", color=INK, fontsize=10.5,
                 fontweight="bold", pad=20)
    leg = bx.legend(loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=2, frameon=False, fontsize=8.5,
                    borderaxespad=0.2)
    for t in leg.get_texts():
        t.set_color(INK_2)

    note = ("geavanceerd: %s-%s mm, gem. %s, sd %s, %s%% tussen 25 en 55 mm   |   eenvoudig: %s-%s mm, gem. %s, sd %s, "
            "%s%% tussen 25 en 55 mm" % (nl(sa["min"]), nl(sa["max"]), nl(sa["mean"]), nl(sa["sd"], 1),
                                         nl(sa["share_25_55"]), nl(ss["min"]), nl(ss["max"]), nl(ss["mean"]),
                                         nl(ss["sd"], 1), nl(ss["share_25_55"])))
    fig.text(0.125, 0.015, note, color=INK_2, fontsize=8)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return sa, ss


if __name__ == "__main__":
    sa, ss = main()
    for name, st in (("geavanceerd", sa), ("eenvoudig", ss)):
        print(name, {k: (round(v, 1) if isinstance(v, float) else [tuple(round(x, 1) for x in r) for r in v])
                     for k, v in st.items()})
