import pandas as pd
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, LabelEncoder

print("📁 1. Importation des données")

print("chargemnent du fichier \n")
reviews = pd.read_csv("data/reviews_clients_vetement2.csv")

print(" Affiche :")
print("\nles premiere lignes du dataset \n", reviews.head())
print("\nLa liste des collonnes :", reviews.columns)
print("\nles types de données:\n", reviews.dtypes)
print("\nles informations générales: \n", reviews.info)
print("\n\n")

print("🧭 2. Exploration des données")
print("Affichages des etiquettes des variariables categorielles\n et Identification des variables")

print("cas de clothing_id: \n", reviews['clothing_id'].value_counts())
print("Type de l'encodage: pret pour le ML ")
print("Raison: car ce sont les variables numeriques continues discretes et non des variables categorielles ")
print("\n\n")
print("cas de age\n: ",reviews['age'].value_counts())
print("Type de l'encodage: pret pour le ML ")
print("Raison: car ce sont les variables numeriques continues discretes et non des variables categorielles ")
print("\n\n")
print("cas de Title \n ",reviews['Title'].value_counts())
print("Type de l'encodage: NLP /text vectorization")
print("Raison: car de sont des texte sementiques libres ecrites par les utilisateurs et non des variable categorielles  ")
print("\n\n")
print("cas de Review Text \n",reviews['Review Text'].value_counts())
print("Type de l'encodage: text vectorization/NLP")
print("Raison: car ce sont les textes semenatiques libres ecrites par les utilisateurs")
print("\n\n")
print("cas de Rating \n",reviews['Rating'].value_counts())
print("Type de l'encodage: Ordinale ")
print("Raison: car ce sont les variables categorielles ordonnees hierarchiquement ")
print("\n\n")
print("cas de Recommended IND\n ",reviews['Recommended IND'].value_counts())
print("Type de l'encodage:  deja numerique donc pret pour le ML ")
print("les variables binaires: Recommended IND \nRaison: Car cette variable a juste "
      "deux valeurs 0 et 1. il pouvait aussi etre True ou False; yes or no et dans ce cas la ou ferais un encodage"
      " mais ici pas besoin ce sont deja des variables numeriques prette pour le ML")
print("\n\n")
print("cas de Positive Feedback Count\n ",reviews['Positive Feedback Count'].value_counts())
print("Type de l'encodage: pret pour le ML ")
print("Raison: car ce sont les variables numeriques continues discretes et non des variables categorielles ")
print("\n\n")
print("cas de Division Name\n",reviews['Division Name'].value_counts())
print("Type de l'encodage: One Hot ")
print("Raison: car ce sont des variables categorielles ")
print("\n\n")
print("cas de Department Name\n",reviews['Department Name'].value_counts())
print("Type de l'encodage: One Hot ")
print("Raison: car ce sont des variables categorielles ")
print("\n\n")
print("cas de Class Name\n",reviews['Class Name'].value_counts())
print("Type de l'encodage: One Hot ")
print("Raison: car ce sont des variables categorielles ")
print("\n\n")
print("cas de review_date\n",reviews['review_date'].value_counts())
print("Type de l'encodage: date-time ")
print("Raison: car les variables de types data time (dt)")
print("\n\n")



print("🔁 3. Encodage des variables catégorielles")


print("\n Encodage de clothing_id ") # etant une variable contninue discrette (rntiers positifs) deja pret pour le ML j'applique directement le scaling (on ne transforme plus)
sc = StandardScaler()

reviews['clothing_id_scaled'] =sc.fit_transform(reviews[['clothing_id']])
print("Resultats sclaler: \n",reviews['clothing_id_scaled'])
print("\n")

print("\n Encodage de age ")  # etant une variable contninue discrette (rntiers positifs) deja pret pour le ML j'applique directement le scaling (on ne transforme plus)
reviews['age_scaled'] = sc.fit_transform(reviews[['age']])
print("Resultats sclaler: \n",reviews['age_scaled'])
print("\n")

print("\n Encodage de Title ")  # etant une variable semantique, on passe directement a text vectorization/NLP)
print("\n")
print("\n Encodage Review Text ")  # etant une variable semantique, on passe directement a text vectorization/NLP)
print("\n")

print("\n Encodage de Rating ")  # etant une variable categorielle , ordinale, on fera l'encodage avec soit le .map, soit le OrdinalEncoder
print("Methode 1  avec le Map")
# creation du dictionnaire:
rating_dict = {
    'Loved it' :   5,
    'Liked it' :   4,
    'Was okay':   3,
    'Not great':    2,
    'Hated it'  : 1
}
#Encodage AVEC .map
reviews['rating_map'] = reviews['Rating'].map(rating_dict)
print("RESULTAT AVEC MAP encoder,\n",reviews['rating_map'] )

print("\n")
print("Methode 2  avec le Ordinal encoder")
# nettoya des des valeurs pour enlever les espaces superflux en debut et en fin de chaines
reviews['Rating'] = reviews['Rating'].astype(str).str.strip()

# creation de lencoder et definition de l'ordre des categories/valeurs uniques
oc = OrdinalEncoder(categories=[['Loved it','Liked it','Was okay','Not great','Hated it']])
# remodelization de la variable
rating_reshaped = reviews['Rating'].values.reshape(-1,1)
# creer une nouvelle variable/colonne avec les valeurs numeriques
reviews['rating_encoder'] = oc.fit_transform(rating_reshaped)
print("\n✅ Données transformation/encodees :",reviews['rating_encoder'].value_counts())
print("\n")
print("\n Encodage de Recommended IND ")
le = LabelEncoder()
reviews['Recommended_IND_encoder'] = le.fit_transform(reviews['Recommended IND'])
print("\n✅ Données transformation/encodees \n" ,reviews['Recommended_IND_encoder'])
print("\n")

print("\n Encodage oneHot de Division Name ")
# creation des nouvelles collones avec la methodes get_dummieus de pandas
Division_Name_ohe = pd.get_dummies(reviews['Division Name'],prefix='Division')
# Ajouter les collones au dataframe
reviews = reviews.join(Division_Name_ohe)
print("Affichage des collones ajoutees au dataframe: ", Division_Name_ohe.columns.tolist())

print("\n Encodage oneHot de Department Name ")
# creation des nouvelles collonnes avec la methode get_dummieus de pandas
DepartmentName_ohe  = pd.get_dummies(reviews['Department Name'],prefix='Department')
# ajout de ces nouvelles colones au dataframe
reviews = reviews.join(DepartmentName_ohe)
# affichage des resultats
print("Affichage des collones ajoutees au dataframe: \n", DepartmentName_ohe.columns.tolist())
print("\n Encodage oneHot de Class Name ")
# creation des nouvelles colonnes avec la methode get_dummies de pandas
Class_Name_ohe = pd.get_dummies(reviews['Class Name'],prefix='Class')
# ajouter ces collonnes au dataframe
reviews = reviews.join(Class_Name_ohe)
print("Affichage des collones ajoutees au dataframe: \n", Class_Name_ohe.columns.tolist())
print("\n Encodage date time review_date")
# Convertion en datetime
# print("avant conversion\n",reviews['review_date'])
reviews['review_date']=pd.to_datetime(reviews['review_date'])
# print("apres conversion\n",reviews['review_date'])
print("Cas de jour: \n")
reviews['random_day']= reviews['review_date'].dt.day
print(reviews['random_day'].head())
print("\n")
reviews['day_of_week']= reviews['review_date'].dt.dayofweek
print(reviews['day_of_week'])
print("\n")
print(" L’indication weekend ou semaine:\n")
reviews['is_weekend'] = reviews['day_of_week'].apply(lambda x:1 if x>=5 else 0) # 🚩🚩🚩🚩attention on travail avec  "day_of_week" car on l'a utilier avant🚩
print(reviews['is_weekend'])
print("\n")
print('Mois:\n')
reviews['month']= reviews['review_date'].dt.month
print(reviews['month'])
print('Trimestre/quarter:\n')
reviews['quarter'] = reviews['review_date'].dt.quarter
print(reviews['quarter'].head())
print("\n")
print("Annee:\n")
reviews['year'] = reviews['review_date'].dt.year
print(reviews['year'].head())





print("\n\n")
print("🧮4. Mise à l’échelle des données")
print("Preparation des donnees pour le scaling")

# Colonnes numeriques utiles
cols_num = ['clothing_id_scaled','age_scaled','rating_map','Recommended_IND_encoder']
# colonnes one hot utiles
cols_one_hot =Division_Name_ohe.columns.tolist()+DepartmentName_ohe.columns.tolist()+Class_Name_ohe.columns.tolist()

#Colonnes temporelles pertinentes (on exclut 'jour_normal' et 'is_weekend')
date_cols = ['month', 'day_of_week', 'quarter', 'year']
# liste finale
feature_to_scale = cols_num + cols_one_hot + date_cols


# scaling
scale_array =sc.fit_transform(reviews[feature_to_scale].copy())
# recreer un dataframe avec les meme index
reviews_scaled = pd.DataFrame(scale_array,columns=feature_to_scale,index=reviews.index)

# 8. Affichage
print("\n✅ Données après mise à l’échelle :")
print(reviews_scaled.head())

print("\n\n")







# ✅ Données après mise à l’échelle :
#    clothing_id_scaled  age_scaled  ...  Class_Lounge  Class_Pants
# 0            0.043822    1.100342  ...     -0.403042     -0.40632
# 1            1.378626   -0.369812  ...      2.481129     -0.40632
# 2           -0.129529   -0.436637  ...     -0.403042     -0.40632
# 3           -1.481668   -1.706315  ...     -0.403042     -0.40632
# 4            0.113162    0.833041  ...     -0.403042     -0.40632



# ✅ Données après mise à l’échelle :
#    clothing_id_scaled  age_scaled  rating_map  ...  day_of_week   quarter      year
# 0            0.043822    1.100342    0.801135  ...    -0.501795 -1.258835 -1.125416
# 1            1.378626   -0.369812    0.801135  ...    -0.501795 -1.258835 -1.125416
# 2           -0.129529   -0.436637   -1.260085  ...    -0.501795 -1.258835 -1.125416
# 3           -1.481668   -1.706315    0.801135  ...    -0.501795 -1.258835 -1.125416
# 4            0.113162    0.833041   -0.229475  ...    -0.501795 -1.258835 -1.125416



"""NOTES"""


"""
N:1
====>>> La methode .str.strip() d'une ligne tel que: df['Rating'] = df['Rating'].astype(str).str.strip()
#ne dois pas etre utilisee sur une dataframe entiere mais doit etre utiliser UNIQUEMENT SUR UNE SERIE DE TYPE CHAINE 
#DE CARACTERES (pd.Series), c'est a dire sur une seule colonne contenant les chaines. PAS SUR UN DATAFRAME ENTIER/COMPLET   
"""

"""
N:2
====>>>  df[['Rating']] = ..., retourne une Dataframe pas une Series de type object/str
"""


"""
N:3 -- DataFrame Vs Series
====>>>  Un dataframe l'ensembles des colonnes avec leurs types, c'est en un mot notre Dataset / jeu de donnees
====>>>  Une "Serie" est une colonne du Dataframe ayant un type tel que (object, str , int64 , ...). pour avoir les series on  fait pd.Series
====>>>  Alors donc on ne fait pas la methode .str.strip() sur un dataframe mais on le fait sur les series et il faut savoir que :
df[['Rating']] retourne un DataFrame, pas une Series, et str.strip() ne fonctionne pas sur les DataFrames.

====>>> df['Rating'] = df['Rating'].astype(str).str.strip().   ---->>>df['Rating'] retourne une Serie
df[['Rating']] = ..., retourne une Dataframe pas une Series de type object/str
====>>> df[['Rating']] = df[['Rating']].astype(str).str.strip()  # ❌ ❌❌❌❌❌Erreur ici ❌❌❌❌❌ NE SE FAIT PAS
"""