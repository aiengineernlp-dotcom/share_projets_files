from cProfile import label

import  matplotlib.pyplot as plt
import numpy as np
from pandas import read_csv
from sklearn.preprocessing import StandardScaler

"Chargement des donnees"
coffee = read_csv("../data/coffee_data.csv")
nearest_starbucks = coffee["nearest_starbucks"]
print("\n",coffee.info)

"Importation de StandartScaler"
scaler = StandardScaler()

# Reachape de la caracteristique age
nearest_starbucks_reshaped = np.array(nearest_starbucks).reshape(-1,1)
nearest_starbucks_scaler = scaler.fit_transform(nearest_starbucks_reshaped)

# print(nearest_starbucks_scaler)
print(np.mean(nearest_starbucks_scaler)) # moyenne
print(np.std(nearest_starbucks_scaler))  # ecart type
print(np.isclose(-1.1013412404281553e-16, 0)) # retourne True car  −1.1013412404281553×10 −16=−0.00000000000000011013412404281553

plt.figure(figsize=(8,5))
plt.hist(nearest_starbucks_scaler,bins=80,color='lightgreen',edgecolor='black')
plt.title("Distribution normaliser de 'nearest_starbucks'")
plt.xlabel("Valueurs normalisees")
plt.ylabel("Nombre de clients")
plt.axvline(0,color = 'red',linestyle = "--",label = "Moyenne (0)",)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()