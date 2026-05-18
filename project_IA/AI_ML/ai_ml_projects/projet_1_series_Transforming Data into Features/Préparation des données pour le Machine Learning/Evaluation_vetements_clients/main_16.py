import pandas as pd
from sklearn.preprocessing import StandardScaler

"""📁 1. Importation des données"""
print('Charge le fichier reviews.csv à l’aide de pd.read_csv.')
df = pd.read_csv("data/reviews_clients_vetement2.csv")
print('les premières lignes du dataset\n', df.head(4))
print("la liste des colonnes,\n", df.columns)
print("les types de données\n",df.dtypes)
print("les informations générales avec .info()\n", df.info())



"""🧭 2. Exploration des données""" 'and' """🧭 2. Type et raison de l'encodage des données (etiquettes/valeurs uniques/categories)"""
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['clothing_id'].value_counts() ,"\n")
print("Type: on ne convertie pllus  \nRaison: car ce sont deja les chiffres plus precisement les valeurs continues discrettes (chiffres positifs) \n")
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['age'].value_counts() ,"\n")
print("Type: on ne convertie pllus  \nRaison: car ce sont deja les chiffres plus precisement les valeurs continues discrettes (chiffres positifs) \n")
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['Title'].value_counts() ,"\n")
print("Type: Text vectorization \nRaison: car la variable categorielle est du texte semantique c'est a dire du texte libre ecrit par les utilisateurs et qui du sens et est comprensible \n")
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['Review Text'].value_counts() ,"\n")
print("Type: Text vectorization \nRaison: car la variable categorielle est du texte semantique c'est a dire du texte libre ecrit par les utilisateurs et qui du sens et est comprensible \n")
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['Rating'].value_counts() ,"\n")
print("Type: Ordianal Encoder ou .map via le dictionnaire \nRaison: car les categories ont une classification ordonnee et hierarchique \n")
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['Recommended IND'].value_counts() ,"\n")
print("Type: Binaire/ \nRaison: car c'est juste deux valeurs 0 et 1.\n ici il ne faut pas confondre avec le "
      "BINARY ENCODER. Ici on dit classification binaire car c'est deux valeurs 0/1. POUVAIS ETRE TRUE OU FALSE/ YES OR NO. "
      "C'EST   pourquoi on dit binaire\n"
      "Note: ici on ne encode plus acr c'est deja les chiffres donc on passe direcetement au scaling. mais si ce netait "
      "pas les chiffres on crearait d'abors le dictionnaire puis on ferait le label encoding/encodage nominale")
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['Positive Feedback Count'].value_counts() ,"\n")
print("Type: on ne convertie pllus  \nRaison: car ce sont deja les chiffres plus precisement les valeurs continues discrettes (chiffres positifs) \n")
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['Division Name'].value_counts() ,"\n")
print("Type: one hot \nRaison: car la variable categorielles a moins de 10 etiquettes \n")
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['Department Name'].value_counts() ,"\n")
print("Type: one hot \nRaison: car la variable categorielles a moins de 10 etiquettes \n")
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['Class Name'].value_counts() ,"\n")
print("Type: one hot \nRaison: car la variable categorielles a moins de 10 etiquettes \n")
print("Les etiquettes/valeurs uniques/categories de  \n: ", df['review_date'].value_counts() ,"\n")
print("Type: date time \nRaison: ce sont les dates et les heures ...\nNote:  mais il faut d'abors convertir en datetime avec la metyhode de pandas avant de commencer l'encodage \n")

print('\n\n\n')
print("🔁 3. Encodage des variables catégorielles")

print("Encodage Binaire de  Recommended IND.")
sc = StandardScaler()
df['Recommended_IND_scalled'] = sc.fit_transform(df[['Recommended IND']])
print("variable encodee : ", df['Recommended_IND_scalled'])
print('\n')

print("Encodage  de  age avec StandardScaler .")
df['age_scaled'] = sc.fit_transform(df[['age']])
print("variable encodee : ", df['age_scaled'])
print('\n')

print("Encodage  de  clothing_id avec StandardScaler .")
df['clothing_id_scaled'] = sc.fit_transform(df[['clothing_id']])
print("variable encodee : ", df['clothing_id_scaled'])
print('\n')

print("3.2 Encodage Ordinal de la variable Rating\n:")
Rating_dictt = {
    'Loved it': 5,
    'Liked it': 4,
    'Was okay':3,
    'Not great':2,
    'Hated it':1
}
df['Rating_Encoded'] = df['Rating'].map(Rating_dictt)
print("variable encodee : ", df['Rating_Encoded'])#❌❌ NON A REVOIR❌❌❌
print('\n')

print("3.3 Encodage One-Hot de Class Name: ")
#creation des nouvelles colonnes au dataframe
ClassName__ohe = pd.get_dummies(df['Class Name'],prefix="Class")
# ajout des collonnes au dataframe
df = df.join(ClassName__ohe)
print("variable encodee : ", ClassName__ohe.columns.tolist())
print('\n')

print("3.3 Encodage One-Hot de Department Name: ")
#creation des nouvelles colonnes au dataframe
Department_Name__ohe = pd.get_dummies(df['Department Name'],prefix="Department")
# ajout des collonnes au dataframe
df = df.join(Department_Name__ohe)
print("variable encodee : ", Department_Name__ohe.columns.tolist())
print('\n')

print("3.3 Encodage One-Hot de Division Name: ")
#creation des nouvelles colonnes au dataframe
Division_Name__ohe = pd.get_dummies(df['Division Name'],prefix="Division")
# ajout des collonnes au dataframe
df = df.join(Division_Name__ohe)
print("variable encodee : ", Division_Name__ohe.columns.tolist())
print('\n')
#
print("3.3 Encodage date time de  review_date : ")
df['review_date_date_time'] = pd.to_datetime(df['review_date'])
print("variable convertie en datetime est : ", df['review_date_date_time'])
print('\n')

#conversion d'un random jour
df['jour'] = df['review_date_date_time'].dt.day
print("le resultat est :", df['jour'])
#conversion d'un jour de la semaine
df['day_of_week']= df['review_date_date_time'].dt.dayofweek
print("le resultat est :", df['day_of_week'])
# conversion du weekend
df['is_weekend'] = df['day_of_week'].apply(lambda x:1 if x>=5 else 0)   # 🚩🚩🚩🚩attention on travail avec  "day_of_week" car on l'a utilier avant🚩
print("le resultat est :", df['is_weekend'])
# conversion pour le mois
df['month']= df['review_date_date_time'].dt.month
print("le resultat est :", df['month'])
# conversion pour l'annee
df['year']= df['review_date_date_time'].dt.year
print("le resultat est :", df['year'])
print("🧮 4. Mise à l’échelle des données")
# preparation des donnees
cols_num = ['Recommended_IND_scalled','age_scaled','clothing_id_scaled','Rating_Encoded']
cols_oneHot = ClassName__ohe.columns.tolist() + Department_Name__ohe.columns.tolist() + Division_Name__ohe.columns.tolist()
cols_date = ['is_weekend','month']
# liste finale
feature_to_scale = cols_date + cols_oneHot + cols_num
#scaling
scale_arrray = sc.fit_transform(df[feature_to_scale].copy())

# data_scaled
my_data_scaled = pd.DataFrame(scale_arrray,columns=feature_to_scale,index=df.index)

print("\n✅ Données après mise à l’échelle :")
print("\n", my_data_scaled)




