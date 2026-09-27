# How long does a game of snakes and ladders last?

Code for the article [How long does a game of snakes and ladders last?](https://medium.com/@diongory/how-long-does-a-game-of-snakes-and-ladders-last-db012ee9480a): a Monte Carlo simulation of one board, then the exact answer
from an absorbing Markov chain.

| | Average rolls |
|---|---|
| Monte Carlo, 1,000 games | 38.65 |
| Monte Carlo, 10,000 games | 37.57 |
| Monte Carlo, 100,000 games | 37.92 |
| **Exact (Markov chain)** | **37.9003** |

Rules: one player, start off the board on square 0, six-sided die, reaching 100 or more
finishes (no exact landing). The board layout is in `code/simulate.py`.

```bash
pip install -r requirements.txt
cd code
python simulate.py      # writes data/rolls_*.csv and data/summary.csv
python exact.py         # expected rolls from the start, and percentiles
python make_figures.py  # renders graphics/*.png
```

- `simulate.py`: plays the game many times and averages the rolls.
- `exact.py`: builds the 101×101 transition matrix T = D @ J and solves (I − Q) e = 1.
- `make_figures.py`: the charts and diagrams used in the article.
