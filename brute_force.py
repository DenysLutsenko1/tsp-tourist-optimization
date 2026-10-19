import itertools

from tests.ivan_algorithm_experiment import run_algorithm_experiment
from tsp_common import check_matrix, check_start, objective_matrix


def brute_force_tsp(start_city=0, weights=None):
    """Return a minimum-weight Hamiltonian cycle by exhaustive enumeration.

    `weights`: optional square matrix of directed edge costs. If omitted, use
    the project's weighted distance, time, and fuel-cost objective.
    """
    matrix = check_matrix(objective_matrix() if weights is None else weights)
    n = len(matrix)
    check_start(start_city, n)

    if n == 1:
        return [start_city, start_city]

    other_cities = [city for city in range(n) if city != start_city]
    best_tour = None
    best_score = float("inf")

    for permutation in itertools.permutations(other_cities):
        tour = [start_city, *permutation, start_city]
        score = sum(
            float(matrix[current, next_city])
            for current, next_city in zip(tour[:-1], tour[1:])
        )
        if score < best_score - 1e-9:
            best_score = score
            best_tour = tour

    return best_tour


if __name__ == "__main__":
    run_algorithm_experiment("Brute force Algorithm", brute_force_tsp)
