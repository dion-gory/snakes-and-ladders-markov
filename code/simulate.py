"""How many dice rolls does a game of Snakes and Ladders take?

Brute force: play the game many times and average the result.
Board transcribed from snakes-and-ladders/graphics/board.png.

Writes one row per game to data/rolls_<n>.csv so the raw vectors can be
re-read later for histograms, and a combined data/summary.csv.
"""

import csv
import random
import statistics
from pathlib import Path

# Snake head -> tail. Land on the key, slide down to the value.
SNAKES = {
    16: 7,
    59: 17,
    63: 19,
    67: 30,
    87: 24,
    93: 69,
    95: 75,
    99: 77,
}

# Ladder foot -> top. Land on the key, climb up to the value.
LADDERS = {
    9: 27,
    18: 37,
    25: 54,
    28: 51,
    56: 64,
    68: 88,
    76: 97,
    79: 100,
}

TRIALS = (1_000, 10_000, 100_000)
SEED = 12345
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def roll_dice() -> int:
    return random.randint(1, 6)


def play_game() -> int:
    """Play one game. Return the number of rolls it took."""
    position = 0
    rolls = 0

    while True:
        position += roll_dice()
        rolls += 1

        if position in SNAKES:
            position = SNAKES[position]
        elif position in LADDERS:
            position = LADDERS[position]

        if position >= 100:
            return rolls


def write_rolls(games: int, results: list[int]) -> Path:
    path = DATA_DIR / f"rolls_{games}.csv"
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rolls"])
        writer.writerows([r] for r in results)
    return path


def main() -> None:
    random.seed(SEED)
    DATA_DIR.mkdir(exist_ok=True)
    summary = []

    for games in TRIALS:
        results = [play_game() for _ in range(games)]
        path = write_rolls(games, results)

        summary.append(
            {
                "games": games,
                "average": round(statistics.mean(results), 3),
                "median": statistics.median(results),
                "min": min(results),
                "max": max(results),
            }
        )
        print(f"{games:>7,} games -> {path.name}")

    with (DATA_DIR / "summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary[0].keys())
        writer.writeheader()
        writer.writerows(summary)

    print()
    print(f"{'games':>8} {'average':>8} {'median':>7} {'min':>5} {'max':>5}")
    for row in summary:
        print(
            f"{row['games']:>8,} {row['average']:>8.2f} "
            f"{row['median']:>7} {row['min']:>5} {row['max']:>5}"
        )


if __name__ == "__main__":
    main()
