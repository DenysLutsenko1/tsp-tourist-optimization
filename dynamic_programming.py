from tests.ivan_algorithm_experiment import run_algorithm_experiment
from tsp_common import check_matrix, check_start, objective_matrix


def dynamic_programming_tsp(start_city=0, weights=None):
    """Return a minimum-weight directed TSP tour using Held-Karp DP.

    `weights`: optional square matrix of directed edge costs. If omitted, use
    the project's weighted distance, time, and fuel-cost objective.
    """
    matrix = check_matrix(objective_matrix() if weights is None else weights)
    n = len(matrix)
    check_start(start_city, n)
    if n == 1:
        return [start_city, start_city]

    cities = [city for city in range(n) if city != start_city]
    city_bits = {city: 1 << index for index, city in enumerate(cities)}
    costs = {}
    paths = {}

    for city in cities:
        state = city_bits[city]
        costs[(state, city)] = float(matrix[start_city, city])
        paths[(state, city)] = [start_city, city]

    for subset_size in range(2, n):
        for subset in range(1 << len(cities)):
            if subset.bit_count() != subset_size:
                continue
            for last_city in cities:
                last_bit = city_bits[last_city]
                if not subset & last_bit:
                    continue
                previous_subset = subset ^ last_bit
                candidates = [
                    previous_city
                    for previous_city in cities
                    if previous_subset & city_bits[previous_city]
                ]
                best_state = min(
                    candidates,
                    key=lambda previous_city: (
                        costs[(previous_subset, previous_city)]
                        + float(matrix[previous_city, last_city]),
                        previous_city,
                    ),
                )
                costs[(subset, last_city)] = (
                    costs[(previous_subset, best_state)]
                    + float(matrix[best_state, last_city])
                )
                paths[(subset, last_city)] = (
                    paths[(previous_subset, best_state)] + [last_city]
                )

    full_subset = (1 << len(cities)) - 1
    best_last_city = min(
        cities,
        key=lambda city: (
            costs[(full_subset, city)] + float(matrix[city, start_city]),
            city,
        ),
    )
    return paths[(full_subset, best_last_city)] + [start_city]


if __name__ == "__main__":
    run_algorithm_experiment("Dynamic Programming", dynamic_programming_tsp)
