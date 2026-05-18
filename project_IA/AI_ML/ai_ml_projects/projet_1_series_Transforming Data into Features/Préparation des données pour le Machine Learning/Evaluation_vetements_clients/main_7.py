"""🧪 Exercice : Préparation des données pour le Machine Learning"""
import pandas as pd
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, LabelEncoder

print("📁 1. Importation des données")
print("Charge le fichier")
my_data_7 = pd.read_csv('data/reviews_clients_vetement2.csv')
print("les premières lignes du datase\n",my_data_7.head())
print("la liste des colonnes\n",my_data_7.columns)
print("les types de données\n", my_data_7.dtypes)
print("les informations générales\n",my_data_7.info)

print("\n\n")

print("🧭 2. Exploration des données")
print("AFFICAHGE DES ETIQUETTES")

print("etiquettes de clothing_id ", my_data_7['clothing_id'].value_counts(),"\n")
print("Type d'encodage : ce sont les valeurs numeriques continue dioscrettes (entiers positifs ) donc deja pret pour le ML. il reste juste a scaler")
print("etiquettes de age ", my_data_7['age'].value_counts(),"\n")
print("Type d'encodage  deja pret pour le ML car ce sont des valeurs numeriques discrettes continues (valeurs positives):")
print("etiquettes de Title ", my_data_7['Title'].value_counts(),"\n")
print("Type d'encodage : Text vectorization car ce sont des valeurs textuelles livres semantiques")
print("etiquettes de Review Text ", my_data_7['Review Text'].value_counts(),"\n")
print("Type d'encodage : Text vectorization car ce sont des valeurs textuelles livres semantiques")
print("etiquettes de Rating ", my_data_7['Rating'].value_counts(),"\n")
print("Type d'encodage : Ordinale/.map, car ce sont des variables categorielles ordinale ")
print("etiquettes de Recommended IND ", my_data_7['Recommended IND'].value_counts(),"\n")
print("Type d'encodage : Binaire car ce sont deux valeurs 1 et 0 ")
print("etiquettes de Positive Feedback Count ", my_data_7['Positive Feedback Count'].value_counts(),"\n")
print("Type d'encodage : deja pret pour le ML car variable numeriques continues (valeur positive) donc il faut juste le scaler ")
print("etiquettes de Division Name ", my_data_7['Division Name'].value_counts(),"\n")
print("Type d'encodage :  one hot ")
print("etiquettes de Department Name ", my_data_7['Department Name'].value_counts(),"\n")
print("Type d'encodage :one hot  ")
print("etiquettes de Class Name ", my_data_7['Class Name'].value_counts(),"\n")
print("Type d'encodage : one hot ")
print("etiquettes de review_date ", my_data_7['review_date'].value_counts(),"\n")
print("Type d'encodage : datetime ")

print('\n\n')
print("🔁 3. Encodage des variables catégorielles")

print("Cas de clothing_id ") # qui n'est pas une Variable categorielle:
sc = StandardScaler ()
my_data_7['clothing_id_scaled'] = sc.fit_transform(my_data_7[['clothing_id']])
print("resultat: \n",my_data_7['clothing_id_scaled']  )
print("\n")

print("Cas de age ") # qui n'est pas une Variable categorielle
my_data_7['age'] = sc.fit_transform(my_data_7[['age']])
print("resultat: \n",my_data_7['age'])
print("\n")

print("Cas de Title ") # NLP

print("\n")

print("Cas de Review Text ") # NLP
print("\n")

print("Cas de Rating ") # qui est  une Variable categorielle
print("Methode:  1 avec .map")
# creation d'un dictionnaire

Rating_dict = {
    "Loved it":5,
    "Liked it": 4,
    "Was okay": 3,
    "Not great":2,
    "Hated it":1
}

# encodage avec map
my_data_7['Rating_map'] = my_data_7['Rating'].map(Rating_dict)
print(" RESULTAT AVEC MAP: \n", my_data_7['Rating_map'])

print("methode avec OrdinalEncoder\n")
# nettoyage des valeurs pour enlever les espaces au debut et en fin de chaines
my_data_7['Rating']=my_data_7['Rating'].astype(str).str.strip()

# creation de l'encoder et definition de lordre des categories
oe = OrdinalEncoder(categories=[['Loved it','Liked it','Was okay','Not great','Hated it']])

# remodelization de la variable

Rating_reshapeed = my_data_7['Rating'].values.reshape(-1,1)
# creer une nouvelles collonnes avec les valeurs numeriques
my_data_7['rating_encoder'] = oe.fit_transform(Rating_reshapeed)
print("\n✅ Données transformation/encodees : rating_encoder \n",my_data_7['rating_encoder'])
print("\n")
le = LabelEncoder()
print("Cas de Recommended IND\n") # c'est deja pret donc je dois faire le scaling directment

my_data_7['Recommended_IND_encoder'] = le.fit_transform(my_data_7['Recommended IND'])
print("Mon resultat code/transfomer est:\n ",my_data_7['Recommended_IND_encoder'])

print("cas de Positive Feedback Count \n")
my_data_7['PositiveFeedbackCount_scaled'] = sc.fit_transform(my_data_7[['Positive Feedback Count']])
print("\n")

print("cas de Division Name\n")
DivisionName_ohe = pd.get_dummies(my_data_7['Division Name'],prefix="Division")
my_data_7 = my_data_7.join(DivisionName_ohe)
print("Affichage des collones ajoutees au dataframe:", DivisionName_ohe.columns.tolist())

print("cas de Department Name\n")
Department_Name_ohe = pd.get_dummies(my_data_7['Department Name'],prefix="Department")
my_data_7 = my_data_7.join(Department_Name_ohe)
print("Affichage des collones ajoutees au dataframe:", Department_Name_ohe.columns.tolist())
print("cas de Class Name\n")
Class_Name_ohe = pd.get_dummies(my_data_7['Class Name'],prefix="Class")
my_data_7 = my_data_7.join(Class_Name_ohe)
print("Affichage des collones ajoutees au dataframe:",Class_Name_ohe.columns.tolist())

print("ENCODAGE DE review_date:\n")
# transformer review_date en datime
print(my_data_7['review_date'])
my_data_7['review_date'] = pd.to_datetime(my_data_7['review_date'])
print(my_data_7['review_date'])
# jour random de la semaine :
my_data_7['random_day']= my_data_7['review_date'].dt.day
print("jour random de la semaine\n",my_data_7['random_day'])

my_data_7['jour_dela_semaine'] = my_data_7['review_date'].dt.dayofweek
print("Jour de la semaine: \n", my_data_7['jour_dela_semaine'].head())

my_data_7['is_Weekend'] = my_data_7['jour_dela_semaine'].apply(lambda x:1 if x>=5 else 0)  # 🚩🚩🚩🚩attention on travail avec  "day_of_week" car on l'a utilier avant🚩
print("Jours weekend\n",my_data_7['is_Weekend'])

my_data_7['mois'] = my_data_7['review_date'].dt.month
print("Jours weekend\n",my_data_7['mois'])

my_data_7['quarter'] = my_data_7['review_date'].dt.quarter
print(my_data_7['quarter'])

my_data_7['annee'] = my_data_7['review_date'].dt.year
print("Jours weekend\n",my_data_7['annee'])

print("\n\n")
print("🧮 4. Mise à l’échelle des données")

print("preparation des donnes pour le scaling ")

# colonnes numeriques
num_cols = ['clothing_id_scaled','age','Rating_map','Recommended_IND_encoder','PositiveFeedbackCount_scaled']

# colonne one_hot
col_one_hott= DivisionName_ohe.columns.tolist()+Department_Name_ohe.columns.tolist()+Class_Name_ohe.columns.tolist()

# colonne datetime
col_date_time = ['annee','jour_dela_semaine','is_Weekend','annee']
# liste finale =
feature_to_scale = num_cols + col_one_hott + col_date_time

#scaling

scale_arrray = sc.fit_transform(my_data_7[feature_to_scale].copy())

my_data_7_scaled = pd.DataFrame(scale_arrray,columns=feature_to_scale,index=my_data_7.index)

print("\n✅ Données après mise à l’échelle :")
print(my_data_7_scaled.head())
