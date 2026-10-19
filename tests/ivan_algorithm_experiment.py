import csv
import os
import time

import numpy as np

from cfg import city_names, num_runs, w1, w2, w3
from data import cost_matrix, distance_matrix, time_matrix
from tsp_common import objective_matrix, tour_score


CSV_HEADER = [
    "Algorithm",
    "Overall Score",
    "Distance (km)",
    "Time (min)",
    "Cost (BDT)",
    "Mean Exec Time (s)",
]

STOCHASTIC_HEADER = [
    "Algorithm",
    "Mean",
    "Median",
    "Std Dev",
    "Min",
    "Max",
    "Success Rate",
    "Mean Exec Time (s)",
]


def _metrics(tour):
    distance = sum(
        distance_matrix[u, v] for u, v in zip(tour[:-1], tour[1:])
    )
    travel_time = sum(time_matrix[u, v] for u, v in zip(tour[:-1], tour[1:]))
    cost = sum(cost_matrix[u, v] for u, v in zip(tour[:-1], tour[1:]))
    return round(float(distance), 2), round(float(travel_time), 2), round(float(cost), 2)


def _upsert_row(filename, header, row):
    rows = []
    if os.path.exists(filename):
        with open(filename, newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            existing_header = next(reader, None)
            if existing_header:
                header = existing_header
            rows = [existing_row for existing_row in reader
                    if existing_row and existing_row[0] != row[0]]
    rows.append(row)
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def run_algorithm_experiment(algorithm_name, solver, *, stochastic=False):
    """
    The best run is written to results/algorithm_results.csv and aggregate
    statistics for all runs are written to results/stochastic.csv.
    """
    weighted = objective_matrix()
    execution_times = []
    scores = []
    best_tour = None
    best_score = float("inf")

    for run in range(num_runs):
        seed = 40 + run
        begin = time.perf_counter()
        tour = solver(seed=seed) if stochastic else solver()
        execution_times.append(time.perf_counter() - begin)
        score = tour_score(tour, weighted)
        scores.append(score)
        if score < best_score:
            best_score = score
            best_tour = tour

    distance, travel_time, cost = _metrics(best_tour)
    mean_time = float(np.mean(execution_times))
    reported_score = w1 * distance + w2 * travel_time + w3 * cost
    os.makedirs("results", exist_ok=True)

    _upsert_row(
        "results/algorithm_results.csv",
        CSV_HEADER,
        [
            algorithm_name,
            f"{reported_score:.4f}",
            f"{distance}",
            f"{travel_time}",
            f"{cost}",
            f"{mean_time:.6f}",
        ],
    )

    rounded_best = round(min(scores), 4)
    success_count = sum(round(score, 4) == rounded_best for score in scores)
    _upsert_row(
        "results/stochastic.csv",
        STOCHASTIC_HEADER,
        [
            algorithm_name,
            f"{np.mean(scores):.4f}",
            f"{np.median(scores):.4f}",
            f"{np.std(scores):.4f}",
            f"{np.min(scores):.4f}",
            f"{np.max(scores):.4f}",
            f"{success_count / num_runs * 100:.2f}%",
            f"{mean_time:.6f}",
        ],
    )

    print(f"{algorithm_name} results saved to results/algorithm_results.csv")
    print("Best tour (indices):", " -> ".join(map(str, best_tour)))
    if len(city_names) == len(best_tour) - 1:
        print("Best tour (city names):", " -> ".join(city_names[i] for i in best_tour))
    print(f"Best multi-objective score: {reported_score:.4f}")
    print(f"Mean execution time: {mean_time:.6f} seconds")
    return best_tour, reported_score
