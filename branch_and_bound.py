from tsp_common import check_matrix, check_start, objective_matrix, run_experiments


def branch_and_bound_tsp(start_city=0, weights=None):
    """Return a provably minimum-weight Hamiltonian cycle.

    `weights`: optional square matrix of directed edge costs. If omitted, use
    0.3*distance + 0.4*time + 0.3*cost, with coefficients from cfg.py.
    """
    w = check_matrix(objective_matrix() if weights is None else weights)
    n = len(w)
    check_start(start_city, n)
    if n == 1:
        return [start_city, start_city]

    # Feasible initial upper bound: weighted nearest-neighbor tour.
    remaining = set(range(n)) - {start_city}
    best_tour = [start_city]
    current = start_city
    while remaining:
        city = min(remaining, key=lambda j: (w[current, j], j))
        best_tour.append(city)
        remaining.remove(city)
        current = city
    best_tour.append(start_city)
    best_score = sum(float(w[u, v]) for u, v in zip(best_tour[:-1], best_tour[1:]))

    def completion_lower_bound(current_city, unvisited):
        """Admissible bound: max(relaxed min-outgoing, min-incoming).

        Each not-yet-used city needs exactly one outgoing and incoming edge.
        Ignoring collisions/subtours gives an optimistic (never too high) bound.
        The last return edge is included in both relaxations.
        """
        if not unvisited:
            return float(w[current_city, start_city])

        # Current city must connect to an unvisited city; remaining cities
        # must connect to another remaining city or the fixed starting city.
        out_lb = min(float(w[current_city, j]) for j in unvisited)
        for u in unvisited:
            destinations = (unvisited - {u}) | {start_city}
            out_lb += min(float(w[u, v]) for v in destinations)

        # Each unvisited city needs an incoming edge from the current or
        # another unvisited city; the start needs an incoming from remaining.
        in_lb = min(float(w[u, start_city]) for u in unvisited)
        for v in unvisited:
            in_lb += min(float(w[u, v]) for u in (current_city, *unvisited) if u != v)
        return max(in_lb, out_lb)

    def search(current_city, path, remaining_cities, partial_score):
        nonlocal best_tour, best_score
        if not remaining_cities:
            total = partial_score + float(w[current_city, start_city])
            if total < best_score - 1e-9:
                best_score = total
                best_tour = path + [start_city]
            return

        if partial_score + completion_lower_bound(current_city, remaining_cities) >= best_score - 1e-9:
            return

        # Explore promising subtrees first to find a low upper bound early.
        for city in sorted(remaining_cities, key=lambda j: (w[current_city, j], j)):
            new_score = partial_score + float(w[current_city, city])
            if new_score >= best_score - 1e-9:
                continue
            search(city, path + [city], remaining_cities - {city}, new_score)

    search(start_city, [start_city], frozenset(range(n)) - {start_city}, 0.0)
    return best_tour


if __name__ == "__main__":
    run_experiments("Branch & bound Algorithm", branch_and_bound_tsp)
