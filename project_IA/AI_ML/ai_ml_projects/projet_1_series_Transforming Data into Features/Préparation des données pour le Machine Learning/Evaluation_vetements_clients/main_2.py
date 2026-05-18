""" 1. Importation des données"""
import matplotlib.pyplot as  plt
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder ,OrdinalEncoder

reviews = pd.read_csv('data/reviews_clients_vetement2.csv')
print('Les 5 premieres lignes du dataset: \n',reviews.head(5))
print('\n\n=======================')
print('Les colonnes du dataset: \n',reviews.columns)
print('\n\n=======================')
print('Les types de donnees: \n',reviews.dtypes)
print('\n\n=======================')
print('Les infos generales: \n',reviews.info)

"""2. Exploration des données"""

print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  clothing_id  ***")
print("Les etiquetes de clothing_id ",reviews['clothing_id'].value_counts())
print("Type de l'encodage: pret pour le ML ")
print("Raison: car ce sont les variables numérique continues discrettes ")
print('\n=======================')
print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  age  ***")
print("Les etiquetes de age ",reviews['age'].value_counts())
print("Type de l'encodage: pret pour le ML ")
print("Raison: car ce sont les variables numeriques continues discretes ")
print('\n=======================')
print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  Title  ***")
print("Les etiquetes de Title ",reviews['Title'].value_counts())
print("Type de l'encodage: text vectorization ")
print("Raison: ce sont des textes libres  ")
print('\n=======================')
print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  Review Text  ***")
print("Les etiquetes de Review Text ",reviews['Review Text'].value_counts())
print("Type de l'encodage: text vectorization")
print("Raison: ce sont des textes libres et non des variables categorielles ")
print('\n=======================')
print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  Rating  ***")
print("Les etiquetes de Rating ",reviews['Rating'].value_counts())
print("Type de l'encodage: ordinale ")
print("Raison: ce sont des variable categorielles (hierachique / ordonnée)")
print('\n=======================')
print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  Positive Feedback Count ***")
print("Les etiquetes de Positive Feedback Count ",reviews['Positive Feedback Count'].value_counts())
print("Type de l'encodage: pret pour le ML  ")
print("Raison: ce sont les variables numeriques continues discretes et non des variables categorielles ")
print('\n=======================')
print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  Division Name  ***")
print("Les etiquetes de Division Name ",reviews['Division Name'].value_counts())
print("Type de l'encodage: one Hot")
print("Raison: Car nous avons moins de 10 categories donc on ne devrait pas craindre les excedants de ligne crees  ")
print('\n=======================')
print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  Department Name  ***")
print("Les etiquetes de Department Name ",reviews['Department Name'].value_counts())
print("Type de l'encodage: one Hot")
print("Raison: Car nous avons moins de 10 categories (variables categorielles) donc on ne devrait pas craindre les excedants de colonne crees vu que en One-Hot, 50 catégories = 50 colonnes supplémentaires 😬  ")
print("Raison: La variable contient peu de catégories (moins de 10), donc le One-Hot Encoding est approprié et ne pose pas de problème de dimensionnalité.")

print('\n=======================')
print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  Class Name  ***")
print("Les etiquetes de Class Name ",reviews['Class Name'].value_counts())
print("Type de l'encodage: one Hot")
print("Raison: Car nous avons moins de 10 categories donc on ne devrait pas craindre les excedants de colonne crees vu que en One-Hot, 50 catégories = 50 colonnes supplémentaires 😬   ")
print("Raison: La variable contient peu de catégories (moins de 10), donc le One-Hot Encoding est approprié et ne pose pas de problème de dimensionnalité.")

print('\n=======================')
print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  review_date  ***")
print("Les etiquetes de review_date ",reviews['review_date'].value_counts())
print("Type de l'encodage: date time  ")
print("Raison: car nous avons a faire aux date ")
print('\n=======================')
print("*** LES ETIQUETES/CATEGORIES/VARIABLES UNIQUES de :  Recommended IND  ***")
print("Les etiquetes de Recommended IND ",reviews['Recommended IND'].value_counts())
print("Type de l'encodage: binaire  ")
print("Raison: car nous avons juste deux variables (0/1) ")

print('\n\n=======================')

"""3. Encodage des variables catégorielles"""

print("***3.1 Encodage Binaire de la variable Recommended IND ***")
# vu que Recommended IND donne 2 valeurs
# uniques qui sont les chiffres alors c'est deja encoder(transformer) et pret pour le ML;
# donc il faut juste en creer une copie
reviews['Recommended_IND_binary'] = reviews['Recommended IND']
print("\n✅ Données transformation/encodees :",reviews['Recommended_IND_binary'].value_counts())
print('\n\n=======================')

print("***3.2 Encodage Ordinal sur la variable Rating METHODE 01 avec .map encoder  ***")
# 1- creation d'un dictionaire
rating_dict = {
    'Loved it':5,
    'Liked it':4,
    'Was okay':3,
    'Not great':2,
    'Hated it':1
}

# 2- creation d'une nouvelle collone et encodage avec map()

reviews['Rating_map'] = reviews['Rating'].map(rating_dict)
print("\n✅ Données transformation/encodees :",reviews['Rating_map'].value_counts())
print('\n\n=======================')


print("***3.2 Encodage Ordinal sur la variable Rating METHODE 02 avec OrdinalEncoder  ***")
# Nettoyage des valeurs pour enlever les espaces supperflus au debut et a la fin des chaines
reviews['Rating'] = reviews['Rating'].astype(str).str.strip()
# creation de l'encoder et definition de l'ordre des categories/valeurs uniques/variables categorielles
oc = OrdinalEncoder(categories=[['Loved it','Liked it','Was okay','Not great','Hated it']])

# Remodelisation de la variable
Rating_reshaped= reviews['Rating'].values.reshape(-1,1)
#creer une nouvelle Variable avec les valeurs numeriques
reviews['Rating_encoder'] = oc.fit_transform(Rating_reshaped)
print("\n✅ Données transformation/encodees :",reviews['Rating_encoder'].value_counts())
print('\n\n=======================')



print("***3.3 Encodage One-Hot de la variable: Class Name ***")
# utilisation de la methode get_dummies de pandas pour creer une colonne par Class Name
class_name_ohe = pd.get_dummies(reviews['Class Name'],prefix='Class')
#ajouter les nouvelles colonnes au Dataframe
reviews = reviews.join(class_name_ohe)
print("\n✅ Données transformation/encodees et colonnes ajoutees: :",class_name_ohe.columns.tolist())
print('\n\n=======================')

print("***3.3 Encodage One-Hot de la variable: Division Name ***")

# Utilisation de la methode get_dummies de pandas pour creer une colonne par Division Name
division_name_ohe = pd.get_dummies(reviews['Division Name'],prefix='Division')
#ajouter les nouvelles colonnes au Dataframe
reviews = reviews.join(division_name_ohe)
print("\n✅ Données transformation/encodees et colonnes ajoutees: :",division_name_ohe.columns.tolist())
print('\n\n=======================')

print("***3.3 Encodage One-Hot de la variable: Department Name ***")
#Utilisation de la methode get_dummies de pandas pour creer une collonne par Department Name
department_name_ohe = pd.get_dummies(reviews['Department Name'],prefix='Department')

#ajouter les nouvelles colonnes au Dataframe
reviews = reviews.join(department_name_ohe)
print("\n✅ Données transformation/encodees et colonnes ajoutees: :",department_name_ohe.columns.tolist())

# # Puis vous les ajoutez à votre DataFrame
# reviews = pd.concat([reviews, class_name_ohe, division_name_ohe, department_name_ohe], axis=1)

# # Maintenant, vous récupérez les vrais noms des colonnes One-Hot
# one_hot_cols = class_name_ohe.columns.tolist() + division_name_ohe.columns.tolist() + department_name_ohe.columns.tolist()

print('\n\n=======================')
print("***3.2 Encodage de la variable review_date ***")
print(reviews['review_date'].head(4)) # dtype: object
print("Conversion en object Datetime\n")
reviews['review_date']= pd.to_datetime(reviews['review_date'])
print(reviews['review_date'].head(4)) # dtype: datetime64[ns]

# Creation des nouvelles variables

print("jour:\n")
reviews['random_day'] = reviews['review_date'].dt.day
print(reviews['random_day'].head())
print('\n=======================')
print('Jour de la semaine\n')
reviews['dayofweek']= reviews['review_date'].dt.dayofweek # exactement "dayofweek"
print(reviews['dayofweek'].head())
print('\n=======================')
print(" L’indication weekend ou semaine:\n")
reviews['is_weekend'] = reviews['dayofweek'].apply(lambda x:1 if x>=5 else 0)
print(reviews['is_weekend'].head())
print('\n=======================')
print('Mois:\n')
reviews['month']=reviews['review_date'].dt.month
print(reviews['month'].head())
print('\n=======================')
print("Le trimestre (quarter)\n")
reviews['quarter']= reviews['review_date'].dt.quarter
print(reviews['quarter'].head())
print('\n=======================')
print("Annee:\n")
reviews['year']= reviews['review_date'].dt.year
print(reviews['year'].head())
print('\n=======================')
print('\n=======================')


print('\n\n=======================')
print("**** 4. Mise à l’échelle des données (StandardScaler) ****")
print("Préparation des données pour le scaling...")

# 1. Colonnes numériques utiles (ceux qui ont ete transformer en chiffres)
base_features = ['Rating_map', 'Recommended_IND_binary']

# 2. Colonnes One-Hot
one_hot_cols = class_name_ohe.columns.tolist() + division_name_ohe.columns.tolist() + department_name_ohe.columns.tolist()

# 3. Colonnes temporelles pertinentes (on exclut 'jour_normal' et 'is_weekend')
date_cols = ['month', 'dayofweek', 'quarter', 'year']

# 4. Liste finale
features_to_scale = base_features + one_hot_cols + date_cols

# 5. Scaling
sc = StandardScaler()
scaled_array = sc.fit_transform(reviews[features_to_scale].copy())

# 6. Recréer un DataFrame avec les mêmes index
reviews_scaled = pd.DataFrame(scaled_array, columns=features_to_scale, index=reviews.index)

# 7. Ajouter is_weekend (binaire) sans le scaler
reviews_scaled['is_weekend'] = reviews['is_weekend'] # 💡 Pourquoi ne pas scaler is_weekend ?
# Parce qu’il s’agit d’une variable binaire (0 ou 1), et que le scaling pourrait lui faire perdre son sens logique dans certains modèles.

# 8. Affichage
print("\n✅ AFFICHAGE Données après mise à l’échelle :")
print(reviews_scaled.head())



"""
🔚 Résultat :
Tu as maintenant un DataFrame reviews_scaled complet et prêt pour le machine learning, avec :

Les variables numériques et OHE bien standardisées

Les variables temporelles extraites et scalées

is_weekend intégrée telle quelle

Tu peux utiliser ce reviews_scaled pour :


X = reviews_scaled
y = reviews['Recommended_IND_binary']  # ou une autre cible

# Puis split/train



"""
"""
✅ Résultat
Tu as maintenant :

Un DataFrame reviews_scaled avec toutes les colonnes utiles, transformées à la même échelle (moyenne = 0, écart-type = 1).
Tu peux l'utiliser directement comme X pour entraîner ton modèle
X = reviews_scaled
y = df['target']  # par exemple
"""



"""
✅ 🔧 Code adaptable pour mise à l’échelle

import pandas as pd
from sklearn.preprocessing import StandardScaler

# Supposons que tu as déjà ce DataFrame `df` avec :
# - des colonnes numériques encodées
# - des colonnes binaires
# - des colonnes one-hot (issues de get_dummies)

# 1. Identifier manuellement les colonnes numériques que tu veux garder
manual_numeric = ['Age', 'Recommended_IND_Binary', 'Rating_Encoded']

# 2. Identifier automatiquement les colonnes one-hot (ex: commençant par 'Division_')
one_hot_cols = [col for col in df.columns if col.startswith('Division_')]

# 3. Créer la liste finale des features à scaler
features_to_scale = manual_numeric + one_hot_cols

# 4. Appliquer le StandardScaler
scaler = StandardScaler()
scaled_array = scaler.fit_transform(df[features_to_scale])

# 5. Recréer un DataFrame avec les colonnes scalées
df_scaled = pd.DataFrame(scaled_array, columns=features_to_scale)

# 6. Afficher un aperçu
print("✅ Données après scaling :")
print(df_scaled.head())


"""


"""
🔁 Astuce : Automatiser encore plus ?
Si tu veux rendre ça encore plus automatique, tu peux filtrer toutes les colonnes numériques (et éviter les colonnes non encodées) :


# Optionnel : sélectionner toutes les colonnes de type numérique
all_numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

# Si tu sais que certaines colonnes numériques ne doivent pas être utilisées (ex: ID, target...)
columns_to_exclude = ['clothing_id', 'target']  # adapte selon ton dataset

# Final list to scale
features_to_scale = [col for col in all_numerical_cols if col not in columns_to_exclude]


"""


