#❌❌❌❌from statistics import LinearRegression # -----------❌❌❌❌attention a la confusion
from sklearn.linear_model import LinearRegression

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from torch.fx.experimental.unification.unification_tools import groupby

"""Check out the Data"""


df = pd.read_csv('data/honeyproduction.csv')
print(df.info)
print(df.columns)
print("Structure de la table: \n",df.head())
print("Production par annnee: \n ")

# # grouping by single column genre chaque annee est dans sa colonne
# prod_per_year = df.groupby('year')
# print(prod_per_year)
# # prod_per_year = df.groupby('year').totalprod.mean().reset_index()
# # application de la fonction sum() sur chaque annee
# sum_by_year = prod_per_year['totalprod'].sum()
# print(sum_by_year)

# creation des groupes des annees il cree autant de groupe quil ya d'annee disteinte dans la colonne Year
groupe_per_year = df.groupby('year')

# somme de la production pour chaque annee ou par annnee.

sum_prod_per_year = groupe_per_year['totalprod'].sum().reset_index() # il va prendre tous les 2001 et les mettre dans
# un groupe appeller groupe1;tous les 2004 et les mettre dans un groupe appeller groupe2; etc ... mais plus important
# encore, on voit que grace a groupby, "sum_prod_per_year et mean_prod_per_year" sont les datasets qui ont pour
# colonnes les variables utilisees depuis l'appel de groupby(), ou alors qui a pour collonnes les variables
# utilises dans leurs utilisations ainsi on peux faire sum_prod_per_year.columns ou mean_prod_per_year.columns et voir les sorties
print("Somme de la prodution par annnee\n",sum_prod_per_year)

# moyenne de la production pour chaque annee ou par annnee.
mean_prod_per_year = groupe_per_year['totalprod'].mean().reset_index()
print(" Moyenne de la production par annee \n",mean_prod_per_year)

# Moyenne total de la production pour toute les annee

mean_globale = df['totalprod'].mean()

# moyenne globale
print("Moyenne totale `Globale\n",mean_globale)

print('\n\n')

#--------------->3
X = mean_prod_per_year['year']
X = X.values.reshape(-1,1) # -1 pour determiner automatiquement le nombre de lignes swlon les donnees et 1 pour juste une colonne
print("",X)
#--------------->4
print('\n\n')
y = mean_prod_per_year['totalprod']
#--------------->5
print('\n\n')
plt.scatter(X,y)
#plt.show()



"""Create and Fit a Linear Regression Model"""

print("Create and Fit a Linear Regression Model")

#1- creation du model
line_fitter_1 = LinearRegression()
print("\n")
#2- entrainer le model sur les donnees
line_fitter_1.fit(X,y)
print("\n")
#3-  afficher les sortie (la pente 'm' et l'ordonnee a l'origine 'b')
print("La pente 'm' est : ", line_fitter_1.coef_)
print("l'ordonne a l'origine 'b' est : ", line_fitter_1.intercept_)
print("\n")
#4- Faire des predictions
#topic: on veut predire quoi ?????
y_predicted = line_fitter_1.predict(X)
print("\n")
print(y_predicted)
print("\n")

plt.plot(y_predicted ,X)
# plt.show()



