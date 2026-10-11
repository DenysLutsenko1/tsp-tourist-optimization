import time
import numpy as np

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

# Number of cities and starting city
num_cities = len(distance_matrix)
start_city = 0  # Chattogram (index 0)

# PSO parameters
num_particles = 30
max_iter = 100


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


def get_swap_sequence(tour_a, tour_b):
    """Generates a swap sequence to transition from tour_a to tour_b."""
    swaps = []
    temp_tour = list(tour_a)
    # We only consider the cities between the start and end (excluding the first and last city)
    for i in range(1, num_cities - 1):
        # If the city at position i in tour_a is not the same as in tour_b, we need to swap it
        if temp_tour[i] != tour_b[i]:
            # Find the index of the city in tour_b that should be at position i
            j = temp_tour.index(tour_b[i])
            # Record the swap and perform it in temp_tour
            swaps.append((i, j))
            temp_tour[i], temp_tour[j] = temp_tour[j], temp_tour[i]
    return swaps


def apply_swaps(tour, swaps):
    """Applies a sequence of swaps to the tour (excluding the start/end city)."""
    new_tour = list(tour)
    for p1, p2 in swaps:
        # Keep the start/end city fixed at index 0 and the last index
        if 0 < p1 < num_cities - 1 and 0 < p2 < num_cities - 1:
            new_tour[p1], new_tour[p2] = new_tour[p2], new_tour[p1]
    return new_tour


def particle_swarm_tsp(start_city=0):
    """Particle Swarm Optimization (PSO) algorithm for TSP."""
    # Initialization of particles, local bests, and global best
    particles = []
    local_best_particles = []
    local_best_scores = []
    # Includes velocity (motion pairs)
    velocities = []

    global_best_tour = None
    global_best_score = float("inf")

    # Initialization of particles
    for i in range(num_particles):
        other_cities = list(range(1, num_cities))
        # full random shuffle of the cities (excluding the starting city)
        np.random.shuffle(other_cities)
        # The tour must start and end at start_city
        p_i = [start_city] + other_cities + [start_city]
        particles.append(p_i)

        # local best is initially the particle itself in initialization
        local_best_particles.append(list(p_i))
        d, t, c = calculate_metrics(p_i)
        score_i = w1 * d + w2 * t + w3 * c
        local_best_scores.append(score_i)

        # take the best of all particles as the global best
        if score_i < global_best_score:
            global_best_score = score_i
            global_best_tour = list(p_i)

        velocities.append([])

    # Main optimization loop
    t_iter = 0
    while t_iter < max_iter:
        t_iter += 1
        for i in range(num_particles):
            # Update velocity using swap sequences towards local and global bests
            swaps_local = get_swap_sequence(particles[i], local_best_particles[i])
            swaps_global = get_swap_sequence(particles[i], global_best_tour)

            # determine the number of swaps to apply from local and global bests (50% of each)
            r1_len = int(len(swaps_local) * 0.5)
            if len(swaps_local) > 0 and r1_len == 0:
                r1_len = 1

            r2_len = int(len(swaps_global) * 0.5)
            if len(swaps_global) > 0 and r2_len == 0:
                r2_len = 1

            velocities[i] = swaps_local[:r1_len] + swaps_global[:r2_len]

            # Apply velocity to generate a new tour
            particles[i] = apply_swaps(particles[i], velocities[i])

            # Random mutation to maintain exploration
            # this mutation is applied with a 20% probability, swapping two random cities in the tour 
            # (excluding the start/end city) becauuse we dont want stay in a local optimum

            if np.random.rand() < 0.2:
                # generate two random indices for cities to swap (excluding the first and last city)
                idx1, idx2 = np.random.choice(range(1, num_cities - 1), 2, replace=False)
                # swap the cities in the particle's tour
                particles[i][idx1], particles[i][idx2] = particles[i][idx2], particles[i][idx1]

            # Evaluate new position
            d, t, c = calculate_metrics(particles[i])
            current_score = w1 * d + w2 * t + w3 * c

            # Update local best
            if current_score < local_best_scores[i]:
                local_best_scores[i] = current_score
                local_best_particles[i] = list(particles[i])

                # Update global best
                if current_score < global_best_score:
                    global_best_score = current_score
                    global_best_tour = list(particles[i])

    return global_best_tour


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
    current_tour = particle_swarm_tsp(start_city=0)

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
print("PARTICLE SWARM OPTIMIZATION RESULTS (10 runs)")
print(f"Mean execution time: {mean_execution_time:.6f} seconds")
print(f"Best multi-objective score: {best_score:.4f}")
print("Best tour (indices):", " -> ".join(map(str, best_tour)))
print("Best tour (city names):", " -> ".join([city_names[i] for i in best_tour]))
print(f"Distance: {best_metrics[0]} km")
print(f"Time: {best_metrics[1]} min")
print(f"Cost: {best_metrics[2]} BDT")