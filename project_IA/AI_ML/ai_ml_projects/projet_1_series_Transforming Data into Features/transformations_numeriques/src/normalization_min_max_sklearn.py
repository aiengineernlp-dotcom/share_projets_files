import matplotlib.pyplot as plt

from pandas import read_csv
import numpy as np
from sklearn.preprocessing import MinMaxScaler
coffee = read_csv("../data/coffee_data.csv")
print(coffee.info())
nearest_starbucks = coffee["nearest_starbucks"]

# initialization du scaller
mm_scaler = MinMaxScaler()

# rechapeed de la caracteristique

nearest_starbucks_reshaped = np.array(nearest_starbucks).reshape(-1,1)
nearest_starbucks_scaler = mm_scaler.fit_transform(nearest_starbucks_reshaped)
print(nearest_starbucks_scaler)

import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))
plt.hist(nearest_starbucks_scaler, bins=80, color='skyblue', edgecolor='black')
plt.axvline(x=0, color='red', linestyle='--', label='Valeur minimale (0)')
plt.axvline(x=1, color='green', linestyle='--', label='Valeur maximale (1)')
plt.title("Normalisation Min-Max avec sklearn")
plt.xlabel("Valeurs normalisées")
plt.ylabel("Nombre d'observations (distances)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
