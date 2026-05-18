# 🔹 Exercice 1 : Encodage et détection de variables
# Fichier à utiliser : student_reviews.csv Instructions :
# 1. Charge le fichier.
# 2. Identifie les variables catégorielles, numériques et booléennes.
# 3. Pour la variable recommended, effectue un encodage binaire.
# 4. Pour la variable rating (valeurs : “Excellent”, “Good”, “Average”, “Poor”), effectue un encodage ordinal.
# 5. Pour department_name, effectue un encodage one-hot.


from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OrdinalEncoder
import pandas as pd

print("Chargement du fichier\n")
df = pd.read_csv("data/student_reviews.csv")


print(df.dtypes) # types des variables
print("\n")
print("#Identifie les variables catégorielles, numériques et booléennes.")
print(df['student_id'].value_counts())
print("type Variables: numerique")
print("\n")
print(df['recommended'].value_counts())
print("type Variables: booleennes ")
print("\n")
print(df['rating'].value_counts())
print("type Variables: categorielles ")
print("\n")
print(df['department_name'].value_counts())
print("type Variables: categorielle ")
print("\n")
print(df['age'].value_counts())
print("type Variables: numerique ")
print("\n")
print(df['review_date'].value_counts())
print("type Variables: date time ")
print("\n")

print("ENCODAGE\n")

print("variable recommended, encodage binaire.")

#METHODE 1 avec .map
# creation d'un dictionnaire
recommended_dic= {
    True : 1,
    False: 0
}

# encodage avec .map en creant directement une nouvelle collone
df['recommended_map'] = df['recommended'].map(recommended_dic)
print("METHODE 1 avec MAP: Donnees transformees/encodees:  \n", df['recommended_map'].head())

#METHODE 2 avec LabelEncoder

le = LabelEncoder()
df['recommended']=le.fit_transform(df['recommended'])

print("METHODE 2 avec LabelEncoder: Donnees transformees/encodees: \n ",df['recommended'].head())

print('\n\n')
print("variable rating (valeurs : “Excellent”, “Good”, “Average”, “Poor”), effectue un encodage ordinal.")

# creation du dictionnaire

rating_dict = {
    'Excellent':4,
    'Good':3,
    'Average':2,
    'Poor':1
}

# Premiere methode avec map
df['rating_map'] = df['rating'].map(rating_dict)
print("Donnees transformees/encodees:\n",df['rating_map'].head())
print('\n\n')
# deuxime methode avec OrdinalEncoder

oc = OrdinalEncoder(categories=[['Excellent','Good','Average','Poor']])
#remodeller la variable
rating_reshaped = df['rating'].values.reshape(-1,1)
#creer une nouvelle variable avec les valeurs numeriques
df['rating_Encoder'] = oc.fit_transform(rating_reshaped)

print("Donnees transformees/encodees: \n",df['rating_Encoder'].head())

print('\n\n')

# creation des nouvelles collonnes avec get_dummies de pandas
department_name_ohe = pd.get_dummies(df['department_name'],prefix="department")
#ajouter les nouvelles collones au dataframe
df = df.join(department_name_ohe)
print('Donnees transformees/encodees: \n',department_name_ohe.columns.tolist())

