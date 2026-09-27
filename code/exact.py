"""The exact expected number of rolls, via an absorbing Markov chain.

Solves (I - Q) e = 1, where Q is the transition matrix between unfinished squares.
e[i] is the expected number of rolls to finish from square i.
"""

import numpy as np

from simulate import LADDERS, SNAKES

N_STATES = 101  # squares 0-99, plus 100 = "finished" (100 or more)
FINISH = 100


def transition_matrix() -> np.ndarray:
    """T = D @ J: roll the die, then slide or climb."""
    D = np.zeros((N_STATES, N_STATES))  # dice: where one roll takes you
    for i in range(FINISH):
        for roll in range(1, 7):
            D[i, min(i + roll, FINISH)] += 1 / 6
    D[FINISH, FINISH] = 1  # once finished, you stay finished

    J = np.eye(N_STATES)  # jumps: stay put, unless on a snake or ladder
    for start, end in {**SNAKES, **LADDERS}.items():
        J[start] = 0
        J[start, end] = 1

    return D @ J


def expected_rolls() -> np.ndarray:
    Q = transition_matrix()[:FINISH, :FINISH]  # drop the finish row and column
    return np.linalg.solve(np.eye(FINISH) - Q, np.ones(FINISH))


def finished_by_roll(max_rolls: int = 1000) -> np.ndarray:
    """Share of games finished by each roll: pour the sand forward."""
    T = transition_matrix()
    sand = np.zeros(N_STATES)
    sand[0] = 1
    cdf = []
    for _ in range(max_rolls):
        sand = sand @ T
        cdf.append(sand[FINISH])
    return np.array(cdf)


if __name__ == "__main__":
    e = expected_rolls()
    print(f"Expected rolls from the start: {e[0]:.4f}")
    cdf = finished_by_roll()
    for p in (0.5, 0.9, 0.99):
        print(f"{p:.0%} of games finished by roll {np.argmax(cdf >= p) + 1}")
