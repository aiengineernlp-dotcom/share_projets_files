import pandas as pd
import  numpy as np
from pandas import read_csv
import matplotlib.pyplot as plt
coffee = read_csv("../data/coffee_data.csv")
print("\n",coffee.info)
starbucks_clients_age = coffee['age']
print(coffee)

# Calcul de la moyenne arithmetique
starbucks_clients_age_mean = np.mean(starbucks_clients_age)

print("la moyenne est : ",starbucks_clients_age_mean )

# Centrering des donnees
centered_mean  = starbucks_clients_age - starbucks_clients_age_mean
print("le centrage est : ", centered_mean)

#Tracer de l'histogramme des starbucks_dist centrer

plt.title("CALCUL DU CENTRERING")
plt.xlabel("Axe des abssices (distance par rapport a la moyenne)  ")  # L’axe X (abscisses) : ce sont les valeurs centrées (par exemple : la distance centrée ou l’âge centré)
plt.ylabel("Axe des ordonnees (ages des clients)") # L’axe Y (ordonnées) : ce n’est pas l’âge, c’est le nombre d’occurrences (combien de fois une valeur centrée est dans chaque intervalle)
# Donc si y s’arrête à 25, ça signifie qu’il y a au maximum 25 clients dans une des barres de ton histogramme (un "bin").
#✅ Si tu veux que y montre les âges eux-mêmes Tu ne dois pas utiliser un histogramme, mais plutôt un nuage de points (scatter) ou une courbe.
plt.hist(centered_mean, bins=80, color = 'g',edgecolor='black')
plt.axvline(0, color='red', linestyle='dashdot', label='Moyenne (0)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

