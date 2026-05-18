import matplotlib.pyplot  as plt
#charger les donnees
import pandas as pd
import numpy as np

from pandas import read_csv

coffee  = read_csv("../data/coffee_data.csv")
print(coffee.info)
nearest_starbucks = coffee["nearest_starbucks"]

# application de la normalization min-max
nearest_starbucks_min = np.min(nearest_starbucks)
nearest_starbucks_max = np.max(nearest_starbucks)
Z_norm = ((nearest_starbucks-nearest_starbucks_min)/(nearest_starbucks_max-nearest_starbucks_min))
print("Le resulatat de cette normalizatrion Min - Max  est:\n",Z_norm)


plt.figure(figsize=(8,5))
plt.hist(Z_norm, bins=80, color='skyblue', edgecolor='black')
plt.title("Normalization Min-Max")
plt.xlabel("Valeurs normalisées (entre 0 et 1)")
plt.ylabel("Fréquence")
plt.axvline(np.mean(Z_norm), color="red", linestyle="--", label=f"Moyenne ({np.mean(Z_norm):.2f})")
plt.legend()
plt.grid(True)
plt.show()
