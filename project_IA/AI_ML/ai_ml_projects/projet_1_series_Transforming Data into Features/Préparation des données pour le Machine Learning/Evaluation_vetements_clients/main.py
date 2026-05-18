import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from category_encoders import BinaryEncoder
from sklearn.preprocessing import OrdinalEncoder


"""1. Importation des données"""
# Chargement des donnees
df = pd.read_csv("data/reviews_clients_vetements.csv")
# exploration  des types de donnees
print("Les informations sur le dataFrame\n", df.info(),"\n")
print('\n')
print("Les types de donnes\n",df.dtypes,"\n")
print('\n')
print("les premieres 4 lignes du dataset\n", df.head(4))
print('\n')
print("liste des colonnes: \n", df.columns)

# Pour chaque variable catégorielle importante : pour moi je pense que les variables categgorielle
# importante sont decidees par rapport a l'objectyif de lexercice qui porter sur les avis des clients sur les vetements
# alors je crois que ce sera les variables : Rating , Recommended IND , Positive Feedback Count,
#  Mais parce que je suis en phase daprentissage je vais tous les gerer

"""2. Exploration des données"""
print('\n')
print('\n')
print("*** FEATURE:  clothing_id  ***")
print('\n')
print("Affichage des etiquetes de la variable clothing_id \n",df['clothing_id'].value_counts())  # ici on devra faire un encodage binaire car ce sont les variable on a plus de 10
print('\n')
print(f"Type de variable textuelle  'clothing_id:Nominale car pas de mathematiques ni ordonne ni hierrachique entre les etiquettes/categories/valeurs uniques ")
print('\n')
print(f"Type d'encodage pour 'clothing_id' : Encodage Binaire")
print('\n')
print(f"Raison: parceque la sortie de value_count donne plus de 10 les etiquetes=categories=valueurs uniques avec moins de 10 on peut faire l'encodage avec one-hot ")
print('\n')


print("*** FEATURE:  age  ***")

print("\n")
print("Affichage des etiquettes de la variable age\n",df['age'].value_counts())
print("Type d'encodage de la variable age: ENCODAGE BINAIRE")
print("Raison: car la sortie de Value_count donne plus de 10 etiquettes=valeurs unique=categorie .Deplus ce sont des valurs qui n'ont aucune relation ordonnee(hierarchique,mathematique)")
print("\n")

print("*** FEATURE:  Title  ***")
print("\n")
print("Affichage des etiquettes pour la variable Title", df['Title'].value_counts())
print("type de l'encodage: ONE HOT")
print("RAISON : la sortie de Valu_count donne moins de 10 etiquettes = valeurs uniques=categories")
print("\n")

print("*** FEATURE:  Review Text ***")
print("\n")
print("Affichage des etiquettes pour la variable Title", df['Review Text'].value_counts())
print("type de l'encodage: ONE HOT")
print("RAISON : la sortie de Valu_count donne moins de 10 etiquettes = valeurs uniques=categories")
print("\n")



print("*** FEATURE:  Rating ***")
print("\n")
print("Affichage des etiquettes pour la variable Title", df['Rating'].value_counts())
print("type de l'encodage: ORDINAL ")
print("RAISON : la sortie de Valu_count donne juste la fréquence (nombre d’occurrences) de chaque étiquette.")
print("\n")


print("*** FEATURE:  Recommended IND ***")
print("\n")
print("Affichage des etiquettes pour la variable Title", df['Recommended IND'].value_counts())
print("type de l'encodage: ORDINAL OU BINAIRE ")
print("RAISON : parceque on a une relation d'ordre entre les etiquettes = valeurs uniques= categories")
print("\n")


print("*** Positive Feedback Count ***")
print("\n")
print("Affichage des etiquettes pour la variable Title", df['Positive Feedback Count'].value_counts())
print("type de l'encodage: ONE HOT ")
print("Raison: car la sortie de Value_count donne plus de 10 etiquettes=valeurs unique=categorie .Deplus ce sont des valurs qui n'ont aucune relation ordonnee(hierarchique,mathematique)")
print("\n")


print("*** Division Name ***\n")

# Affichage des étiquettes (valeurs uniques et leur fréquence)
print("Affichage des étiquettes pour la variable 'Division Name' :")
print(df['Division Name'].value_counts(), "\n")

# Type d'encodage utilisé
print("Type de l'encodage : ONE HOT")

# Justification du choix
print(
    "Raison : la variable 'Division Name' contient 3 catégories distinctes, "
    "sans relation ordonnée (ni hiérarchique ni mathématique). "
    "Un encodage ordinal pourrait tromper le modèle en lui faisant croire à une hiérarchie entre les catégories. "
    "Le One-Hot Encoding permet donc de représenter chaque catégorie de manière binaire, "
    "sans introduire de relation numérique trompeuse."
)
print("\n")


print("*** Department Name ***")
print("\n")
print("Affichage des etiquettes pour la variable Title", df['Department Name'].value_counts())
print("type de l'encodage: ONE HOT ")
print("Raison: car la sortie de Value_count donne juste 6 etiquettes=valeurs unique=categorie .Deplus ce sont des valurs qui n'ont aucune relation ordonnee(hierarchique,mathematique) ")
print("\n")

print("*** Class Name ***")
print("\n")
print("Affichage des etiquettes pour la variable Title", df['Class Name'].value_counts())
print("type de l'encodage: ONE HOT ")
print("Raison: car la sortie de Value_count donne juste 7 etiquettes=valeurs unique=categorie .Deplus ce sont des valurs qui n'ont aucune relation ordonnee(hierarchique,mathematique) ")
print("\n")


print("*** review_date  ***")
print("\n")
print("Affichage des etiquettes pour la variable Title", df['review_date'].value_counts())
print("type de l'encodage: DATE HEURE ")
print("Raison: c'est question de temps ici. ")
print("\n")
print("\n")



"""3. Encodage des variables catégorielles"""
print("***3.1 Encodage Binaire de la variable Recommended IND ***")

df['Recommended_IND_binary'] = df['Recommended IND']
print("Confirmation de l'encodage Binaire....", df['Recommended_IND_binary'].value_counts())
# vu que Recommended IND donne 2 valeurs
# uniques qui sont les chiffres alors c'est deja encoder(transformer) et pret pour le ML;
# donc il faut juste en creer une copie
print("\n")

print("***3.1 Encodage Binaire de la variable clothing_id ***")
clothingId = BinaryEncoder(cols=['clothing_id'],drop_invariant=True).fit_transform(df)
print("Confirmation de l'encodage Binaire sur clothing_id : \n", clothingId)
print("\n")


print("***3.1 Encodage Binaire de la variable age ***")
Age  = BinaryEncoder(cols=['age'],drop_invariant=True).fit_transform(df)
df = pd.concat([df,Age],axis=1)
print("Confirmation de l'encodage Binaire sur la variable age : \n", Age)

print("\n")
print("\n")

print("***3.2 Encodage Ordinal sur la variable Rating METHODE 01 avec OrdinalEncoder  ***") # CETTE METHODE A UNE ERREUR
# Nettoyer les valeurs pour enlever les espaces supperflus au debut et a la fin des chaines
print(type(df['Rating']))        # doit afficher <class 'pandas.core.series.Series'>
print(type(df[['Rating']]))      # affiche <class 'pandas.core.frame.DataFrame'>
df['Rating'] = df['Rating'].astype(str).str.strip()
#vérifier les valeurs uniques avant d’encoder
# print("UNICITE DES ETIQUETES : ",df['Rating'].unique())
#creation l'encoder et definition de l'ordre des categories/variables uniques/etiquetes
oc = OrdinalEncoder(categories=[['Loved it','Liked it','Was okay','Not great','Hated it']])  # ✅ PAS de virgule à la fin !
# remodeller la variable dans ce cas c'est Rating
Rating_reshaped = df['Rating'].values.reshape(-1,1)

# creation de la collone des donnees transformees
df['rating_transform'] = oc.fit_transform(Rating_reshaped)
print("Confirmation de l'encodage Ordinale sur la variable Rating : \n", df['rating_transform'])
print("\n")
print("***3.2 Encodage Ordinal sur la variable Rating METHODE 02 avec Dictionnaire  ***")

# creation du dictionnaire  en supposant ma propre hierrarchie comme dans le cours
Rating_dic = {
    'Loved it' : 5,
    'Liked it': 4,
    'Was okay':3,
    'Not great':2,
    'Hated it':1
}

# Vérifie bien que c'est un dict
print("Type de Rating_dic :", type(Rating_dic))


# creation d'une nouvelle collone pour mettre cet encodage
# Encodage avec map
df['Rating_Encoded'] = df['Rating'].map(Rating_dic)
print(df['Rating_Encoded'].head())

print("\n")
print("\n")

print("*** 3.3 Encodage One-Hot de 'Division Name' ***\n")

# Encodage One-hot de la variable 'Division Name'
division_ohe = pd.get_dummies(df['Division Name'],prefix='Division')
# Ajout des nouvelles colonnes encodées au DataFrame initial
df = df.join(division_ohe)
print("Encodage One-Hot terminé. Colonnes ajoutées au DataFrame :") # prefix="Division" : pour éviter des noms de
# colonnes ambigus comme juste "General" ou "Intimates".
print(division_ohe.columns.tolist(), "\n") # pour vérifier visuellement les nouvelles colonnes ajoutées.
print("\n")
print("\n")

print("**** 4. Mise à l’échelle des données (StandardScaler) ****")
print("Préparation des données pour le scaling...")

# 1. Colonnes numériques utiles
base_features = ['Recommended_IND_binary', 'Age']  # clothingId exclu

# 2. Colonnes One-Hot
division_ohe_cols = division_ohe.columns.tolist()

# 3. Liste finale
features_to_scale = base_features + division_ohe_cols

# 4. Scaling
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
scaled_array = sc.fit_transform(df[features_to_scale].copy())

# 5. Recréer un DataFrame
df_scaled = pd.DataFrame(scaled_array, columns=features_to_scale, index=df.index)

# 6. Affichage
print("\n✅ Données après mise à l’échelle :")
print(df_scaled.head())

