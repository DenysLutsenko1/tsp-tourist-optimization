import time
import numpy as np
import csv
import os

np.random.seed(40)

# Берем данные из файла data.py
from data import (
    One_liter_benzin_BDT_coast,
    cost_matrix,
    distance_matrix,
    fuel_consumption_per_km,
    time_matrix,
)

# Weights for multi-criteria assessment
w1 = 0.3  # Distance (km)
w2 = 0.4  # Time (min)
w3 = 0.3  # Cost (BDT)

# City names
city_names = [
    "Chattogram",
    "Bandorban",
    "Rangamati",
    "Khagrachari",
    "Sajek",
    "Cox's Bazar",
    "Teknaf",
    "Saint Martin",
]

n_cities = len(distance_matrix)


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


def genetic_algorithm_run(pop_size=50, generations=100, start_city=0):
    """Genetic algorithm following Algorithm 6 structure from the research article."""
    # Cities to permute (excluding the fixed start city)
    cities = list(range(n_cities))
    cities.remove(start_city)
    
    # Initialization: Produce a random population of solutions (chromosomes)
    population = []
    for _ in range(pop_size):
        # Randomly permute the cities to create a chromosome
        chromosome = list(np.random.permutation(cities))
        # full tour includes the start city at the beginning and end
        full_tour = [start_city] + chromosome + [start_city]
        # Calculate the multi-objective score for the chromosome
        d, t, c = calculate_metrics(full_tour)
        score = w1 * d + w2 * t + w3 * c
        population.append({'chrom': chromosome, 'score': score, 'metrics': (d, t, c)})
    
    # cicle of generations
    for _ in range(generations):
        # Select an operation randomly (crossover or mutation)
        operation = 'crossover' if np.random.rand() < 0.8 else 'mutation'

        # child or offspring chromosome placeholder
        offspring_chrom = None
        
        if operation == 'crossover':
            # Select two parents ia and ib at random
            parent_a = population[np.random.randint(0, pop_size)]['chrom']
            parent_b = population[np.random.randint(0, pop_size)]['chrom']
            
            # Produce an offspring ic = crossover (ia and ib) using Order Crossover
            # take a random segment from parent_a and fill the rest from parent_b in order
            # sort the start and end indices for the crossover segment
            # random 0 to 6
            # for example [5,2] not dublicate
            # sort them to get [2,5] this part will be taken from parent_a
            start, end = sorted(np.random.choice(len(parent_a), 2, replace=False))
            # new empty child with -1 placeholders
            child = [-1] * len(parent_a)
            # replace the segment from parent_a into the child
            child[start:end+1] = parent_a[start:end+1]

            # pointer for filling the rest of the child from parent_b
            ptr = 0
            # cycle through parent_b and fill in the child where there are -1 placeholders
            for city in parent_b:
                if city not in child:
                    # find the next available position in child
                    while child[ptr] != -1:
                        ptr += 1
                    child[ptr] = city
            # full child with start and end city
            offspring_chrom = child
            
        else:  # mutation
            # Randomly select one chromosome and produce an offspring ic = mutate(i) (Swap mutation)
            target_ind = population[np.random.randint(0, pop_size)]['chrom']
            offspring_chrom = target_ind.copy()
            # Randomly select two indices to swap
            idx1, idx2 = np.random.choice(len(offspring_chrom), 2, replace=False)
            # Swap the cities at idx1 and idx2
            offspring_chrom[idx1], offspring_chrom[idx2] = offspring_chrom[idx2], offspring_chrom[idx1]

        # Local search (ic)
        
        # The fitness of the offspring ic is calculated
        full_offspring_tour = [start_city] + offspring_chrom + [start_city]
        off_d, off_t, off_c = calculate_metrics(full_offspring_tour)
        off_score = w1 * off_d + w2 * off_t + w3 * off_c
        
        # Sort population by score (ascending for minimization)
        population.sort(key=lambda x: x['score'])
        
        # If ic is better, then replace the worst chromosome with ic
        if off_score < population[-1]['score']:
            population[-1] = {
                'chrom': offspring_chrom, 
                'score': off_score, 
                'metrics': (off_d, off_t, off_c)
            }

    # Return the fittest individual to P
    population.sort(key=lambda x: x['score'])
    best_ind = population[0]
    best_tour = [start_city] + best_ind['chrom'] + [start_city]
    
    return best_tour, best_ind['score'], best_ind['metrics']


# A cycle of 10 algorithm runs to obtain execution time statistics and the best solution.
num_runs = 10  # Number of runs
execution_times = []  # time taken for each run
best_score = float("inf")  # Best multi-objective score
best_tour = None  # Best tour found
best_metrics = None  # Metrics for the best tour

# starting the runs
for run in range(num_runs):
    start_time = time.perf_counter()

    # Algorithm execution (the journey starts and ends in Chattogram, index 0)
    current_tour, score, metrics = genetic_algorithm_run(start_city=0)
    
    end_time = time.perf_counter()
    # how many seconds it took to run the algorithm
    exec_time = end_time - start_time
    execution_times.append(exec_time)

    # Remember the optimal solution
    if score < best_score:
        best_score = score
        best_tour = current_tour
        best_metrics = metrics

# Calculate the average execution time
mean_execution_time = np.mean(execution_times)

# --- Output Results ---
print("GENETIC ALGORITHM RESULTS (10 runs)")
print(f"Mean execution time: {mean_execution_time:.6f} seconds")
print(f"Best multi-objective score: {best_score:.4f}")
print("Best tour (indices):", " -> ".join(map(str, best_tour)))
print("Best tour (city names):", " -> ".join([city_names[i] for i in best_tour]))
print(f"Distance: {best_metrics[0]} km")
print(f"Time: {best_metrics[1]} min")
print(f"Cost: {best_metrics[2]} BDT")





# --- Save or Update Results in CSV File ---
filename = "algorithm_results.csv"
algorithm_name = "Genetic Algorithm"

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