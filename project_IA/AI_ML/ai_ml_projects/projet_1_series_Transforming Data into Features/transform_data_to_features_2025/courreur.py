

# importer le dataset
import pandas as pd
reviews  = pd.read_csv('data/reviews.csv')
from sklearn.preprocessing import LabelEncoder
import category_encoders as ce

print("\n--->> importation des donnees ....")
"""Basic Exploration"""

online_c = pd.read_csv('data/online_course_feedback.csv')


print("\naffichage des collones du dataset c'est a dire les variables categorielles")
print(reviews.columns)
print('\naffichage du type de donnees ')
print(reviews.dtypes)
print('\naffichage des informatiomns sur le dataset')
print(reviews.info)
print('\n afficher linformation des collones/variables/variables categorielle du dataframe')
print('-------',reviews['Title'].info)

"""Data Transformations"""

'''Recommended IND FEATURE'''
# Start by printing the feature’s .value_counts().

print('\n Affichage des etiquettes de la variable Recommended IND ') # A partir d'ici je sais quel methode d'encodage choisir. confirme si c'est bien ici que on le decouvre.
print(reviews['Recommended IND'].value_counts())  # vu que nous avons deja les valeurs numeriques et que c'est binaire, (1,0) on ne va plus rien transformer

# Création d'une copie : nouvelle colonne pour conserver la version d'origine sans modifier la colonne 'Recommended IND'
reviews['Recommended_IND_Binary'] = reviews['Recommended IND']
print("COPIE_1::::", reviews['Recommended_IND_Binary'].value_counts())


'''RATING FEATURE  Department Name'''

print("AVANT LA TRANSFORMATION ",reviews['Rating'].value_counts()) # pour voir les etiquetes dans cette variable
#---> a cause des sortis ordonner je vais faire un encodage Ordinal encoder

encoder = ce.BinaryEncoder(cols=['Rating'],drop_invariant= True).fit_transform(reviews)
print("--- APRES LA TRANSFORMATION BinaryEncoder en action ----",encoder)


'''Department Name FEATURE  '''

# 1. Vérifier les étiquettes
print("Les étiquettes de Department Name\n", reviews['Department Name'].value_counts())

# 2. One-hot encoding pour variable catégorielle nominale
# On ajoute un préfixe pour éviter les collisions de noms
ohe = pd.get_dummies(reviews['Department Name'], prefix='Dept')

# 3. On concatène les colonnes encodées au DataFrame original
reviews = pd.concat([reviews, ohe], axis=1)
#OR
"""reviews  = reviews.join(ohe)"""


# (Optionnel) Vérification des nouvelles colonnes
print("Nouvelles colonnes après encodage one-hot :\n", ohe.columns.tolist())



'''Title FEATURE (encodage binaire car trop de catégories uniques)'''

# Afficher les étiquettes de Title
print("Etiquettes de Title: \n", reviews['Title'].value_counts())

# Comme la colonne Title contient trop de catégories uniques (>10)
# et qu'il n'y a pas d'ordre logique entre elles, on utilise un encodage binaire
# au lieu d'un encodage one-hot (qui créerait trop de colonnes)

# Étape 1 : Remplacer les valeurs manquantes
reviews['Title'] = reviews['Title'].fillna("Unknown")

# Étape 2 : Appliquer BinaryEncoder
import category_encoders as ce
title_encoded = ce.BinaryEncoder(cols=['Title'], drop_invariant=True).fit_transform(reviews)

# Étape 3 : Fusionner les nouvelles colonnes dans le dataframe original si nécessaire
# reviews = pd.concat([reviews, title_encoded], axis=1)

# Affichage pour vérification
print("les resultats :::::\n",title_encoded.head())













