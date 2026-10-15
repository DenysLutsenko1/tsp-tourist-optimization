from data import distance_matrix
from tsp_common import check_matrix, check_start, run_experiments


def nearest_neighbor_tsp(start_city=0, distances=None):
    """Return a closed city-index tour, starting/ending at start_city.

    The tour is deterministic; ties are broken by lower city index.
    Optional `distances` permits testing on a synthetic or external matrix.
    """
    matrix = check_matrix(distance_matrix if distances is None else distances)
    n = len(matrix)
    check_start(start_city, n)
    unvisited = set(range(n)) - {start_city}
    tour = [start_city]
    current = start_city

    while unvisited:
        next_city = min(unvisited, key=lambda city: (matrix[current, city], city))
        tour.append(next_city)
        unvisited.remove(next_city)
        current = next_city

    tour.append(start_city)
    return tour


if __name__ == "__main__":
    # CSV name matches the corresponding entry in results.py exactly.
    run_experiments("Nearest Neighborhood algorithm", nearest_neighbor_tsp)
