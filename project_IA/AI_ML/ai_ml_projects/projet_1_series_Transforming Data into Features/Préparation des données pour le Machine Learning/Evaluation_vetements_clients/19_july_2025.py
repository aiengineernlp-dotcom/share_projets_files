import pandas as pd
import numpy as np
from category_encoders import OrdinalEncoder
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, LabelEncoder


print("📁 1. Importation des données\n\n")
print("importation des donnees\n")
print("chargement du fichier\n")
fichier =pd.read_csv ("data/reviews_clients_vetement2.csv")
print("Convertion du fichier en dataset grace a pandas Dataframe\n")
df = pd.DataFrame(fichier)
print("les premieres l;ignes du dataset: \n",df.head(5),"\n")
print("liste des colonnes du dataset:\n", df.columns,"\n")
print("les types de donnees du dataset plus exactement les type de variables qui sont dans le dataset\n",df.dtypes,"\n")
print("les informations genrales du dataset: \n",df.info(),"\n")

print("🧭 2. Exploration des données\n\n")
print("AFFICHAGE DES ETIQUETTES/(VALEURS UNIQUES/CATEGORIES) DE TOUTES LES VARIABLES CATETORIELLES ET PRECISION DU TYPE D'ENCODAGE ET POURQUOI\n")
print("les etiquettes/valeurs uniques/categories de clothing_id:\n",df['clothing_id'].value_counts(), "\n","Type d'encodage:""On Scale juste avec StandartScaling"
"\n","Raison: car cette variable categorielle est un ensemble de valeurs discrettes ( chiffres continues positifs)")
print("les valeurs uniques/etiquettes/categories de age \n",df['age'].value_counts(),"\n","Type d'encodage: on scale juste avec standartsaclaer ","\n","Raison:car cette variable categorielle , ce sont les valeurs continues dicrettes (valeurs positives) ")
print("les etiquettes / valeurs uniques/ categories de Title:\n",df['Title'].value_counts()  ,"Type d'encodage: text vectorization de NLP""\n","Raison: Car la variable categorielle est un ensemnble de texte libres entree par les clients a valeurs semantique (ayant du sens)")
print("les etiqiuettes/valeurs uniques/categories de Review Text\n",df['Review Text'].value_counts(),"\n","Type d'encodage: text vectorization de NLP","\n","Raison: texts libres a valeurs semantiques ")
print("les etiquetes/ valeurs uniques/categorires de Rating\n ",df['Rating'].value_counts(),"\n","Type d'encodage: ordinal \n", "raison: car la variable categorielle a une representation hierarchique/ordonnee de ses etiquettes ")
print("les etiquettes/valeurs uniques/categories de Recommended IND \n", df['Recommended IND'].value_counts(),"\n", "type d'encodage: binaire" "","\n" ,"Raison: car on avons deux etiquettes et aussi c'est du genre True/False, yes or no, oui ou non ""\n" ,"Note: ici il ne faut pas confondre avec le binaryEncoder qui est le superieur (au lieu d'utiliser le one HOT LORSQUJE ON A POLUS DE 10 CATEGORIES ON PENSE A BINARY ENCODER ) de l'encodage Onehot  ")
print("les etiquettes /valeurs uniques/ categories de Positive Feedback Count: ", df['Positive Feedback Count'].value_counts(),"\n","Type encodage: on scale juste ""\n","Raison: ce sont des valeurs numeriques continue (valeurs positives) ")
print("les etiquettes/valeurs uniques/categories de Division Name", df['Division Name'].value_counts(),"types encodage: one hot  ","\n" "raison: car la variable categorielle a moins de 10 etiquettes ")
print("les etiquettes/valeurs uniques/categories de Class Name", df['Class Name'].value_counts(),"types encodage: one hot  ","\n" "raison: car la variable categorielle a moins de 10 etiquettes ")
print("les etiquettes/valeurs uniques/categories de Department Name", df['Department Name'].value_counts(),"types encodage: one hot  ","\n" "raison: car la variable categorielle a moins de 10 etiquettes ")
print("\n\n")
print("Encodage de review_date",df['review_date'].value_counts())
print("convertion de review_date de la classe object a datetime grace a pandas  ")
df['review_date_to_date_time'] = pd.to_datetime(df['review_date'])
print(df['review_date_to_date_time'])


print(" 🔁 3. Encodage des variables catégorielles\n")

print("encodage de review_date")
print("\n")
print("Encodage de : jour,weekend,mois,trimestre(quarter), annee,\n")
# jour
df['jour_random'] = df['review_date_to_date_time'].dt.day
print("le jour random est : \n", df['jour_random'] )
#dayofweek
df['day_of_week'] = df['review_date_to_date_time'].dt.dayofweek
print("le day_of_week  est : \n", df['day_of_week'] )
# weekend
df['is_weekend'] = df['day_of_week'].apply(lambda x :1 if x >=5 else 0)  # revient ici 🚩🚩🚩🚩🚩
print("le is_weekend  est : \n", df['is_weekend'] )
# mois
df['mois'] = df['review_date_to_date_time'].dt.month
print("le mois  est : \n", df['mois'] )
#trimestre /quarter
df['quarter'] = df['review_date_to_date_time'].dt.quarter
print("le quarter  est : \n", df['quarter'] )
#Annee
df['Annee'] = df['review_date_to_date_time'].dt.year
print("le Annee  est : \n", df['Annee'] )

print("Encodage de clothing_id\n")
sc = StandardScaler()
df['clothing_id_sclaled'] = sc.fit_transform(df[['clothing_id']])
print("clothing_id scalled est: " , df['clothing_id_sclaled']  )
print("\n\n")
print("Encodage de age\n")
df['age_scaled'] = sc.fit_transform(df[['age']])
print("age scalled est: " , df['age_scaled'])
print("\n\n")
print("Encodage de Rating \n# methode avec .map via le dictionnaire\n")
# methode avec .map via le dictionnaire
Rating_dict = {
    "Loved it" : 5,
    "Liked it": 4,
    "Was okay":3,
    "Not great": 2,
    "Hated it":1
}
df['Rating_map_encoder'] = df['Rating'].map(Rating_dict)
print("le resultat est : \n", df['Rating_map_encoder'].head())

print("Encodage de Rating \n# methode avec .map via le dictionnaire\n")
# methode avec ordinalEncoder via le dictionnaire
# nottoyage ds valeeurs pour enlever les espaces en debut et en fin des chaines
df['Rating'] = df['Rating'].astype(str).str.strip()
# creation de lencodeur et definition de lordre des categories
oe = OrdinalEncoder(categories=[['Loved it','Liked it','Was okay','Not great','Hated it']])
# remodelisation de la variable
Rating_reshaped = df['Rating'].values.reshape(-1,1)
# creer une nouvelle collone avec les valeurs numeriques
df['Rating_Ordianl_Encoder'] = oe.fit_transform(Rating_reshaped)
print("\n✅ Données transformation/encodees :",df['Rating_Ordianl_Encoder'].value_counts())
print('\n\n=======================')
print("Encodage \nRecommended IND ")
# methode avec label encoder
le = LabelEncoder()
df['Recommended_IND_binary'] = le.fit_transform(df['Recommended IND'])
# juste une transformation via copie
df["Recommended_IND_just_copie "] = df['Recommended IND']
print("le resultat est ", df["Recommended_IND_just_copie "])
print('\n\n=======================')
print("Encodage \nPositive Feedback Count")
df['Positive_Feedback_Count_just_copie'] = df ['Positive Feedback Count']
print("le resultat est ", df['Positive_Feedback_Count_just_copie'])

print("Encodage \nDivision Name")
# creation des collonnes (une par classe name) grace a la methode get_dummies de Pandas
Division_Name_one_hot = pd.get_dummies(df['Division Name'],prefix="Division")
# ajout des collonnes au dataFrame
df = df.join(Division_Name_one_hot)
print("\n✅ Données transformation/encodees :",Division_Name_one_hot.columns.tolist())
print('\n\n=======================')
print("Encodage \nDepartment Name ")

# creation des collonnes grace a la methode get_dommies de pandas (pour chaque departement on cree une collone)
Department_Name_one_hot_e = pd.get_dummies(df['Department Name'],prefix="Department")
# ajouter les collones au dataframe
df = df.join(Department_Name_one_hot_e)
print("\n✅ Données transformation/encodees :",Department_Name_one_hot_e.columns.tolist())

print('\n\n=======================')
print("Encodage \nClass Name ")
# creation de des collones grace a la methode get_dummies de pandas
Class_name_one_hot_e = pd.get_dummies(df['Class Name'],prefix="Class")
#ajouter les colonnes au dataframme
df = df.join(Class_name_one_hot_e)

print("🧮 4. Mise à l’échelle des données")
#1-prepartion des donnees
cols_numm = ['Recommended_IND_binary','Rating_Ordianl_Encoder','age_scaled']
cols_ohe = Department_Name_one_hot_e.columns.tolist()+ Division_Name_one_hot.columns.tolist()+ Class_name_one_hot_e.columns.tolist()
cols_Date = ['day_of_week','quarter','Annee']
feature_to_scaled = cols_Date + cols_ohe + cols_numm
#2- scaling
sc = StandardScaler()
scaling_array = sc.fit_transform(df[feature_to_scaled].copy())
# reccrer un dataframe avec les memes index
df_scaleed = pd.DataFrame(scaling_array,columns=feature_to_scaled,index=df.index)

print("\n✅ AFFICHAGE Données après mise à l’échelle :")
print(df_scaleed.head())