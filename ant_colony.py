import numpy as np

from tsp_common import check_matrix, check_start, objective_matrix, run_experiments


# Explicit hyperparameters for reproducibility; edit these to tune the method.
ACO_NUM_ANTS = 30
ACO_ITERATIONS = 100
ACO_ALPHA = 1.0
ACO_BETA = 3.0
ACO_EVAPORATION = 0.5
ACO_Q = 100.0


def ant_colony_tsp(start_city=0, weights=None, *, num_ants=ACO_NUM_ANTS,
                   iterations=ACO_ITERATIONS, alpha=ACO_ALPHA,
                   beta=ACO_BETA, evaporation=ACO_EVAPORATION,
                   q=ACO_Q, seed=40):
    """Return best discovered directed TSP tour after the specified iterations.

    Optional `weights` is a directed positive-cost matrix; zero-cost edges are
    allowed. Uses a private NumPy RNG, so runs with the same seed reproduce.
    """
    w = check_matrix(objective_matrix() if weights is None else weights)
    n = len(w)
    check_start(start_city, n)
    if not isinstance(num_ants, int) or num_ants < 1:
        raise ValueError("num_ants must be a positive integer")
    if not isinstance(iterations, int) or iterations < 1:
        raise ValueError("iterations must be a positive integer")
    if alpha < 0 or beta < 0 or not 0 <= evaporation < 1 or q <= 0:
        raise ValueError("alpha, beta >= 0; evaporation in [0, 1); q > 0")
    if n == 1:
        return [start_city, start_city]

    rng = np.random.default_rng(seed)
    # Ant System on a directed graph: tau[i,j] need not equal tau[j,i].
    pheromone = np.ones((n, n), dtype=float)
    # 1/0 distances must not create infinities. Mark the diagonal unavailable.
    heuristic = 1.0 / np.maximum(w, 1e-12)
    np.fill_diagonal(heuristic, 0.0)
    best_score = float("inf")
    best_tour = None

    for _ in range(iterations):
        tours = []
        for _ant in range(num_ants):
            current = start_city
            tour = [start_city]
            unvisited = set(range(n)) - {start_city}
            while unvisited:
                candidates = sorted(unvisited)
                desirability = (pheromone[current, candidates] ** alpha
                                * heuristic[current, candidates] ** beta)
                total = float(np.sum(desirability))
                if not np.isfinite(total) or total <= 0:
                    # Numerical fallback: equal probability for remaining cities.
                    next_city = int(rng.choice(candidates))
                else:
                    next_city = int(rng.choice(candidates, p=desirability / total))
                tour.append(next_city)
                unvisited.remove(next_city)
                current = next_city
            tour.append(start_city)
            score = float(sum(w[u, v] for u, v in zip(tour[:-1], tour[1:])))
            tours.append((tour, score))
            if score < best_score:
                best_score = score
                best_tour = tour[:]

        pheromone *= (1.0 - evaporation)
        for tour, score in tours:
            deposit = q / max(score, 1e-12)
            for u, v in zip(tour[:-1], tour[1:]):
                pheromone[u, v] += deposit
        # Keep pheromone strictly positive and finite over long runs.
        np.clip(pheromone, 1e-12, 1e12, out=pheromone)

    return best_tour


if __name__ == "__main__":
    run_experiments("Ant Colony Optimization", ant_colony_tsp, stochastic=True)
