import numpy as np

# Chattogram  Bandorban  Rangamati  Khagrachari  Sajek  Cox's Bazar  Teknaf  Saint Martin

One_liter_benzin_BDT_coast = 166
fuel_consumption_per_km = 0.08


distance_matrix = np.array([
  [0,  73,  63, 105, 170, 144, 217, 229], # Chattogram +
  [73,   0,  72.6,  133,  199, 116, 194, 211], # Bandorban +
  [63,  72.6,   0, 68.1, 134, 208, 281, 285], # Rangamati +
  [105,  133, 68.1,   0,  65.9, 250, 323, 333], # Khagrachari +
  [170,  199, 134,  65.9,   0, 315, 388, 397], # Sajek +
  [146, 116, 210, 252, 315,   0,  81.5, 108], # Cox's Bazar +
  [219, 189, 271, 325, 390,  81.5,   0,  32.3], # Teknaf +
  [229, 211, 285, 333, 397, 108,  50,   0]  # Saint Martin
])

time_matrix = np.array([
  [0,  118,  104, 161, 297, 201, 313, 330], # Chattogram 
  [118,   0,  141,  239,  375, 154, 268, 291], # Bandorban
  [97,  141,   0, 108, 242, 272, 384, 390], # Rangamati
  [156,  253, 108,   0,  134, 326, 438, 452], # Khagrachari
  [304,  388, 244,  134,   0, 484, 584, 598], # Sajek
  [187, 151, 276, 352, 484,   0,  116, 154], # Cox's Bazar
  [290, 256, 392, 447, 583,  116,   0,  46], # Teknaf
  [330, 291, 390, 452, 598, 154,  46,   0]  # Saint Martin
])

cost_per_km = np.round(One_liter_benzin_BDT_coast * fuel_consumption_per_km, 2)

# Obtaining the final expenditure matrix in BDT
cost_matrix = np.round(distance_matrix * cost_per_km, 2)

# print("Cost per km:", cost_per_km, "BDT")
# print("\nExpenditure matrix (in BDT):\n", cost_matrix)