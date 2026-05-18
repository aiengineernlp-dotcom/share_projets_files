import matplotlib.pyplot as plt
import pandas as pd
from pandas import read_csv
import  numpy as np

# cha=rgement de la donnee
coffee = read_csv("../data/coffee_data.csv")
print("\n",coffee.info)
age = coffee ['age']
"""Centralisation"""
#1- calcul de la moyenne
mean_age = np.mean(age)

#2- centering
centered_mean = age - mean_age

"""Normalization/ Standartisation"""
# eccart type
ecart_type = np.std(age)

z  = centered_mean/ecart_type
print(z.head(5))


plt.figure(figsize=(8,5))
plt.hist(z,bins=30,color='skyblue',edgecolor='black')
plt.title("Distribution des ages Normaliser (Z-scores)")
plt.xlabel("Z-scores")
plt.ylabel("Nombre de clients")
plt.axvline(0, color='red', linestyle='--', label="Moyenne (Z=0)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
