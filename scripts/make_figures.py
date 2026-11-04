"""Draw docs/img/hero.png, cube.png and spans.png from the seeded synthetic site."""

import matplotlib.pyplot as plt
import numpy as np
from _style import BG, GOLD, GOLD_DIM, IMG, LINE, MUTED, SERIF, TEXT, style, title
from matplotlib.patches import Rectangle

from rack_check.capacity import level_capacity_kg, sag_mm
from rack_check.catalog import load
from rack_check.check import check, summarise
from rack_check.synthetic import site

SEED = 4
CAT = load()


def hero() -> None:
    rs = check(site(SEED), CAT)
    s = summarise(rs)
    fig = plt.figure(figsize=(16, 6.4), dpi=100)
    fig.text(0.05, 0.80, "rack-check", fontfamily=SERIF, fontsize=50, color=TEXT)
    fig.text(0.05, 0.71, "Which rack beams carry more than they should.", fontsize=17, color=TEXT)
    fig.text(
        0.05,
        0.655,
        "Beam bending by hand formula, every level, one table.",
        fontsize=17,
        color=MUTED,
    )
    fig.add_artist(plt.Line2D([0.05, 0.12], [0.6, 0.6], color=GOLD, lw=2))
    fig.text(
        0.95,
        0.82,
        f"{len(s.bays_over)} of {s.bays} bays over limit",
        fontfamily=SERIF,
        fontsize=36,
        color=GOLD,
        ha="right",
    )
    fig.text(
        0.95,
        0.74,
        f"synthetic site, seed {SEED}, illustrative beam data",
        fontsize=13,
        color=MUTED,
        ha="right",
    )
    ax = fig.add_axes((0.05, 0.1, 0.9, 0.44))
    bays = sorted({r.level.bay for r in rs})
    x0 = {}
    x = 0.0
    for b in bays:
        x0[b] = x
        x += next(r.level.span_m for r in rs if r.level.bay == b) + 0.25
    for r in rs:
        u = min(r.utilisation, 1.5)
        col = GOLD if not r.ok else plt.cm.Greys_r(0.15 + 0.5 * u)  # type: ignore[attr-defined]
        ax.add_patch(
            Rectangle((x0[r.level.bay], r.level.level - 1), r.level.span_m, 0.82, color=col, lw=0)
        )
    ax.set_xlim(-0.3, x)
    ax.set_ylim(-0.1, 4)
    ax.axis("off")
    ax.text(
        0,
        -0.08,
        "each block is one level, lighter = more of its safe load used, gold = over",
        fontsize=10,
        color=MUTED,
        va="top",
        transform=ax.transAxes,
    )
    fig.savefig(IMG / "hero.png", facecolor=BG)
    plt.close(fig)


def cube() -> None:
    spans = np.linspace(1.2, 4.0, 60)
    p = CAT.profiles["B100"]
    fig, ax = plt.subplots(figsize=(9, 5))
    for kg, c in ((1000, GOLD_DIM), (2000, GOLD)):
        ax.plot(
            spans,
            sag_mm(np.full_like(spans, kg), spans, p.i_m4, CAT),
            color=c,
            lw=2,
            label=f"{kg:,} kg on the level",
        )
    ax.plot(
        spans,
        spans / CAT.deflection_ratio * 1000,
        color=MUTED,
        ls="--",
        lw=1.2,
        label=f"limit span/{CAT.deflection_ratio:g}",
    )
    ax.set_xlabel("beam span, m")
    ax.set_ylabel("mid-span sag, mm")
    ax.legend(frameon=False)
    title(
        ax,
        "Sag grows with the cube of the span",
        "B100 beam pair, uniform load, illustrative steel and section values",
    )
    fig.tight_layout()
    fig.savefig(IMG / "cube.png")
    plt.close(fig)


def spans() -> None:
    sp = np.linspace(1.2, 4.0, 60)
    fig, ax = plt.subplots(figsize=(9, 5))
    shades = [MUTED, GOLD_DIM, "#B89A3A", GOLD]
    for (name, p), c in zip(CAT.profiles.items(), shades, strict=True):
        ax.plot(sp, level_capacity_kg(sp, p.i_m4, p.w_m3, CAT), color=c, lw=2, label=name)
    ax.set_xlabel("beam span, m")
    ax.set_ylabel("safe load per level, kg")
    ax.set_ylim(0, 12000)
    ax.legend(frameon=False, title_fontsize=9)
    ax.grid(color=LINE)
    title(
        ax,
        "Safe load per level by beam and span",
        "Lower of the sag and stress limits; illustrative, not a manufacturer's table",
    )
    fig.tight_layout()
    fig.savefig(IMG / "spans.png")
    plt.close(fig)


if __name__ == "__main__":
    style()
    IMG.mkdir(parents=True, exist_ok=True)
    hero()
    cube()
    spans()
