'''
Ce code montre que tu sais importer, explorer et préparer des données pour l’analyse,
'''

import pandas as pd # pour la manipulation  de mes fichier csv
import numpy as np  # pour mes fonction mathematique
# from sklearn.preprocessing import StandardScaler # pour standartiser nos donnees


# importer le dataset
print("\n--->> importation des donnees ....")
reviews  = pd.read_csv('data/reviews.csv')

"""Basic Exploration me permetant sutout de savoir quel type de donnees j'ai a faire dans ce cas c'est des donnees categorielle de type Ordinale """
# afficher les colones du dataset
print("\n--->> Affichage des colonnes du dataset(c'est a dire les variables) ....")
print(reviews.columns)
print("\n--->> Affichage des colonnes du dataset avec les types de donnees  (c'est a dire les variables) ....")
print(reviews.dtypes)
#  afficher les infos sur le dataset
print('\n--->> affichages des informations sur le dataset ....')
print(reviews.info())

"""Data Transformations"""










"""Scaling the Data



Ici, il s’agit de préparer tes données pour l’étape de la mise à l’échelle (scaling).
Quand tu as plusieurs colonnes numériques avec des valeurs très différentes (par exemple, l’âge peut aller de 18 à 80, 
alors que d’autres colonnes sont juste 0 ou 1), il est important de les mettre sur la même échelle pour que les modèles 
de machine learning fonctionnent mieux.

L’instruction te demande de :

Garder seulement les colonnes numériques utiles (celles que tu as créées ou transformées, comme age, recommended, rating, etc.)
Créer un nouveau DataFrame avec uniquement ces colonnes.
Cela permet de préparer les données pour l’étape suivante, où tu vas appliquer le “scaling” (mise à l’échelle) avec un outil comme StandardScaler.


"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# import data
reviews = pd.read_csv('reviews.csv')

# Print the column names of your dataset. c'est a dire les variables
print(reviews.columns)
print('\n the column names of your dataset. cest a dire les variables')
# print column names and types (c'est a dire les variables)
print('\n column names and types (cest a dire les variables)')
print(reviews.dtypes)

# print .info
print('\n print .info')
print(reviews.info())

# look at the counts of recommended
print('\n look at the counts of recommended')
print(reviews['recommended'].value_counts())

# create binary dictionary
binary_dict = {
    True: 1,
    False: 0
}

# on crée une nouvelle colonne pour conserver la version transformée (encodée) sans écraser la version originale
reviews['recommended_column_transform'] = reviews['recommended'].map(binary_dict)

# print your transformed column
print("\n Voici la colonne transformee: ")
print(reviews['recommended_column_transform'].value_counts())

# look at the counts of rating
count_of_rating = reviews['rating'].value_counts()
print(count_of_rating, )
print("\n La taille de count_of_ratingc est : ", len(count_of_rating))

# create dictionary
rating_dict = {
    "Loved it": 5,
    "Liked it": 4,
    "Was okay": 3,
    "Not great": 2,
    "Hated it ": 1
}

# transform rating column
reviews['rating_column'] = reviews['rating'].map(rating_dict)

# print your transformed column values
print("\n my transformed column values est ")
print(reviews['rating_column'].value_counts())

# get the number of categories in a feature
print("\n Transformation de department_name")
number_feature = reviews['department_name'].value_counts()
print(number_feature)

# perform get_dummies

"""
cette partie est juste pour la transformation des donnees ??
Ces colonnes viennent de la transformation “one-hot encoding” que tu as faite sur la colonne `department_name` avec la fonction `pd.get_dummies()`.

Quand tu fais :
```python
one_hot = pd.get_dummies(reviews['department_name'])
reviews = reviews.join(one_hot)
```
Pandas crée une colonne pour chaque catégorie trouvée dans `department_name` :  
- `Bottoms`
- `Dresses`
- `Intimate`
- `Jackets`
- `Tops`
- `Trend`

Chaque colonne contient 0 ou 1 pour indiquer si la ligne appartient à cette catégorie.  
C’est ce qu’on appelle l’encodage “one-hot”.
'''
"""

ohe = pd.get_dummies(reviews['department_name'])

# join the new columns back onto the original
reviews = reviews.join(ohe)

print("Pandas crée une colonne pour chaque catégorie trouvée dans department_name ", ohe)

# print column names
print("le resultat est :", reviews)

# transform review_date to date-time data

print("Voici review_date avant la transformation en date time: ")
print(reviews['review_date'])
print("la diffrence est ici AVANT la transformation:", reviews['review_date'].dtype)

reviews['review_date'] = pd.to_datetime(reviews['review_date'])

# print review_date data type
print("Voici review_date apres la transformation en date time: ")
print(reviews['review_date'])
print("la diffrence est ici APRES la transformation: ", reviews['review_date'].dtype)

"""Scaling the Data"""

# get numerical columns

"""j'ai eu une erreur car j'ai sélectionné les colonnes recommended et rating au lieu de leurs versions transformées (recommended_column_transform et rating_column).
Les colonnes d’origine contiennent encore des chaînes de caractères.

Comment corriger ?
Dans la ligne où tu sélectionnes les colonnes pour le scaling, utilise les colonnes transformées : """

reviews = reviews[
    ['clothing_id', 'age', 'recommended_column_transform', 'rating_column', 'Bottoms', 'Dresses', 'Intimate', 'Jackets',
     'Tops', 'Trend']].copy()

# reset index
"""
Pour cette étape, il faut que la colonne clothing_id devienne l’index de ton DataFrame.
Cela veut dire que chaque ligne sera identifiée par la valeur de clothing_id au lieu d’un simple numéro de ligne.

La logique est :

Utilise la méthode .set_index() sur ton DataFrame avec la colonne clothing_id.
Par exemple :

df = df.set_index('clothing_id')

Copy code

Après cela, clothing_id ne sera plus une colonne, mais l’index de chaque ligne.
"""
reviews = reviews.set_index('clothing_id')

# instantiate standard scaler

"""
Ta logique est correcte !  
Voici ce que fait chaque ligne :

1. `reviews = reviews.set_index('clothing_id')`  
   → Met `clothing_id` comme index du DataFrame.

2. `scaler = StandardScaler()`  
   → Crée un objet pour la mise à l’échelle.

3. `reviews = scaler.fit_transform(reviews)`  
   → Applique la transformation sur toutes les colonnes numériques.

4. `print(reviews)`  
   → Affiche le résultat : toutes les valeurs sont maintenant “scalées”.

Après cette étape, tes données sont prêtes pour être utilisées dans un modèle de machine learning.

"""

scaler = StandardScaler()

# fit transform data
reviews = scaler.fit_transform(reviews)
print(reviews)


