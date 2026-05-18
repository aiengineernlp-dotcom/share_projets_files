import friendly_traceback as ft
from matplotlib.lines import lineStyles
from nltk import precision
from torch.utils.flop_counter import suffixes

ft.install(lang="fr")  # ou "en" pour anglais

# import codecademylib3
from tkinter.font import names
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn import tree


"""ANALYSE:  Investigate the data 
#🎯🎯🎯🎯🎯🎯🎯🎯 Préparation des données  ///// data preprocessing ///// l’analyse exploratoire (EDA).  ///// Feature Engineering ou Data Cleaning. //// ➡️ C’est la partie "Data Science" (ou plus précisément, la phase de préparation à l’IA).

✅ Réponse simple :
📊 "Data Science" → avant les print(...)
🤖 "Machine Learning / IA" → commence après ces vérifications
🔄 Reprenons ton idée étape par étape :
📍 1. Tout ce qui vient avant les print(...)

C’est la phase de préparation des données, appelée aussi :

Exploration

Nettoyage

Prétraitement

Encodage des variables

Split train/test

➡️ C’est la partie "Data Science" (ou plus précisément, la phase de préparation à l’IA).

📍 2. Les print(...) de shape
print("X.shape:", X.shape)
print("Y.shape:", Y.shape)
print(x_train.shape, x_test.shape)
print(y_train.shape, y_test.shape)


C’est comme un check-point technique avant de passer au ML.

✅ Si les dimensions sont correctes → tu peux dire que les données sont prêtes pour l'apprentissage.



📍 3. Après ces vérifications :

Tu vas commencer à faire :

Créer un modèle (DecisionTreeClassifier, RandomForest, etc.)

L'entraîner (fit)

Prédire (predict)

Évaluer (accuracy_score, confusion_matrix, etc.)

➡️ C’est là que le Machine Learning / IA commence réellement ✅


✅ Donc oui, tu peux dire :

"Avant les print(...), je fais de la Data Science.
Les print(...) valides, c’est un feu vert pour dire :
✅ Mes données sont prêtes pour le Machine Learning."

Et quand les sorties sont correctes, tu peux dire :

"C’est OK, je peux commencer le ML."

🧠 Petit schéma mental :
[ Exploration + Nettoyage ]
         ↓
[ Encodage, sélection de variables ]
         ↓
[ Split train/test ]
         ↓
✅ print(...shape) ← "Checkpoint OK"
         ↓
🚀 [ ML/IA : entraînement, prédiction, évaluation ]

"""

#https://archive.ics.uci.edu/ml/machine-learning-databases/flags/flag.data
cols=[
'name','landmass','zone', 'area', 'population', 'language','religion','bars','stripes','colours',
'red','green','blue','gold','white','black','orange','mainhue','circles',
'crosses','saltires','quarters','sunstars','crescent','triangle','icon','animate','text','topleft','botright'
]



#variable names to use as predictors
var = [ 'red', 'green', 'blue','gold', 'white', 'black', 'orange', 'mainhue','bars','stripes', 'circles','crosses', 'saltires','quarters','sunstars','triangle','animate']


df = pd.read_csv("../database/flags/flag.data",names=cols)
# the list of the columns
print(df.columns)


# 1- Calcluate the count of flags by landmass value.
print(df['landmass'].value_counts()) # //  1=N.America, 2=S.America, 3=Europe, 4=Africa, 5=Asia, 6=Oceania
print('\n')

# ->> 2 Rather than looking at all six continents, we will focus on just two, Europe and Oceania. Create a new dataframe with only flags from Europe and Oceania.
# New Dataframe with the flags for europe and oceania only. DONC ON VEUT FILTRE

'''creation du masque'''
masque_f_landmass = df['landmass'].isin([3,6])  # ici on a filtrer landmass et mise les valeurs que l'on veut dans 'masque_f_landmass'

'''Creation du nouveau dataFrame europe oceania'''
new_df_e_o = df[masque_f_landmass]

print("---------", new_df_e_o.head())

# ->> 3 Given the list of predictors in the list var, print the average values of each for these two continents. Note which predictors have very different averages

# try:
#     if "landmass" in new_df_e_o.columns and var in new_df_e_o.columns:
#         means = new_df_e_o.groupby("landmass")[var].mean()
#         print("",means.T)
#     else:
#         print("🚩🚩🚩cette collonne n'existe pas ")
#
# except KeyError as e :
#     print(" 🚩🚩🚩The error is ", e)
# except NameError as e:
#     print("🚩🚩🚩The error is ", e)
# except Exception as e:
#     ft.explain_traceback()
#     print("🚩🚩🚩The error is ", e)


'''Transformation numerique de (mainhue) vu que le calcule de la moyenne
 me donne une erreur. Chose normale car on a deux types de donnees dans la liste var.
 
 donc je pass par le value_counts() pour savoir quel type d'encodage appliquer.
 '''
#

# encodage des variables name; mainhue; topleft; botright avec one-hot encoder

'''METHODE 1 -->  appliquer l'encodage'''
# # creer une colonne par mainhue
# mainhue_dummies = pd.get_dummies(new_df_e_o['mainhue'],prefix='mainhue')  #  donc ici chaque "mainhue" sera creer avec soit 0 soit 1
# #ajouter ces colonnes au dataframe
# try:
#     new_df_e_o = new_df_e_o.join(mainhue_dummies)
# except ValueError as e:
#     print('the error is', e)


"""METHODE 2 : filtrer seulement les colonnes catégorielles et appliquer l'encodage"""
# Toutes les colonnes de type object ou category
cat_cols = new_df_e_o[var].select_dtypes(include=['object', 'category']).columns
print("======",cat_cols)

# Filtrer les colonnes numériques dans var
num_cols = new_df_e_o[var].select_dtypes(include='number').columns.tolist()
print("======",num_cols)


# Celles présentes dans var
cat_cols_in_var = [col for col in var if col in cat_cols]
print("======",cat_cols_in_var)


# Séparer les colonnes catégorielles uniquement
cat_cols = new_df_e_o[var].select_dtypes(include=['object', 'category']).columns
# print("======>OutPUT======>>>",cat_cols)
num_cols = new_df_e_o[var].select_dtypes(include=['number']).columns

# encodage uniquement des variables categorielles
dummies = pd.get_dummies(new_df_e_o[cat_cols],prefix=cat_cols, dtype=int)

# Reconstitution du DataFrame avec les colonnes numériques + dummies
data_encoded = pd.concat([new_df_e_o[num_cols],dummies],axis=1)
# Ajouter la colonne de regroupement au DataFrame par exemple continent
data_encoded['continent'] = new_df_e_o['landmass']

# Calcul de la moyenne pour chaque variable encodée, par continent

mean_by_continent = data_encoded.groupby('continent').mean(numeric_only=True)
print(mean_by_continent)
print(mean_by_continent.columns.tolist())

#  4- We will build a classifier to distinguish flags for these two continents – but first, inspect the variable types for each of the predictors.
labels = (new_df_e_o["landmass"].isin([3,6]))*1
"""
Cela crée une série de booléens (True ou False)
C’est une condition logique qui dit : 
Est-ce que la valeur dans landmass est 3 ou 6 ?

Exemple :

Si tu as :

landmass

| landmass |
| -------- |
| 1        |     
| 3        |
| 5        |
| 6        |

Alors :

df["landmass"].isin([3, 6])

[False, True, False, True]


🧩 2. Pourquoi * 1 ?
En Python (et NumPy / pandas), tu peux convertir des True / False en entiers très facilement :

| Booléen | Entier |
| ------- | ------ |
| `True`  | `1`    |
| `False` | `0`    |


Donc quand on écrit :

(df["landmass"].isin([3, 6])) * 1


C’est une astuce rapide pour convertir les True et False en 0 et 1.
C'est équivalent à :

(df["landmass"].isin([3, 6])).astype(int)

Résultat :
[False, True, False, True]  →  [0, 1, 0, 1]


✅ Et ça devient une variable binaire parfaite pour entraîner un classificateur.

🧩 3. Pourquoi on fait ça pour créer Y ?

Parce que tu veux prédire si un drapeau appartient à l’un de deux continents spécifiques :

3 = Amérique du Nord

6 = Océanie

Donc tu transformes le landmass en une variable binaire cible :

1 si le drapeau est en Amérique du Nord ou Océanie

0 sinon

➡️ Cette variable est ton Y, la cible à prédire


✅ Résumé visuel

| landmass | isin([3, 6]) | * 1 | `labels` (Y) |
| -------- | ------------ | --- | ------------ |
| 1        | False        | 0   | 0            |
| 3        | True         | 1   | 1            |
| 5        | False        | 0   | 0            |
| 6        | True         | 1   | 1            |




✅ Pourquoi on garde le reste dans X = data ?

Parce que X doit contenir les colonnes explicatives, donc :

les couleurs

les formes

les symboles

les proportions

etc.

En revanche, Y = labels contient juste la réponse à prédire :

"Ce drapeau est-il en Amérique du Nord ou en Océanie ?"

🧾 TL;DR

(df["landmass"].isin([3, 6])) → produit une série booléenne

* 1 → convertit ça en 0/1 (entiers)

Ce vecteur binaire devient le label Y de ton modèle

Tu cherches à prédire Y à partir de X = data (les caractéristiques du drapeau)



🎓 Règle générale

Quand tu fais un modèle :

X = tout ce que tu connais d’avance (variables explicatives)

Y = ce que tu veux prédire

"""
#  5- Note that all the predictor variables are numeric except for mainhue. Transform the dataset of predictor variables to dummy variables and save this in a new dataframe called data.
data = pd.get_dummies(new_df_e_o[cat_cols], prefix=cat_cols, dtype=int)
print("======>OutPUT======>>>",data.head())

''' 📊 Tableau récapitulatif du comportement de pd.get_dummies()
| **Type de données**                        | **Nombre de modalités** | **Paramètre `columns=` utilisé ?** | **`get_dummies()` l’encode ?** | **Commentaire**                                         |
| ------------------------------------------ | ----------------------- | ---------------------------------- | ------------------------------ | ------------------------------------------------------- |
| `object` (ex: chaînes)                     | Peu ou beaucoup         | ❌ Non                              | ✅ Oui                          | Toujours encodé par défaut                              |
| `category`                                 | Peu ou beaucoup         | ❌ Non                              | ✅ Oui                          | Idem, car c’est déjà catégorisé                         |
| `int` (numérique entier)                   | Beaucoup (ex: âges)     | ❌ Non                              | ❌ Non                          | Ignoré sauf si explicitement précisé                    |
| `int` (ex: 0/1 ou 1/2/3)                   | Peu                     | ❌ Non                              | ❌ Non                          | Aussi ignoré par défaut                                 |
| `int` ou `float`                           | Peu ou beaucoup         | ✅ Oui (ex: `columns=['col']`)      | ✅ Oui                          | Encodé uniquement car explicitement demandé             |
| `float`                                    | Peu ou beaucoup         | ❌ Non                              | ❌ Non                          | Ignoré par défaut                                       |
| `object` contenant chiffres (ex: '1', '2') | Peu ou beaucoup         | ❌ Non                              | ✅ Oui                          | Car c’est du texte, même si ça ressemble à des chiffres |


🧪 Exemples rapides :

✅ Cas encodé :

df = pd.DataFrame({'color': ['red', 'blue', 'green']})
pd.get_dummies(df)

➡️ Résultat : color_blue, color_green, color_red

❌ Cas ignoré :
df = pd.DataFrame({'age': [20, 30, 40]})
pd.get_dummies(df)


➡️ Résultat : rien ne change, car age est numérique

✅ Forçage via columns=... :
df = pd.DataFrame({'code': [1, 2, 1]})
pd.get_dummies(df, columns=['code'])


➡️ Résultat : code_1, code_2

🧾 Résumé en une phrase :

pd.get_dummies() encode automatiquement les colonnes de type object ou category, mais ignore les colonnes numériques (int, float) sauf si tu les spécifies manuellement via columns=.
'''

#=======================================================================================================================

"""
✅ Exemple d’interprétation :

| Variable        | Europe (3) | Océanie (6) | Interprétation                                                                                 |
| --------------- | ---------- | ----------- | ---------------------------------------------------------------------------------------------- |
| `red`           | 0.83       | 0.80        | Le rouge est fréquent dans les deux régions                                                    |
| `mainhue_red`   | 0.49       | 0.30        | En Europe, 49 % des drapeaux ont le rouge comme **couleur principale**, contre 30 % en Océanie |
| `mainhue_white` | 0.29       | 0.00        | Aucun drapeau d’Océanie n’a le blanc comme couleur principale                                  |
| `blue`          | 0.51       | 0.80        | Le bleu est plus courant sur les drapeaux d’Océanie                                            |
| `bars`          | ex: 1.7    | ex: 0.8     | Plus de barres sur les drapeaux européens                                                      |



📊 Et maintenant, que faire avec ça ?

🧠 1. Trouver les variables les plus discriminantes

diff = (mean_by_continent.loc[3] - mean_by_continent.loc[6]).abs()
print(diff.sort_values(ascending=False))
→ Tu obtiens les variables où Europe et Océanie sont le plus différentes.


📈 2. Visualiser avec un barplot

import matplotlib.pyplot as plt

mean_by_continent.T.plot(kind='bar', figsize=(12, 6))
plt.title("Comparaison des moyennes entre Europe et Océanie")
plt.ylabel("Valeur moyenne (ou proportion)")
plt.xlabel("Variables")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()



                            # .T signifie transpose → on échange les lignes et les colonnes
                            # 
                            # Avant .T :
                            # 
                            # Lignes = continents (3, 6)
                            # 
                            # Colonnes = variables (red, blue, etc.)
                            # 
                            # Après .T :
                            # 
                            # Lignes = variables
                            # 
                            # Colonnes = continents
                            # 
                            # ✅ On fait ça pour que chaque variable ait ses propres barres (comparaison visuelle claire entre continents).
                            
                            
                            # .plot(kind='bar', figsize=(12, 6))
                            # .plot() : fonction de Pandas qui utilise Matplotlib pour tracer des graphiques
                            # 
                            # kind='bar' : on veut un bar plot
                            # 
                            # figsize=(12, 6) : largeur = 12, hauteur = 6 (taille de l’image)




📈 2. Visualiser avec un barplot (avancer)

diff = (mean_by_continent.loc[3] - mean_by_continent.loc[6]).abs()
top_diff_vars = diff.sort_values(ascending=False).head(10).index

mean_by_continent[top_diff_vars].T.plot(kind='bar', figsize=(12, 6))
plt.title("Top 10 différences Europe vs Océanie")
plt.ylabel("Moyenne / proportion")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

🤖 3. Créer un modèle simple (par exemple : prédire landmass)

Si tu veux aller vers le machine learning, tu peux entraîner un classifieur sur ces variables pour prédire si un drapeau vient d’Europe ou d’Océanie.

"""

#=======================================================================================================================


"""
✅ Récapitulatif des étapes que tu as faites jusqu’ici :

| Étape                      | Ce que tu as fait                      | Pourquoi c’est important                              |
| -------------------------- | -------------------------------------- | ----------------------------------------------------- |
| 📥 Chargement              | `pd.read_csv()`                        | Obtenir les données dans Python                       |
| 🧼 Filtrage                | Europe + Océanie uniquement            | Se concentrer sur le bon sous-ensemble                |
| 🔢 Sélection des variables | `var = [...]`                          | Choisir les prédicteurs pertinents                    |
| 🔄 Encodage                | `get_dummies()`                        | Transformer les variables catégorielles en numériques |
| 🧠 Analyse exploratoire    | Moyennes par continent, barplots, etc. | Comprendre les tendances & patterns                   |
| 📊 Visualisation           | `plot(kind='bar')`                     | Voir les différences de façon intuitive               |


✅ Ce que tu peux faire maintenant : Passer au Machine Learning

🎯 Objectif typique :

Prédire le continent (Europe vs Océanie) à partir des caractéristiques du drapeau


🚀 Étapes suivantes en ML :

| Étape                                     | Code ou action                                                                    | Objectif                                            |
| ----------------------------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------- |
| 🎯 1. Définir `X` et `y`                  | `X = data_encoded.drop('continent', axis=1)` <br> `y = data_encoded['continent']` | Séparer les features (X) et la cible (y)            |
| 🔀 2. Split                               | `train_test_split(X, y)`                                                          | Avoir un set pour entraîner et un autre pour tester |
| 🤖 3. Choisir un modèle                   | `from sklearn.ensemble import RandomForestClassifier`                             | Choisir un algorithme                               |
| 🧠 4. Entraîner le modèle                 | `model.fit(X_train, y_train)`                                                     | Apprendre à partir des données                      |
| 📈 5. Évaluer                             | `model.score(X_test, y_test)`                                                     | Mesurer la performance                              |
| ✅ 6. (optionnel) Interpréter les features | `model.feature_importances_`                                                      | Voir ce qui influence le plus la prédiction         |



from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Séparer features (X) et cible (y)
X = data_encoded.drop('continent', axis=1)
y = data_encoded['continent']

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Choix du modèle
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Prédiction
y_pred = model.predict(X_test)

# Évaluation
acc = accuracy_score(y_test, y_pred)
print("✅ Accuracy :", acc)


"""



"""REMARQUES"""

"""
#3-the average (mean) values of each for these two continents 

il faut bien voir que c'est la moyenne des sur toutes dans les deux continents. 
Donc on peut changer et passer autres variables que les couleurs par exemple:

Change la variable var :
Exemple 1 : si tu veux calculer la moyenne du nombre de barres :
var = "bars"
means = new_df_e_o.groupby("landmass")[var].mean()


Exemple 2 : moyenne du nombre de couleurs :
var = "colours"
means = new_df_e_o.groupby("landmass")[var].mean()



Condition unique et incontournable: 
    -lorsque on fait dtype sur le dataset, la sortie doit etre tous des entier car la moyenne se fait sur les entiers.
    -Si ce ne sont pas pas les entiers, il faudra faire la transformation de donnees

"""


"""
observation 👀 !

🎯 Ton intention :

Tu veux identifier les colonnes catégorielles (object ou category) dans ton DataFrame, mais seulement parmi les colonnes listées dans var.
Tu fais :
cat_cols = new_df_e_o[var].select_dtypes(include=['object', 'category']).columns
Et tu obtiens une seule colonne, alors que :
new_df_e_o.dtypes
montre trois colonnes de type object.

Ce genre de situation est très courant et vient généralement d’un mismatch subtil entre ce que tu crois sélectionner et ce que le code sélectionne réellement.

"""

# 6-->  Split the data into a train and test set

X = data # donnees transformees
Y = labels # Variable cible





# Vérifie la taille de X et Y
print("X.shape:", X.shape)
print("Y.shape:", Y.shape)

x_train, x_test, y_train, y_test = train_test_split(
    X,
    Y,
    train_size=0.8,
    test_size=0.2,
    random_state=42,
    stratify=Y  # ✅ garde l'équilibre des classes
)

print(x_train.shape, x_test.shape)
print(y_train.shape, y_test.shape)


"""
print("X.shape:", X.shape)
print("Y.shape:", Y.shape)
print(x_train.shape, x_test.shape)
print(y_train.shape, y_test.shape)

VOICI L"EXPLICATION DES SORTIES EN BAS 
                                            X.shape: (55, 6)
                                            Y.shape: (55,)
                                            (44, 6) (11, 6)
                                            (44,) (11,)

| Variable  | Shape     | Explication                                                                                                                   |
| --------- | --------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `X`       | `(55, 6)` | 55 exemples (drapeaux) × 6 variables explicatives (features). C’est ton **jeu de données complet**, après sélection/filtrage. |
| `Y`       | `(55,)`   | 55 labels (valeurs cibles), 1 par exemple. Ici, tu prédis si chaque drapeau est en Amérique du Nord (3) ou en Océanie (6).    |
| `x_train` | `(44, 6)` | 80% de `X` → **44 exemples d'entraînement**, toujours avec 6 features.                                                       |
| `x_test`  | `(11, 6)` | 20% de `X` → **11 exemples de test**, mêmes 6 features.                                                                      |
| `y_train` | `(44,)`   | 44 labels correspondant à `x_train`.                                                                                          |
| `y_test`  | `(11,)`   | 11 labels correspondant à `x_test`.                                                                                           |

✅ Remarques :

Tu as aligné correctement tes données et tes labels — chaque ligne de X a une cible dans Y.

Les proportions 80/20 sont respectées car tu as utilisé train_size=0.8 et test_size=0.2.

Cette structure est maintenant prête pour entraîner un modèle et le tester correctement.



"""

# ❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌


"""
🛠️ Petite vérification (à faire toi-même apres avoir trouver X et Y )

Tu peux vérifier tes shapes :

print(X.shape)  # par exemple (194, 11)
print(Y.shape)  # par exemple (194,)


Et ensuite  apres le split faire:

print(x_train.shape, x_test.shape)
print(y_train.shape, y_test.shape)


➡️ En gros, à quoi ça sert de faire print(X.shape) etc. ?
Voyons ça simplement.

🎯 Pourquoi vérifier .shape ?
📌 Pour s'assurer que :

Les dimensions des données sont correctes

Le découpage train/test s’est bien passé

Les X et Y ont bien le même nombre de lignes (alignement)

Tu n’as pas de données manquantes ou désalignées

🧪 Que représente .shape ?

.shape retourne un tuple :
X.shape → (n_lignes, n_colonnes)
n_lignes : le nombre d’exemples (drapeaux)
n_colonnes : le nombre de variables (couleurs, formes, etc.)


🧾 Exemple avec 194 drapeaux

Imaginons que ton dataset a 194 lignes (drapeaux) et 11 variables :

print(X.shape)      # (194, 11) : 194 drapeaux, 11 features
print(Y.shape)      # (194,)    : 194 labels (0 ou 1)


Puis tu fais un split train/test :

x_train, x_test, y_train, y_test = train_test_split(X, Y, train_size=0.8)

Tu veux voir ça :
print(x_train.shape)  # (155, 11) → 80% de 194
print(x_test.shape)   # (39, 11)  → 20% de 194

print(y_train.shape)  # (155,)
print(y_test.shape)   # (39,)


✅ Tout est cohérent : chaque exemple dans x_train a un label correspondant dans y_train
❌ Si tu ne vérifies pas…

Tu peux facilement avoir des problèmes silencieux comme :

Des dimensions qui ne collent pas (erreurs à l’entraînement du modèle)

Un Y mal aligné avec X

Trop ou pas assez de données dans train ou test

Des colonnes perdues par erreur

✅ Résumé simple

| Vérification                           | À quoi ça sert ?        |
| -------------------------------------- | ----------------------- |
| `X.shape == Y.shape[0]`                | Même nombre d’exemples  |
| `x_train.shape[0] == y_train.shape[0]` | Alignement train        |
| `x_test.shape[0] == y_test.shape[0]`   | Alignement test         |
| `X.shape[1] == x_train.shape[1]`       | Même nombre de features |


🧠 TL;DR

Tu fais print(X.shape) et compagnie pour :

Vérifier la cohérence du split

T'assurer qu’aucune donnée n’a été perdue ou mal formatée

Éviter des bugs plus loin (dans le modèle)

C’est une bonne pratique de base en machine learning ✅

❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌mauvais découpage" (train/test)❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌
Tu veux comprendre à quoi ressemble un "mauvais découpage" (train/test) — c’est super important pour bien préparer tes données avant de construire un modèle.

✅ D'abord, c’est quoi un "bon découpage" ?
Quand tu fais un split train/test, tu veux que :

| Élément          | Train                          | Test                   |
| ---------------- | ------------------------------ | ---------------------- |
| Données (`X`)    | Un sous-ensemble des lignes    | Un autre sous-ensemble |
| Labels (`Y`)     | Alignés avec `X`               | Alignés avec `X`       |
| Proportions      | Correctes (ex: 80% / 20%)      |                        |
| Représentativité | Similaire à l’ensemble complet | Similaire aussi        |


❌ Un "mauvais découpage" = quand une ou plusieurs de ces règles sont cassées
🔴 Cas 1 : X et Y n’ont pas la même taille

X.shape → (194, 11)
Y.shape → (193,)  ❌

➡️ Le modèle va planter car chaque ligne de X doit avoir un label correspondant dans Y.


🔴 Cas 2 : x_train et y_train ne sont pas alignés
x_train.shape → (155, 11)
y_train.shape → (154,)  ❌


➡️ Ici aussi, une erreur apparaîtra pendant l'entraînement car les exemples et les étiquettes ne sont pas appariés.

🔴 Cas 3 : Tu ne fais pas de shuffle (shuffle=False par erreur)

Imagine que les données sont triées par continent dans ton DataFrame.
Si tu fais :

train_test_split(X, Y, shuffle=False)


➡️ Tu risques d’avoir tous les drapeaux d’Amérique dans le train, et tous ceux d’Océanie dans le test.

❌ Résultat : ton modèle n’a jamais vu l’Océanie pendant l’entraînement
→ Il sera nul sur le test.

🔴 Cas 4 : Taille du test trop petite
train_test_split(X, Y, test_size=0.01)


➡️ Test = seulement 1 ou 2 exemples → pas du tout fiable pour mesurer la performance

🔴 Cas 5 : Classement déséquilibré entre train et test

Par exemple :

Tu veux classifier entre classes 0 et 1

Mais le train contient 90% de classe 0 et 10% de classe 1

Et le test contient 50% de chaque

➡️ ❌ Le modèle est biaisé : il a appris un déséquilibre qui ne reflète pas la réalité du test

Pour éviter ça, on utilise souvent stratify=Y

train_test_split(X, Y, test_size=0.2, stratify=Y)

✅ En résumé : tableau des erreurs fréquentes
| Erreur                         | Symptôme               | Impact                                      |
| ------------------------------ | ---------------------- | ------------------------------------------- |
| `X` et `Y` mal alignés         | `.shape` différents    | Crash ou erreur                             |
| Trop peu de test               | `test_size` trop petit | Évaluation peu fiable                       |
| Shuffle désactivé              | `shuffle=False`        | Sur-apprentissage / mauvaise généralisation |
| Déséquilibre des classes       | Pas de `stratify=Y`    | Modèle biaisé                               |
| Trop peu de données tout court | < 100 lignes           | Résultats non stables                       |

🛠️ Que faire pour bien découper ?

from sklearn.model_selection import train_test_split

x_train, x_test, y_train, y_test = train_test_split(
    X, Y,
    test_size=0.2,
    random_state=42,
    stratify=Y,  # ⚠️ si Y est binaire ou déséquilibré
)

# Vérification
print(f"X: {X.shape}, Y: {Y.shape}")
print(f"x_train: {x_train.shape}, y_train: {y_train.shape}")
print(f"x_test: {x_test.shape}, y_test: {y_test.shape}")


❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌

| Paramètre      | Ce qu’il signifie                                            | Exemple        |
| -------------- | ------------------------------------------------------------ | -------------- |
| `test_size`    | Proportion (ou nombre) pour **test**                         | `0.2` → 20%    |
| `train_size`   | Proportion (ou nombre) pour **train**                        | `0.8` → 80%    |
| `random_state` | Pour reproduire les mêmes splits                             | `42` (souvent) |
| `stratify`     | Pour garder les mêmes proportions de classes dans train/test | `Y`            |


x_train, x_test, y_train, y_test = train_test_split(
    X, Y,
    test_size=0.2,
    train_size=0.8,
    random_state=42,
    stratify=Y
)

| Paramètre      | Sert à…                                                       |
| -------------- | ------------------------------------------------------------- |
| `X, Y`         | Données et labels                                             |
| `train_size`   | Proportion (ou nombre) de données pour l’entraînement         |
| `test_size`    | Proportion (ou nombre) de données pour le test                |
| `random_state` | Pour avoir le **même split à chaque fois**                    |
| `stratify=Y`   | Pour garder **même proportion de classes** dans train et test |

| Question                                                  | Réponse                                 |
| --------------------------------------------------------- | --------------------------------------- |
| Peut-on mettre les 4 paramètres ?                         | ✅ Oui                                  |
| Faut-il que `train_size + test_size ≤ 1` ?                | ✅ Absolument                            |
| Est-ce que `stratify` et `random_state` posent problème ? | ❌ Pas du tout, ils sont sûrs à utiliser |

Oui, tu peux mettre les 4 paramètres à condition que train_size + test_size ≤ 1.

Et dans ce cas précis (0.8 + 0.2 = 1), ça fonctionne parfaitement ✅
"""





#=======================================================================================================================
#=======================================================================================================================
#===========================================TOUTE LA PARTIE DU HAUT EST L"ANALYSE DES DONNEES===========================
#=======================================================================================================================
#=======================================================================================================================


#🎯🎯🎯🎯🎯🎯🎯🎯 Decision Tree Classifiers by Depth


"""🎯 Alors c’est quoi le Machine Learning ?"""

"""
est ce que le model creer c'est deja l'ia ? ou est ce le model IA ?

🧠 Réponse courte :

🔹 Le modèle que tu crées avec scikit-learn est un modèle de Machine Learning.
🔹 Ce n’est pas une IA au sens complet, mais c’est une brique de l’IA.

🎯 Définissons les termes simplement

| Terme                              | Définition                                                                                                                                      | Exemple                                    |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| **IA (Intelligence Artificielle)** | Domaine global qui cherche à donner à une machine la capacité de **simuler un comportement intelligent** (raisonner, décider, comprendre, etc.) | ChatGPT, voiture autonome, assistant vocal |
| **Machine Learning (ML)**          | Sous-domaine de l’IA qui permet à une machine d’**apprendre à partir de données**, sans être explicitement programmée                           | Arbre de décision, régression, SVM         |
| **Modèle de ML**                   | Objet entraîné pour **faire une tâche précise** (prédiction, classification)                                                                    | Un `DecisionTreeClassifier()` entraîné     |


✅ Donc : ce que tu fais avec scikit-learn, c’est :

Créer un modèle de ML

Entraîner ce modèle avec des données

Utiliser ce modèle pour automatiser une tâche intelligente (comme prédire un continent à partir d’un drapeau)

➡️ Tu peux dire que :

👉 "Je construis un système simple d’IA basé sur le Machine Learning."

Mais le modèle lui-même (ex : un arbre de décision) n’est pas une "IA complète" — c’est un composant d’IA.

🧪 Analogie :

Un moteur n’est pas une voiture, mais il fait partie de la voiture.

Un modèle de ML n’est pas une IA complète, mais il en est le cœur.


✅ En résumé

| Tu peux dire…                           | C’est correct ?                      |
| --------------------------------------- | ------------------------------------ |
| "Je crée un modèle IA"                  | ✅ Acceptable dans le langage courant |
| "Je crée un modèle de Machine Learning" | ✅ Plus précis techniquement          |
| "Le modèle seul est une IA complète"    | ❌ Pas vraiment (trop réducteur)      |
| "Je construis une brique d’IA"          | ✅ Oui, exactement ça !               |


Voici une mini-carte mentale simple et claire pour t’aider à visualiser comment IA, Machine Learning et modèle sont liés 👇

🧠 Carte mentale : IA → ML → Modèle → Application

🎯 INTELLIGENCE ARTIFICIELLE (IA)
│
├── 🤖 Machine Learning (ML)
│   │
│   ├── 📦 Modèle de ML
│   │   ├── Exemple : DecisionTreeClassifier, RandomForest
│   │   └── Fonction : Apprendre à partir de données
│   │
│   └── 📊 Données d'entraînement
│       ├── Features (X)
│       └── Labels (Y)
│
└── 🛠️ Autres domaines de l'IA
    ├── Traitement du langage (NLP)
    ├── Vision par ordinateur
    ├── Raisonnement logique
    └── Planification autonome

🧩 Exemple dans ton projet "Flags"

| Niveau      | Exemple concret                                                        |
| ----------- | ---------------------------------------------------------------------- |
| IA          | Distinguer les continents à partir des couleurs et formes des drapeaux |
| ML          | Classifier les drapeaux selon `landmass` (continent)                   |
| Modèle      | `DecisionTreeClassifier()` entraîné sur `X_train`, `y_train`           |
| Application | Prédire le continent d’un nouveau drapeau jamais vu                    |



❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌❌

le Traitement du langage (NLP) et le ML marche ensemble ?
Le traitement du langage naturel (NLP) et le machine learning (ML) travaillent souvent ensemble — et même, aujourd’hui, ils sont presque inséparables.

✅ Réponse courte

Le NLP utilise le Machine Learning pour comprendre, analyser, traduire ou générer du texte.

Sans ML, le NLP moderne ne serait pas aussi puissant qu’il l’est aujourd’hui (ex : ChatGPT, Google Translate, assistants vocaux…).

🧠 Expliquons simplement :


| Domaine                               | Rôle                                                          |
| ------------------------------------- | ------------------------------------------------------------- |
| **NLP** (Natural Language Processing) | Comprendre et traiter **le langage humain** (texte ou parole) |
| **ML** (Machine Learning)             | Apprendre à faire une tâche **à partir de données**           |


➡️ Le NLP est le quoi (ex : analyser un texte),
➡️ Le ML est le comment (ex : entraîner un modèle qui sait le faire)

🧪 Exemples où NLP et ML travaillent ensemble :

| Tâche NLP                             | Ce que fait le ML                            |
| ------------------------------------- | -------------------------------------------- |
| Classifier un texte (spam / pas spam) | Entraîner un modèle avec des exemples        |
| Traduire une langue                   | Utiliser un modèle séquence-à-séquence       |
| Résumer un texte                      | Apprendre à générer des résumés automatiques |
| Identifier les émotions               | Modèle entraîné à reconnaître des sentiments |
| Chatbots / assistants IA              | Modèles de ML génératifs comme GPT           |


🎯 Donc, on peut dire :

| Ce que tu veux dire                | Est-ce correct ?                                   |
| ---------------------------------- | -------------------------------------------------- |
| "Le NLP utilise le ML"             | ✅ Oui                                              |
| "Le ML aide à comprendre le texte" | ✅ Oui                                              |
| "NLP et ML marchent ensemble"      | ✅ Oui                                              |
| "NLP = ML"                         | ❌ Non (NLP est plus large, ML est un outil dedans) |


💡 Petit schéma visuel :
🧠 NLP (le langage humain)
   ├── Utilise → 🤖 Machine Learning
   │       └── Utilise → 📊 Données textuelles
   │               └── Donne → 🧾 Modèle entraîné
   └── Sert à → Traduire, classer, résumer, discuter, etc.


"""
#Le machine learning, c’est quand tu passes à l’étape suivante :
    #Utiliser tes données préparées pour entraîner un modèle qui apprend à prédire une variable cible.





"""Tune Decision Tree Classifiers by Depth"""



#question 7 Fit a decision tree classifier for max_depth values from 1-20.

max_depth  = range(1,21)
acc_depth = []

for p in max_depth:
    arbre = DecisionTreeClassifier(max_depth=p,random_state=42)
    arbre.fit(x_train,y_train)
    acc = arbre.score(x_test,y_test)
    acc_depth.append(acc)
    # print(acc_depth)

for p,a in zip(max_depth,acc_depth):
    print(f" profondeur: {p} ---> accuracy: {a:.2f}")


#question 8 Plot the accuracy of the decision tree models versus the max_depth

plt.figure(figsize=(10,5))
plt.plot(acc_depth,max_depth,marker="o",linestyle="-",color="b")
plt.xlabel("les precisions (acc_depth)", )
plt.ylabel("profondeur de l'arbre (max_depth)")
plt.title("Accuracy of the decision tree models versus the max_depth")
plt.grid(True)
# plt.show()


#question 9.Find the largest accuracy and the depth this occurs.

print("initial list  accuracy: ",acc_depth)
print("initial list profondeur: ",max_depth)

#9-1   largest accuracy
max_acc = max (acc_depth)
depth_max = max(max_depth)
print("Accuracy Maximale est:",max_acc)
print("Profondeur Maximale est (profondeur):",depth_max)

#9.2 Trouver la/les profondueurs correspondantes a l'accuracy maximale

best_depths = [d for d,a in zip(max_depth,acc_depth) if a==max_acc]
print(f"L'accuracy maximale est {max_acc:.2f}, obtenue pour profondeur(s) : {best_depths}")

#9.3 Trouver l'accuracy minimal
min_acc = min(acc_depth)
print("Accuracy Minimale est : ",min_acc)
#9.4 Trouver la/les profondueurs correspondantes a l'accuracy Minimale

worst_depths = [d for d,a in zip(max_depth,acc_depth) if a == min_acc]
# print(worst_depths)
print(f"L'accuracy minimale est {min_acc:2f},obtenue pour les profondeurs: {worst_depths}")


#10 Refit the decision tree model using the max_depth from above
#10-1 creation du model
arbre_refit = DecisionTreeClassifier(max_depth=depth_max,random_state=42)
#10-2 #entrainement
arbre_refit.fit(x_train,y_train)
#10-3 plot the tree


plt.figure(figsize=(10,5))
plot_tree(arbre_refit,feature_names=X.columns,  # noms des colonnes (tes prédicteurs)
          class_names=["Océanie", "Europe"],  # tes labels
    filled=True,
    rounded=True)
plt.grid(True)
# plt.show()




"""Tune Decision Tree Classifiers by Pruning"""
#question 11:  Fit a decision tree classifier for each value in ccp

path = DecisionTreeClassifier(random_state=42).cost_complexity_pruning_path(x_train,y_train)
ccp_alphas = path.ccp_alphas
print("\n")
acc_pruned = []

for alpha in ccp_alphas:
    modele = DecisionTreeClassifier(random_state=42,ccp_alpha=alpha)
    modele.fit(x_train,y_train)
    acc_score = modele.score(x_test,y_test)
    acc_pruned.append(acc_score)


#question 12:
plt.figure(figsize=(10, 5))
plt.plot(ccp_alphas, acc_pruned, marker='o')
plt.xlabel("ccp_alpha")
plt.ylabel("Accuracy on Test Set")
plt.title("Accuracy vs CCP Alpha for Pruned Decision Trees")

"""
🔍 Interprétation de la consigne :

"Plot the accuracy of the decision tree models versus the ccp_alpha."

La phrase “A versus B” en anglais signifie généralement :

X-axis : B
Y-axis : A

Donc ici :

X-axis : ccp_alpha

Y-axis : accuracy



| Formulation       | Axe X     | Axe Y       |
| ----------------- | --------- | ----------- |
| A vs B            | B (cause) | A (effet)   |
| Accuracy vs Alpha | Alpha     | Accuracy    |
| Price vs Size     | Size      | Price       |
| Temp vs Time      | Time      | Temperature |


🤓 Pourquoi cette convention ?

C’est parce qu’en science (et en programmation comme ici), on met souvent la variable indépendante (ce qu’on contrôle ou modifie) sur l’axe X, et la variable dépendante (le résultat ou effet) sur l’axe Y.

Donc :
ccp_alpha = paramètre qu’on choisit → axe X
accuracy = performance mesurée après entraînement → axe Y

"""
plt.grid(True)
# plt.show()


# question 13 Find the largest accuracy and the ccp_alpha value this occurs.
largest_accurracy = max(acc_pruned)
best_index = acc_pruned.index(largest_accurracy)
print(largest_accurracy)
print(best_index)


# Question 14: Fit a decision tree model with the values for max_depth and ccp_alpha found above. Plot the final decision tree.

modele_final = DecisionTreeClassifier(max_depth=20,ccp_alpha=best_index)
modele_final.fit(x_train,y_train)

plt.figure(figsize=(10,5))
plot_tree(modele_final,feature_names=x_train.columns, # si tu as des noms de colonnes
          class_names=[str(c) for c in y_train.unique()],#  # noms des classes
          )

plt.show()




"""
15.
Nice work! Note that the accuracy of our final model increased and the structure of the tree was simpler – many unnecessary branches were removed in the pruning process making for a much easier interpretation.

There are a few different ways to extend this project:

Try to classify something else! Rather than predicting the "Landmass" feature, could predict something like the "Language"?
Find a subset of features that work better than what we’re currently using. An important note is that a feature that has categorical data won’t work very well as a feature. For example, we don’t want a decision node to split nodes based on whether the value for "Language" is above or below 5.
Tune more parameters of the model. You can find a description of all the parameters you can tune in the Decision Tree Classifier documentation. For example, see what happens if you tune max_leaf_nodes. Think about whether you would be overfitting or underfitting the data based on how many leaf nodes you allow.


"""