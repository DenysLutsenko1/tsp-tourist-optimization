import csv
import time
from pathlib import Path

import numpy as np

from cfg import city_names, num_runs, w1, w2, w3
from data import distance_matrix, time_matrix, cost_matrix

CSV_COLUMNS = [
    "Algorithm", "Overall Score", "Distance (km)", "Time (min)",
    "Cost (BDT)", "Mean Exec Time (s)",
]


def check_matrix(matrix):
    """Return an N x N numeric, nonnegative, finite (possibly asymmetric) matrix."""
    matrix = np.asarray(matrix, dtype=float)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1] or len(matrix) == 0:
        raise ValueError("Expected a nonempty square cost matrix.")
    if not np.all(np.isfinite(matrix)) or np.any(matrix < 0):
        raise ValueError("Costs must be finite and nonnegative.")
    return matrix


def check_start(start_city, n):
    if not isinstance(start_city, (int, np.integer)) or not 0 <= start_city < n:
        raise ValueError(f"start_city must be an integer in range 0..{n - 1}")


def objective_matrix():
    """Return the weighted directed arc costs from the team's source matrices."""
    return check_matrix(w1 * distance_matrix + w2 * time_matrix + w3 * cost_matrix)


def tour_score(tour, matrix):
    """Score a complete directed Hamiltonian tour using a supplied cost matrix."""
    matrix = check_matrix(matrix)
    n = len(matrix)
    if len(tour) != n + 1 or tour[0] != tour[-1] or set(tour[:-1]) != set(range(n)):
        raise ValueError("Tour must visit every city once and return to its start.")
    return float(sum(matrix[u, v] for u, v in zip(tour[:-1], tour[1:])))


def calculate_metrics(tour):
    """Original project's distance, time and fuel cost, in their native units."""
    distances = float(sum(distance_matrix[u, v] for u, v in zip(tour[:-1], tour[1:])))
    minutes = float(sum(time_matrix[u, v] for u, v in zip(tour[:-1], tour[1:])))
    bdt = float(sum(cost_matrix[u, v] for u, v in zip(tour[:-1], tour[1:])))
    return round(distances, 2), round(minutes, 2), round(bdt, 2)


def run_experiments(algorithm_name, solver, *, stochastic=False, runs=None, csv_file="algorithm_results.csv"):
    """Run one algorithm 10 times, report the best route and upsert its CSV row.

    For stochastic methods, solver accepts seed=<integer>. The seeds are 40..49
    for 10 runs. For deterministic methods the same instance is timed repeatedly.
    CSV is updated without removing any previous algorithm's results.
    """
    runs = num_runs if runs is None else runs
    if not isinstance(runs, int) or runs < 1:
        raise ValueError("runs must be a positive integer")
    execution_times = []
    scores = []
    best_tour = None
    best_score = float("inf")
    weighted = objective_matrix()
    seeds = list(range(40, 40 + runs)) if stochastic else None

    for run in range(runs):
        begin = time.perf_counter()
        tour = solver(seed=seeds[run]) if stochastic else solver()
        seconds = time.perf_counter() - begin
        score = tour_score(tour, weighted)
        execution_times.append(seconds)
        scores.append(score)
        if score < best_score:
            best_tour = tour
            best_score = score

    distance, travel_time, cost = calculate_metrics(best_tour)
    # Preserve the team's convention: compute the score from the rounded
    # route metrics before writing the CSV (all measurements round to 2 dp).
    reported_score = w1 * distance + w2 * travel_time + w3 * cost
    mean_time = float(np.mean(execution_times))
    print(f"\n{algorithm_name.upper()} RESULTS ({runs} runs)")
    if stochastic:
        print("Random seeds:", seeds)
    print(f"Mean execution time: {mean_time:.6f} seconds")
    print(f"Best multi-objective score: {reported_score:.4f}")
    print("Best tour (indices):", " -> ".join(map(str, best_tour)))
    if len(city_names) == len(weighted):
        print("Best tour (city names):", " -> ".join(city_names[i] for i in best_tour))
    print(f"Distance: {distance} km")
    print(f"Time: {travel_time} min")
    print(f"Cost: {cost} BDT")
    print(f"Score statistics: mean={np.mean(scores):.4f}, "
          f"median={np.median(scores):.4f}, "
          f"std={np.std(scores):.4f}, "
          f"min={np.min(scores):.4f}, max={np.max(scores):.4f}")

    path = Path(csv_file)
    rows = []
    if path.exists():
        with path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != CSV_COLUMNS:
                raise ValueError("Unexpected algorithm_results.csv header; refusing to overwrite it")
            rows = [row for row in reader if row.get("Algorithm") != algorithm_name]
    rows.append({
        "Algorithm": algorithm_name,
        "Overall Score": f"{reported_score:.4f}",
        "Distance (km)": f"{distance}",
        "Time (min)": f"{travel_time}",
        "Cost (BDT)": f"{cost}",
        "Mean Exec Time (s)": f"{mean_time:.6f}",
    })
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Results for '{algorithm_name}' saved to '{path}'.")
    return best_tour, reported_score
