import time
import numpy as np
import csv
import os

np.random.seed(40)

from cfg import (w1, w2, w3, city_names, num_runs)

# Берем данные из файла data.py
from data import (
    One_liter_benzin_BDT_coast,
    cost_matrix,
    distance_matrix,
    fuel_consumption_per_km,
    time_matrix,
)

# input: tour (list of city indices) for example: [0, 1, 2, 3, 4, 5, 6, 7, 0]
def calculate_metrics(tour):
  """A function for calculating the total distance, time, and cost of a route."""
  total_dist = 0
  total_time = 0
  total_cost = 0
  for i in range(len(tour) - 1):
    u, v = tour[i], tour[i + 1]
    total_dist += distance_matrix[u][v]
    total_time += time_matrix[u][v]
    total_cost += cost_matrix[u][v]
  return (
      round(total_dist, 2),
      round(total_time, 2),
      round(total_cost, 2),
  )

def greedy_tsp(start_city=0):
  """Greedy algorithm for TSP with multi-criteria assessment at each step."""
  n = len(distance_matrix)
  # Initialize visited cities [False, False, False, False, False, False, False, False]
  visited = [False] * n
  # start point of the tour   
  tour = [start_city]
  # Mark the starting city as visited   
  visited[start_city] = True

  # current city is the starting city   
  current = start_city
  while len(tour) < n:
    next_city = None
    min_val = float("inf")
    # проходимся по всем городам
    for j in range(n):
    #   если город еще не был посещен 
      if not visited[j]:
        # Complex evaluation of the next step based on weights
        val = (
            w1 * distance_matrix[current][j]
            + w2 * time_matrix[current][j]
            + w3 * cost_matrix[current][j]
        )
        if val < min_val:
          min_val = val
          next_city = j
    tour.append(next_city)
    visited[next_city] = True
    current = next_city

  # Return to the starting city to close the cycle
  tour.append(start_city)
  return tour


# A cycle of 10 algorithm runs to obtain execution time statistics and the best solution.
execution_times = [] # time taken for each run
best_score = float("inf") # Best multi-objective score
best_tour = None # Best tour found
best_metrics = None # Metrics for the best tour

# starting the runs
for run in range(num_runs):
  start_time = time.perf_counter()

  # Algorithm execution (the journey starts and ends in Chattogram, index 0)
  current_tour = greedy_tsp(start_city=0)
  
  end_time = time.perf_counter()
  # how many seconds it took to run the algorithm
  exec_time = end_time - start_time
  execution_times.append(exec_time)

  # Calculate metrics and the overall multi-objective indicator (score)
  d, t, c = calculate_metrics(current_tour)
  score = w1 * d + w2 * t + w3 * c

  # Remember the optimal solution
  if score < best_score:
    best_score = score
    best_tour = current_tour
    best_metrics = (d, t, c)

# Calculate the average execution time
mean_execution_time = np.mean(execution_times)

# --- Output Results ---
print("GREEDY ALGORITHM RESULTS (10 runs)")
print(f"Mean execution time: {mean_execution_time:.6f} seconds")
print(f"Best multi-objective score: {best_score:.4f}")
print("Best tour (indices):", " -> ".join(map(str, best_tour)))
print("Best tour (city names):", " -> ".join([city_names[i] for i in best_tour]))
print(f"Distance: {best_metrics[0]} km")
print(f"Time: {best_metrics[1]} min")
print(f"Cost: {best_metrics[2]} BDT")


filename = "algorithm_results.csv"
algorithm_name = "Greedy Algorithm"

# Prepare the new row data
new_row = [
    algorithm_name,
    f"{best_score:.4f}",
    f"{best_metrics[0]}",
    f"{best_metrics[1]}",
    f"{best_metrics[2]}",
    f"{mean_execution_time:.6f}",
]

header = [
    "Algorithm",
    "Overall Score",
    "Distance (km)",
    "Time (min)",
    "Cost (BDT)",
    "Mean Exec Time (s)",
]

rows = []
algorithm_found = False

# 1. Read existing file data if the file exists
if os.path.exists(filename):
    with open(filename, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        file_header = next(reader, None)
        if file_header:
            header = file_header  # Keep the existing CSV header

        for row in reader:
            if row:
                # If the algorithm is found, update its record
                if row[0] == algorithm_name:
                    rows.append(new_row)
                    algorithm_found = True
                else:
                    # Keep data for other algorithms unchanged
                    rows.append(row)

# 2. If the algorithm was not present in the file, append it to the list
if not algorithm_found:
    rows.append(new_row)

# 3. Rewrite the CSV file with updated rows
with open(filename, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)

if algorithm_found:
    print(f"\nResults for '{algorithm_name}' were successfully updated in '{filename}'.")
else:
    print(f"\nResults for '{algorithm_name}' were successfully added to '{filename}'.")