import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from main_16_july import X_future

# 1. Chargement des données
honey_data = pd.read_csv('data/honeyproduction.csv')
honey_df = pd.DataFrame(honey_data)

# 2. Affichage des premières lignes pour comprendre la structure
print("📊 Structure du DataFrame :\n", honey_df.head())

# 3. Groupement par année
grouped_by_year = honey_df.groupby('year')

# 4. Moyenne de la production totale par an
print("\n📈 Moyenne de la production de miel par an :")
mean_prod_per_year = grouped_by_year['totalprod'].mean().reset_index()
# Trier par année si nécessaire
mean_prod_per_year = mean_prod_per_year.sort_values('year')

print(mean_prod_per_year)

# 5. Somme de la production totale par an
print("\n📊 Somme de la production de miel par an :")
sum_prod_per_year = grouped_by_year['totalprod'].sum().reset_index()
# Trier par année si nécessaire
sum_prod_per_year = sum_prod_per_year.sort_values('year')

print(sum_prod_per_year)



#------------>>>>3 Create a variable called X  (l' annee) that is the column of years in this prod_per_year DataFrame.
""" Preparation de la variable independante X en la mettant sous forme de matrice 2D – c’est obligatoire pour les modèles scikit-learn"""

X = mean_prod_per_year['year']
X = X.values.reshape(-1,1)

#------------>>>>4 Create a variable called y that is the totalprod column in the prod_per_year dataset.
"""Preparation de la variable DEPENDANTE y (La production de mielle par annee)"""
y = mean_prod_per_year['totalprod']

#------------>>>>5
plt.figure(figsize=(8, 5))
plt.scatter(X, y, color='orange', label='Données réelles')
plt.title('Production moyenne de miel par année')
plt.xlabel('Année')
plt.ylabel('Production moyenne (totalprod)')
plt.grid(True)
plt.legend()
plt.show()


print("\n\n")



"""Create and Fit a Linear Regression Model"""
#------------>>>>6
'''1- Creation du model model'''

regr = LinearRegression()

#------------>>>>7
'''2- entrainement de mon model avec mes donnees: X (variables independante --> (l'Annee)) et y (variable dependante---->(production moyenne)) '''
regr.fit(X,y)

#------------>>>> Coefficients
'''3- affichage de regr.coef_ (la pente 'm') et l'ordonnee a l'origine regr.intercept_'''
print("La pente est 'm' est : ", regr.coef_)
print("`l'ordonnee a l'origine 'b' est : ", regr.intercept_)
# ✔️ Tu récupères les paramètres de la droite :
#
# coef_ = pente m
#
# intercept_ = ordonnée à l’origine b
#
# Ta droite de régression : y = m × X + b


#------------>>>>Prédictions

print("prediction : ")
y_predict = regr.predict(X)  # ✔️ Tu prédis les y (valeurs estimées) à partir des X.

#------------>>>>10 Affichage
plt.figure(figsize=(8, 5))
plt.scatter(X, y, color='orange', label='Données réelles')
plt.plot(X, y_predict, color='blue', label='Régression linéaire')
plt.title('Régression linéaire de la production de miel')
plt.xlabel('Année')
plt.ylabel('Production moyenne (totalprod)')
plt.grid(True)
plt.legend()
plt.show()

print("\n\n")


"""Predict the Honey Decline"""

# Variable indépendante : X (2013 à 2049)
X_future_21 = np.array(range(2013, 2050))# tableau 1D
X_future_21_reshaped = X_future_21.reshape(-1, 1) # tableau 2D

# Prédiction avec la version reshaped
future_predict = regr.predict(X_future_21_reshaped)

# Affichage
plt.figure(figsize=(10, 6))
plt.scatter(X, y, color='orange', label='Données historiques')
plt.plot(X_future_21_reshaped, future_predict, color='blue', label='Prédictions futures')
plt.title('📉 Régression linéaire : Production de miel jusqu’en 2050')
plt.xlabel('Année')
plt.ylabel('Production moyenne (totalprod)')
plt.grid(True)
plt.legend()
plt.show()



"""
🧠 Résumé : toujours prédire avec la forme que le modèle attend
X pour sklearn doit toujours être en 2D → .reshape(-1, 1)

Ce même X reshaped doit être utilisé à la fois pour la prédiction et l'affichage


"""
