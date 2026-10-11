import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Set font style
plt.rcParams.update({'font.size': 10, 'font.family': 'sans-serif'})

# 1. Read data from CSV without normalization
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

df['Algorithm'] = pd.Categorical(
    df['Algorithm'], categories=desired_order, ordered=True
)
df = df.sort_values('Algorithm').reset_index(drop=True)

df_stoch = df[df['Type'] == 'Stochastic'].copy()
df_det = df[df['Type'] == 'Deterministic'].copy()

algos = df['Algorithm'].tolist()
types = df['Type'].tolist()
labels = [f'{alg}\n({t})' for alg, t in zip(algos, types)]
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
      f'{height:.3f}',
      xy=(bar.get_x() + bar.get_width() / 2, height),
      xytext=(0, 5),
      textcoords='offset points',
      ha='center',
      va='bottom',
      fontsize=8,
  )

plt.xticks(x_pos, labels, rotation=25, ha='right')
plt.ylabel('Optimized Value / Overall Score')
plt.title(
    '1. Multi-Objective Optimized Value (Overall Score)', fontweight='bold'
)
plt.ylim(min(scores) * 0.85, max(scores) * 1.12)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('chart_1_score.png', dpi=300)
plt.show()

# --- CHART 2: Mean Execution Time in Pure Seconds (With negative bottom offset) ---
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
      f'{height:.6f}\n({t})'.rstrip('0'),
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

# Опускаем нижнюю границу ниже нуля, чтобы появился зазор под маленьким столбцом
max_t = max(times)
plt.ylim(-max_t * 0.002, max_t * 1.25)

plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('chart_2_time.png', dpi=300)
plt.show()

# --- CHART 3: Distance, Time, and Cost with CLEAR SPACING between columns ---
fig, ax1 = plt.subplots(figsize=(16, 6))

group_spacing = 1.35  # Широкий отступ между группами алгоритмов
x_spaced = x_pos * group_spacing
width = 0.26  # Ширина каждой колонки

distances = df['Distance (km)'].tolist()
travel_times = df['Time (min)'].tolist()
costs = df['Cost (BDT)'].tolist()

# Четкий сдвиг для каждой колонки с зазором друг от друга:
# Левая колонка (Distance), Центральная (Time), Правая (Cost)
b_dist = ax1.bar(
    x_spaced - width - 0.04,
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

# Правая ось для Cost с отступом вправо
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

# Аннотации значений для всех трех колонок
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

# Объединение легенд
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')

plt.xticks(x_spaced, labels, rotation=20, ha='right')
plt.title(
    '3. Comparison of Distance, Time, and Cost with Clear Column Spacing',
    fontweight='bold',
)
ax1.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('chart_3_metrics.png', dpi=300)
plt.show()