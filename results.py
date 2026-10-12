import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Set font style and size for academic presentation
plt.rcParams.update({'font.size': 10, 'font.family': 'sans-serif'})

# 1. Create directory for saving chart photos if it does not exist
output_dir = 'results_photo'
os.makedirs(output_dir, exist_ok=True)

# 2. Read data from CSV without normalization
df = pd.read_csv('algorithm_results.csv')

# Programmatically define algorithm types
stochastic_algos = [
    'Genetic Algorithm',
    'Particle Swarm Optimization',
    'Ant Colony Optimization',
    'Simulated Annealing',
]
df['Type'] = df['Algorithm'].apply(
    lambda x: 'Stochastic' if x in stochastic_algos else 'Deterministic'
)

# Strict sequence of algorithms as requested
desired_order = [
    'Greedy Algorithm',
    'Genetic Algorithm',
    'Particle Swarm Optimization',
    'Ant Colony Optimization',
    'Simulated Annealing',
    'Brute force Algorithm',
    'Branch & bound Algorithm',
    'Dynamic Programming',
    'Nearest Neighborhood algorithm',
]

# Sort the DataFrame based on the desired order of algorithms
df['Algorithm'] = pd.Categorical(
    df['Algorithm'], categories=desired_order, ordered=True
)
df = df.sort_values('Algorithm').reset_index(drop=True)

# Separate DataFrames for Stochastic and Deterministic methods
df_stoch = df[df['Type'] == 'Stochastic'].copy()
df_det = df[df['Type'] == 'Deterministic'].copy()

# Print tables to console
print('=' * 120)
print('TABLE 1: STOCHASTIC METHODS')
print('=' * 120)
print(df_stoch.to_string(index=False))

print('\n' + '=' * 120)
print('TABLE 2: DETERMINISTIC METHODS')
print('=' * 120)
print(df_det.to_string(index=False))

print('\n' + '=' * 120)
print('FINAL COMBINED TABLE (ALL ALGORITHMS)')
print('=' * 120)
print(df.to_string(index=False))
print('=' * 120)

algos = df['Algorithm'].tolist()
types = df['Type'].tolist()
# Create labels for x-axis with algorithm names and types
labels = [f'{alg}\n({t})' for alg, t in zip(algos, types)]
# Create x positions for the bars
x_pos = np.arange(len(algos))

# --- CHART 1: Overall Score ---
plt.figure(figsize=(14, 6))
scores = df['Overall Score'].tolist()
colors = ['#1f4e78' if t == 'Deterministic' else '#2ca02c' for t in types]

bars1 = plt.bar(
    x_pos,
    scores,
    color=colors,
    width=0.55,
    hatch='//',
    edgecolor='black',
    linewidth=0.8,
)
for bar, t in zip(bars1, types):
  height = bar.get_height()
  plt.annotate(
      f'{height:.3f}', # Display the score with 3 decimal places
      xy=(bar.get_x() + bar.get_width() / 2, height), # Position the annotation at the top center of the bar
      xytext=(0, 5), # Offset the annotation slightly above the bar
      textcoords='offset points',
      ha='center', # Horizontal alignment of the text
      va='bottom', # Vertical alignment of the text
      fontsize=8,
  )

# Set x-ticks with algorithm names and types, rotated for better readability
plt.xticks(x_pos, labels, rotation=25, ha='right')
# Set y-axis label and chart title with bold font weight
plt.ylabel('Optimized Value / Overall Score')
plt.title(
    '1. Multi-Objective Optimized Value (Overall Score)', fontweight='bold'
)
# Set y-axis limits with a slight offset to ensure bars are fully visible
plt.ylim(min(scores) * 0.85, max(scores) * 1.12)
# Add grid lines for better readability of the chart
plt.grid(axis='y', linestyle='--', alpha=0.5)
# Adjust layout to prevent clipping of tick-labels and ensure proper spacing
plt.tight_layout()

# Save the chart to the output directory with a descriptive filename
chart1_path = os.path.join(output_dir, 'chart_1_score.png')
plt.savefig(chart1_path, dpi=300)
print(f'[INFO] Chart 1 successfully saved to {chart1_path}')
plt.show()

# --- CHART 2: Mean Execution Time in Pure Seconds (Linear Scale with negative offset for small values) ---
plt.figure(figsize=(14, 6))
times = df['Mean Exec Time (s)'].tolist()
bar_colors = ['#1f4e78' if t == 'Deterministic' else '#2ca02c' for t in types]

bars2 = plt.bar(
    x_pos,
    times,
    color=bar_colors,
    width=0.55,
    hatch='\\\\',
    edgecolor='black',
    linewidth=0.8,
)
for bar, t in zip(bars2, types):
  height = bar.get_height()
  plt.annotate(
      f'{height:.6f}\n({t})'.rstrip('0'), # Display the time with 6 decimal places, remove trailing zeros
      xy=(bar.get_x() + bar.get_width() / 2, height),
      xytext=(0, 6),
      textcoords='offset points',
      ha='center',
      va='bottom',
      fontsize=8,
      rotation=0,
  )

plt.xticks(x_pos, labels, rotation=25, ha='right')
plt.ylabel('Mean Execution Time (seconds)')
plt.title(
    '2. Mean Execution Time Comparison (in Pure Seconds)', fontweight='bold'
)

# Linear scale with negative bottom offset so the smallest bar is clearly visible
max_t = max(times)
plt.ylim(-max_t * 0.002, max_t * 1.25)

plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

chart2_path = os.path.join(output_dir, 'chart_2_time.png')
plt.savefig(chart2_path, dpi=300)
print(f'[INFO] Chart 2 successfully saved to {chart2_path}')
plt.show()

# --- CHART 3: Distance, Time, and Cost with Dual Axes and Clear Spacing ---
fig, ax1 = plt.subplots(figsize=(16, 6))

# Define spacing and width for the grouped bars
group_spacing = 1.35
# Calculate the x positions for the bars with spacing
x_spaced = x_pos * group_spacing
# Define the width of each bar
width = 0.26

distances = df['Distance (km)'].tolist()
travel_times = df['Time (min)'].tolist()
costs = df['Cost (BDT)'].tolist()

# Left axis for Distance and Time with distinct gaps between columns
b_dist = ax1.bar(
    x_spaced - width - 0.04, # Offset the distance bars to the left of the center
    distances,
    width,
    label='Distance (km)',
    color='#2b5c8f',
    hatch='//',
    edgecolor='black',
    linewidth=0.6,
)
b_time = ax1.bar(
    x_spaced,
    travel_times,
    width,
    label='Time (min)',
    color='#404040',
    hatch='\\\\',
    edgecolor='black',
    linewidth=0.6,
)

ax1.set_ylabel('Distance (km) / Time (min)', color='black', fontweight='bold')
ax1.set_ylim(0, max(max(distances), max(travel_times)) * 1.25)

# Right axis for Cost with proper offset
ax2 = ax1.twinx()
b_cost = ax2.bar(
    x_spaced + width + 0.04,
    costs,
    width,
    label='Cost (BDT)',
    color='#a65b28',
    hatch='..',
    edgecolor='black',
    linewidth=0.6,
)
ax2.set_ylabel('Cost (BDT)', color='#a65b28', fontweight='bold')
ax2.set_ylim(0, max(costs) * 1.35)

# Annotations for all three metric columns
for bar, orig_val in zip(b_dist, distances):
  ax1.annotate(
      f'{orig_val}',
      (bar.get_x() + bar.get_width() / 2, bar.get_height()),
      xytext=(0, 3),
      textcoords='offset points',
      ha='center',
      fontsize=7,
      rotation=90,
  )
for bar, orig_val in zip(b_time, travel_times):
  ax1.annotate(
      f'{orig_val}',
      (bar.get_x() + bar.get_width() / 2, bar.get_height()),
      xytext=(0, 3),
      textcoords='offset points',
      ha='center',
      fontsize=7,
      rotation=90,
  )
for bar, orig_val in zip(b_cost, costs):
  ax2.annotate(
      f'{orig_val}',
      (bar.get_x() + bar.get_width() / 2, bar.get_height()),
      xytext=(0, 3),
      textcoords='offset points',
      ha='center',
      fontsize=7,
      rotation=90,
  )

# Combine legends from both axes
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')

plt.xticks(x_spaced, labels, rotation=20, ha='right')
plt.title(
    '3. Comparison of Distance, Time, and Cost with Dual Axes and Spacing',
    fontweight='bold',
)
ax1.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

chart3_path = os.path.join(output_dir, 'chart_3_metrics.png')
plt.savefig(chart3_path, dpi=300)
print(f'[INFO] Chart 3 successfully saved to {chart3_path}')
plt.show()