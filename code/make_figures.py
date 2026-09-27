"""Render the article's figures to graphics/*.png (1600px wide, Medium-friendly).

Run from the code/ folder:  python make_figures.py
"""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from exact import expected_rolls, finished_by_roll

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "graphics"
DATA = ROOT / "data"

BLUE, ORANGE, GREEN = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#1a1a19", "#6b6a66", "#e1e0d9"
EXACT = 37.9003

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 13,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def save(fig, name):
    fig.savefig(OUT / name, dpi=160, bbox_inches="tight", pad_inches=0.3)
    plt.close(fig)
    print("wrote", name)


# --- Data figures -----------------------------------------------------------

def histogram():
    with (DATA / "rolls_100000.csv").open() as f:
        rolls = np.array([int(r["rolls"]) for r in csv.DictReader(f)])
    cdf = finished_by_roll(400)
    pmf = np.diff(np.concatenate([[0], cdf]))  # P(game takes exactly n rolls)

    fig, ax = plt.subplots(figsize=(10, 5))
    bins = np.arange(0.5, 201.5, 1)
    ax.hist(rolls, bins=bins, color=BLUE, alpha=0.55, label="100,000 simulated games")
    n = np.arange(1, len(pmf) + 1)
    ax.plot(n[:200], pmf[:200] * len(rolls), color=INK, lw=1.6, label="Exact distribution")
    ax.axvline(31, color=GREEN, lw=1.5, ls="--")
    ax.axvline(EXACT, color=ORANGE, lw=1.5, ls="--")
    ax.text(31 - 1.5, ax.get_ylim()[1] * 0.93, "median 31", color=GREEN, ha="right")
    ax.text(EXACT + 1.5, ax.get_ylim()[1] * 0.93, "average 37.9", color=ORANGE)
    ax.set_xlim(0, 200)
    ax.set_xlabel("Rolls to finish")
    ax.set_ylabel("Number of games")
    ax.set_title("How long a game of snakes and ladders lasts", loc="left", fontsize=15, color=INK)
    ax.legend(frameon=False, loc="center right")
    save(fig, "02-histogram.png")


def toy_cdf():
    steps = [0, 1, 2, 3, 4, 5]
    finished = [0, 0, 0.75, 1, 1, 1]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.fill_between(steps, finished, 1, step="post", color=ORANGE, alpha=0.25)
    ax.step(steps, finished, where="post", color=BLUE, lw=2.5)
    ax.axhline(1, color=MUTED, lw=1)
    for x, label in [(0.5, "1"), (1.5, "1"), (2.5, "0.25")]:
        ax.text(x, 0.55 if label == "1" else 0.87, label, ha="center", color=ORANGE, fontsize=16, weight="bold")
    ax.text(3.2, 0.45, "shaded area = 1 + 1 + 0.25 = 2.25\n= expected number of rolls",
            color=INK, fontsize=13)
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1.08)
    ax.set_xticks(range(6))
    ax.set_xlabel("Rolls")
    ax.set_ylabel("Share of games finished")
    ax.set_title("Toy board: the unfinished share, added up", loc="left", fontsize=15, color=INK)
    save(fig, "04-toy-cdf.png")


def expected_by_square():
    e = expected_rolls()
    fig, ax = plt.subplots(figsize=(11, 4.8))
    colours = [BLUE] * 100
    from simulate import LADDERS, SNAKES
    for s in SNAKES:
        colours[s] = ORANGE
    for s in LADDERS:
        colours[s] = GREEN
    ax.bar(range(100), e, color=colours, width=0.85)
    ax.annotate(f"from the start: {e[0]:.4f}", xy=(0.4, e[0]), xytext=(12, e[0] - 1),
                arrowprops=dict(arrowstyle="-", color=MUTED), color=INK, va="center")
    ax.set_ylim(0, e.max() * 1.12)
    ax.set_xlim(-1, 100)
    ax.set_xlabel("Square")
    ax.set_ylabel("Expected rolls to finish")
    ax.set_title("Expected rolls to finish from every square", loc="left", fontsize=15, color=INK)
    ax.text(99, max(e) * 0.97, "orange: snake heads   green: ladder feet",
            ha="right", color=MUTED, fontsize=11)
    save(fig, "06-expected-by-square.png")


def estimates_vs_exact():
    with (DATA / "summary.csv").open() as f:
        rows = list(csv.DictReader(f))
    games = [int(r["games"]) for r in rows]
    avg = [float(r["average"]) for r in rows]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.axhline(EXACT, color=ORANGE, lw=2)
    ax.text(2.2e3, EXACT - 0.1, "exact: 37.9003", color=ORANGE, ha="left", va="top")
    ax.plot(games, avg, "o-", color=BLUE, ms=9, lw=1.5)
    for g, a in zip(games, avg):
        ax.annotate(f"{a:.2f}", (g, a), textcoords="offset points", xytext=(0, 12),
                    ha="center", color=BLUE, weight="bold")
    ax.set_xscale("log")
    ax.set_xticks(games, [f"{g:,}" for g in games])
    ax.set_xlim(600, 2e5)
    ax.set_ylim(37.2, 39.1)
    ax.set_xlabel("Simulated games (log scale)")
    ax.set_ylabel("Average rolls")
    ax.set_title("Three runs, three answers, one exact number", loc="left", fontsize=15, color=INK)
    save(fig, "07-estimates-vs-exact.png")


# --- Toy-board diagrams -----------------------------------------------------

def board_row(ax, labels, greyed=()):
    for i, label in enumerate(labels):
        colour = "#f3f2ee" if i in greyed else "white"
        ax.add_patch(FancyBboxPatch((i * 2 - 0.55, -0.55), 1.1, 1.1,
                                    boxstyle="round,pad=0.02,rounding_size=0.15",
                                    fc=colour, ec=INK, lw=1.8))
        ax.text(i * 2, 0, label, ha="center", va="center", fontsize=15, color=INK, weight="bold")


def arc(ax, a, b, label, colour=BLUE, above=True, lw=2.0, dy=0.0):
    rad = -0.45 if above else 0.45
    if b < a:  # a right-to-left arrow bends the other way
        rad = -rad
    y0 = 0.6 if above else -0.6
    ax.add_patch(FancyArrowPatch((a * 2, y0), (b * 2, y0), connectionstyle=f"arc3,rad={rad}",
                                 arrowstyle="-|>", mutation_scale=20, color=colour, lw=lw))
    height = 0.45 * abs(b - a) * 2 / 2
    y = y0 + (height + 0.25 + dy if above else -height - 0.35 - dy)
    ax.text((a + b), y, label, ha="center", va="center", fontsize=14, color=colour, weight="bold",
            bbox=dict(fc="white", ec="none", pad=1))


def toy_ladder():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    board_row(ax, ["Start", "1", "2", "3", "4\nfinish"], greyed=(1,))
    arc(ax, 0, 2, "½")
    arc(ax, 0, 3, "½ (roll 1, ladder)", dy=0.35)
    arc(ax, 2, 3, "½")
    arc(ax, 2, 4, "½", dy=-0.15)
    arc(ax, 3, 4, "1")
    arc(ax, 1, 3, "ladder 1 → 3", colour=GREEN, above=False, lw=3)
    ax.set_xlim(-1, 9)
    ax.set_ylim(-2.3, 3.4)
    ax.axis("off")
    ax.set_title("Toy board: two-sided die, one ladder. Square 1 is never occupied.",
                 loc="left", fontsize=14, color=INK)
    save(fig, "03-toy-ladder.png")


def toy_snake():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    board_row(ax, ["Start", "1", "2", "3", "4\nfinish"], greyed=(3,))
    arc(ax, 0, 1, "½")
    arc(ax, 0, 2, "½", dy=0.2)
    arc(ax, 1, 2, "½")
    arc(ax, 1, 3, "½", colour=ORANGE, dy=0.35)
    arc(ax, 2, 3, "½", colour=ORANGE)
    arc(ax, 2, 4, "½", dy=0.2)
    arc(ax, 3, 1, "snake 3 → 1", colour=ORANGE, above=False, lw=3)
    ax.set_xlim(-1, 9)
    ax.set_ylim(-2.3, 3.4)
    ax.axis("off")
    ax.set_title("Toy board with a snake: land on 3 and you're back on 1. The loop is in orange.",
                 loc="left", fontsize=14, color=INK)
    save(fig, "05-toy-snake.png")


if __name__ == "__main__":
    histogram()
    toy_ladder()
    toy_cdf()
    toy_snake()
    expected_by_square()
    estimates_vs_exact()
