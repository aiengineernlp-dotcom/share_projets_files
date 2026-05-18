import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
"""Check out the Data"""
df = pd.read_csv('data/honeyproduction.csv')
print("affcher les 5 premiere ligne du Dataframe\n", df.head())
print('\n\n')

print("total of production of honey per year:\n")
methode_groupe_by = df.groupby('year')

print("somme de la production annuelle:\n")
sum_prod_per_year = methode_groupe_by['totalprod'].sum().reset_index()
print("la somme par annee est: ", sum_prod_per_year)
print('\n\n')
print("moyenne de la production annuelle:\n")
mean_prod_per_year = methode_groupe_by['totalprod'].mean().reset_index()
print("la moyenne par annee est: ", mean_prod_per_year)
print('\n\n')
# print(la moyenne globale
mean_globale = df['totalprod'].mean()
print("la moyenne globale est:\n", mean_globale)

#-------------->>>3
print(mean_prod_per_year.columns)
X = mean_prod_per_year['year']
X = X.values.reshape(-1,1)

#-------------->>>4
y = mean_prod_per_year['totalprod']
#-------------->>>5

plt.scatter(X,y)
# plt.show()
print('\n\n')
"""Create and Fit a Linear Regression Model"""
#--------------->6,7,8,9,10
#1- creation du model
regr  = LinearRegression()
#2- entrainement du model
regr.fit(X,y)
#3- Affichage des resultats de l'entrainement
print("La pente est 'm' : \n",regr.coef_)
print("L'ordonnee a l'origine est 'b' : ",regr.intercept_)
#4- prediction
y_prediction = regr.predict(X)
# 5- Tracer la ligne
plt.plot(X,y_prediction)
# plt.show()
print("\n\n")
"""Predict the Honey Decline"""
#--------------->11
nums = np.array(range(1, 11)) # X_future
print (nums)
X_future = nums
print("\n")
X_future = X_future.reshape(-1,1) # revient ici
nums = np.array(range(1,11))

print(X_future)

#--------------->12
future_predict = regr.predict(X_future)
y = future_predict
plt.plot(X_future,y)
plt.show()

print("\n\n")



