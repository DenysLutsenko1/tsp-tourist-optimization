"""Tests for the three TSP implementations contributed by Matsvei.
Run from repo root: python -m unittest discover -s tests -v
"""

import itertools
import tempfile
import unittest
from pathlib import Path

import numpy as np

from ant_colony import ant_colony_tsp
from branch_and_bound import branch_and_bound_tsp
from nearest_neighbor import nearest_neighbor_tsp
from tsp_common import objective_matrix, tour_score, run_experiments


def brute_force(matrix, start=0):
    cities = [i for i in range(len(matrix)) if i != start]
    tours = ([start, *perm, start] for perm in itertools.permutations(cities))
    return min(tours, key=lambda t: tour_score(t, matrix))


class MatsveiAlgorithmsTests(unittest.TestCase):
    def assert_hamiltonian_cycle(self, tour, n, start=0):
        self.assertEqual(len(tour), n + 1)
        self.assertEqual(tour[0], start)
        self.assertEqual(tour[-1], start)
        self.assertEqual(set(tour[:-1]), set(range(n)))
        self.assertEqual(len(tour[:-1]), len(set(tour[:-1])))

    def test_nearest_neighbor_explicitly_uses_distance(self):
        matrix = np.array([
            [0, 1, 2, 8],
            [8, 0, 1, 2],
            [2, 8, 0, 1],
            [1, 2, 8, 0],
        ], dtype=float)
        self.assertEqual(nearest_neighbor_tsp(distances=matrix), [0, 1, 2, 3, 0])
        self.assertEqual(nearest_neighbor_tsp(start_city=2, distances=matrix), [2, 3, 0, 1, 2])

    def test_branch_and_bound_exact_on_random_asymmetric_instances(self):
        rng = np.random.default_rng(7)
        for n in range(2, 8):
            for trial in range(8):
                matrix = rng.integers(1, 100, size=(n, n)).astype(float)
                np.fill_diagonal(matrix, 0)
                for start in (0, n - 1):
                    with self.subTest(n=n, trial=trial, start=start):
                        obtained = branch_and_bound_tsp(start_city=start, weights=matrix)
                        correct = brute_force(matrix, start)
                        self.assert_hamiltonian_cycle(obtained, n, start)
                        self.assertAlmostEqual(tour_score(obtained, matrix),
                                               tour_score(correct, matrix), places=7)

    def test_aco_reproducible_and_valid_for_asymmetric_matrix(self):
        matrix = np.array([
            [0, 3, 8, 5], [6, 0, 2, 7],
            [3, 6, 0, 1], [2, 4, 5, 0],
        ], dtype=float)
        kwargs = dict(start_city=1, weights=matrix, num_ants=12,
                      iterations=20, seed=123)
        a = ant_colony_tsp(**kwargs)
        b = ant_colony_tsp(**kwargs)
        self.assertEqual(a, b)
        self.assert_hamiltonian_cycle(a, 4, 1)

    def test_article_data_three_algorithms_and_exact_optimum(self):
        matrix = objective_matrix()
        routes = [
            nearest_neighbor_tsp(),
            branch_and_bound_tsp(),
            ant_colony_tsp(num_ants=20, iterations=50, seed=40),
        ]
        for route in routes:
            self.assert_hamiltonian_cycle(route, 8, 0)
        exhaustive_best = brute_force(matrix)
        self.assertAlmostEqual(tour_score(routes[1], matrix),
                               tour_score(exhaustive_best, matrix), places=7)
        self.assertAlmostEqual(tour_score(routes[1], matrix), 4109.253, places=3)
        self.assertGreaterEqual(tour_score(routes[0], matrix),
                                tour_score(routes[1], matrix) - 1e-9)
        self.assertGreaterEqual(tour_score(routes[2], matrix),
                                tour_score(routes[1], matrix) - 1e-9)

    def test_csv_upsert_keeps_other_algorithm_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            csv_path = Path(folder) / "algorithm_results.csv"
            run_experiments("Nearest Neighborhood algorithm", nearest_neighbor_tsp,
                            runs=2, csv_file=csv_path)
            run_experiments("Branch & bound Algorithm", branch_and_bound_tsp,
                            runs=2, csv_file=csv_path)
            run_experiments("Nearest Neighborhood algorithm", nearest_neighbor_tsp,
                            runs=2, csv_file=csv_path)
            csv_text = csv_path.read_text(encoding="utf-8")
            self.assertEqual(csv_text.count("Nearest Neighborhood algorithm"), 1)
            self.assertEqual(csv_text.count("Branch & bound Algorithm"), 1)

    def test_inputs_rejected(self):
        with self.assertRaises(ValueError):
            nearest_neighbor_tsp(distances=[[1, 2, 3]])
        with self.assertRaises(ValueError):
            branch_and_bound_tsp(weights=[[0, -1], [5, 0]])
        with self.assertRaises(ValueError):
            ant_colony_tsp(weights=np.eye(2), evaporation=1)


if __name__ == "__main__":
    unittest.main()
