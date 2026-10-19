import math

import numpy as np

from tests.ivan_algorithm_experiment import run_algorithm_experiment
from tsp_common import check_matrix, check_start, objective_matrix


SA_INITIAL_TEMPERATURE = 1000.0
SA_COOLING_RATE = 0.995
SA_ITERATIONS = 5000


def simulated_annealing_tsp(
    start_city=0,
    weights=None,
    *,
    initial_temperature=SA_INITIAL_TEMPERATURE,
    cooling_rate=SA_COOLING_RATE,
    iterations=SA_ITERATIONS,
    seed=40,
):
    """Return the best directed TSP tour found by simulated annealing.

    `weights`: optional square matrix of directed edge costs. If omitted, use
    the project's weighted distance, time, and fuel-cost objective.
    """
    matrix = check_matrix(objective_matrix() if weights is None else weights)
    n = len(matrix)
    check_start(start_city, n)

    if initial_temperature <= 0:
        raise ValueError("initial_temperature must be positive")
    if not 0 < cooling_rate < 1:
        raise ValueError("cooling_rate must be between 0 and 1")
    if not isinstance(iterations, (int, np.integer)) or iterations < 1:
        raise ValueError("iterations must be a positive integer")

    if n == 1:
        return [start_city, start_city]

    rng = np.random.default_rng(seed)
    cities = [city for city in range(n) if city != start_city]
    current = [int(city) for city in rng.permutation(cities)]

    def score(permutation):
        tour = [start_city, *permutation, start_city]
        return float(sum(matrix[u, v] for u, v in zip(tour[:-1], tour[1:])))

    current_score = score(current)
    best = current[:]
    best_score = current_score
    temperature = float(initial_temperature)

    for _ in range(int(iterations)):
        candidate = current[:]
        first, second = rng.choice(len(candidate), size=2, replace=False)
        candidate[first], candidate[second] = candidate[second], candidate[first]
        candidate_score = score(candidate)
        difference = candidate_score - current_score

        if difference < 0 or rng.random() < math.exp(-difference / temperature):
            current = candidate
            current_score = candidate_score
            if current_score < best_score:
                best = current[:]
                best_score = current_score

        temperature = max(temperature * cooling_rate, 1e-12)

    return [start_city, *best, start_city]


if __name__ == "__main__":
    run_algorithm_experiment(
        "Simulated Annealing",
        simulated_annealing_tsp,
        stochastic=True,
    )
