from collections import Counter
import pandas as pd # pour la manipulation des fichiers .csv
from src.preprocessing import cleaner

from tqdm import tqdm  # pour afficher la barre de progression

"""STEP 0 -  barre de prograssion """
print("Start Processing......")
tqdm.pandas() # Permet d'afficher une barre de progression lors du traitement du Dataset

"""STEP 1 -  chargement du fichier brut """
df = pd.read_csv('data/raw/Reviews.csv') # je lis le fichier csv

"""STEP 2 -  suppression des lignes vides """
df = df.dropna(subset=['Text']) #Elimine les lignes ou la colonne 'Text' est vide

"""STEP 3 -  instanciation/creation dune instance de classe: le DatasetCleaner car on va deja l'utiliser  """
obj_DatasetCleaner_1 = cleaner.DatasetCleaner(language='english')

"""STEP 4 -  APPLICATION DU  PIPELINE "DatasetCleaner_pipeline" que on a creer dans la classe DatasetCleaner  sur la collonne "Text"  """
# Application de la methode "DatasetCleaner_pipeline" a CHAQUE ENTREE de la colonne de "Text"
# progress_apply montre une barre de progression pendant le traitement

#df["Cleaned_Tokens"] = (obj_DatasetCleaner_1.DatasetCleaner_pipeline(df["Text"])) # est ce bon?

df["Cleaned_Tokens"] = df["Text"].progress_apply(obj_DatasetCleaner_1.DatasetCleaner_pipeline)
# ici on cree une variable selon la syntax de pandas en faisant : df["Cleaned_Tokens"] qui est une nouvelle colonne
# devant recevoir les donnes traitees
#
# puis on commence:
# On appelle les donnees/collones a traiter qui est:  df["Text"] ensuite,
# On appelle la barre de progression avec: .progress_apply
# Enfin on appelle la Pipeline DatasetCleaner_pipeline() depuis le fichier cleaner


'''
EXPLICATION SUPPLEMENTAIRES
  # ici on cree une variable selon
# les regles de pandas, en faisant df["Cleaned_Tokens"]. puis on  applique
# le PIPELINE<qui est dans la classe< DatasetCleaner representer par
# l'oject 'obj_datasetcleaner_1'< grace a la methode progress_apply()< sur notre dataset qui est "dataset".
# --------------/// je crois que avec pandas, vu que il traite les donnees en particulier csv c'est a
# dire dans un fichier excel, le fait que j'ai a
# la notation df["Text"], et que je sais que "Text" est une colonne dans laquelle il ya les donnees,
# veut dire que c'est une variable qui existe deja donc on l'utilise juste.  je fais ce raprochement avec
# le fait que on a creer une collonne nommee df["Cleaned_Tokens"].
# cette collone est tout simplement comme la cration d'une variable; et le fait que df["Text"] y est directement
# utiliser veut dire que il existe deja c'est a dire deja creer depuis or il est venu avec le dataset
# -----/// Encore plus bas on creer un autre et cette fois on l'appelle exactement colonne. je parle de df["clean_text"]
# --------------//// j'ai l'impressions que ces variables/collonnes sont egalement des listes

'''

"""CLAUDE

Votre raisonnement est très bon ! Je vais clarifier quelques points pour vous aider à mieux comprendre le fonctionnement de pandas.
Vous avez parfaitement raison sur la plupart des aspects :

df["Cleaned_Tokens"] crée effectivement une nouvelle colonne dans votre DataFrame.
df["Text"] est bien une colonne existante qui contient vos données textuelles d'origine.
.progress_apply(obj_datasetcleaner_1.clean_pipeline) applique votre fonction de nettoyage à chaque élément de la colonne "Text".

Quelques précisions :

Dans pandas, un DataFrame (df) est comme un tableau Excel où les colonnes sont accessibles via 
la notation df["nom_colonne"].
Quand vous écrivez df["Cleaned_Tokens"] = ..., vous créez une nouvelle colonne si elle n'existe pas déjà, ou vous 
la remplacez si elle existe.
Les colonnes de pandas sont techniquement des Series, qui sont similaires à des listes/arrays mais avec 
des fonctionnalités supplémentaires.
.progress_apply() est une variante de .apply() qui montre une barre de progression 
(fournie par la bibliothèque tqdm) pendant le traitement.
Le clean_pipeline que vous appliquez est probablement une fonction qui nettoie chaque texte individuellement 
(tokenisation, suppression de mots vides, lemmatisation, etc.).

Votre intuition est donc correcte : vous utilisez une colonne existante ("Text") pour créer une nouvelle colonne 
("Cleaned_Tokens") en appliquant une fonction de transformation à chaque élément.

"""

"""STEP 5 -  Sauvegarde les resultats dans un nouveau fichier CSV"""
df.to_csv('data/processed/processed_amazone.csv',index=False)


"""OPTIONNELL"""
""" 0-1 - Affiche les 5 premieres ligne du dataframe avec les colones 'Text' et 'Cleaned_Tokens' """
print(df[['Text','Cleaned_Tokens']].head(5))
#print(df['Text'].head(5),df['Cleaned_Tokens'].head(5)) valable mais duplication
#print(df['Text'])

"""0-2 - Cree une nouvelle colonne avec les tokens rejoins en une seule chaine """
df ["cleaned_text"] = df['Cleaned_Tokens'].apply(lambda tokens: " ".join(tokens)) # ici donc on lie tous les tokens nottoyer
# sur une seule chaine comme si on avait fait une phrase. et a partir dela on peut faire une analyse du contenu

"""0-3 - ici on cree une liste plate de tous les tokens de toutes les lignes """
all_tokens =[token for tokens in df['Cleaned_Tokens'] for token in tokens]  # est ce une facon
# de sortir les tokens de la colonne df['Cleaned_Tokens'] avant de les afficher???

# car je comprend que ici on fait :
#- pour les "tokens" qui sont dans df['Cleaned_Tokens'],   --->> on recupere les tokens de la colonnes df['Cleaned_Tokens']
#- pour 'token' in tokens --->> ici on affiche les token qui se trouvent dans tokens, recuperer dans df['Cleaned_Tokens'] .

'''
CLAUDE:
all_tokens = [token for tokens in df['Cleaned_Tokens'] for token in tokens]
Décomposition étape par étape :

1. for tokens in df['Cleaned_Tokens'] : 
    .On parcourt chaque élément de la colonne df['Cleaned_Tokens']
    .Chaque élément tokens est une liste de mots (ex: ['adore', 'produit', 'livraison'])
    
2. for token in tokens 
    .Pour chaque liste tokens, on parcourt chaque mot individuel token
    .On "déplie" chaque liste pour extraire les mots un par un
    
3. token
    .C'est ce qu'on collecte dans la nouvelle liste c'est a dire all_tokens[] : chaque mot individuel



Exemple concret
    Supposons que df['Cleaned_Tokens'] contient :
    
    df['Cleaned_Tokens'] = [
    ['adore', 'produit', 'livraison'],      # Ligne 1
    ['tres', 'efficace', 'rapide'],         # Ligne 2
    ['excellent', 'service']                # Ligne 3
]

La list comprehension va faire :

# Étape 1: tokens = ['adore', 'produit', 'livraison']
#   → token = 'adore', puis 'produit', puis 'livraison'

# Étape 2: tokens = ['tres', 'efficace', 'rapide']
#   → token = 'tres', puis 'efficace', puis 'rapide'

# Étape 3: tokens = ['excellent', 'service']
#   → token = 'excellent', puis 'service'

# Résultat final :
all_tokens = ['adore', 'produit', 'livraison', 'tres', 'efficace', 'rapide', 'excellent', 'service']


Équivalent avec des boucles classiques
Cette list comprehension est équivalente à :

all_tokens = []
for tokens in df['Cleaned_Tokens']:      # Pour chaque ligne
    for token in tokens:                 # Pour chaque mot dans la ligne
        all_tokens.append(token)         # Ajouter le mot à la liste finale
        
        
C'est exactement ce que fait la ligne suivante dans votre code :
    Counter(all_tokens).most_common(20)  # Trouve les 20 mots les plus fréquents

'''




"""0-4 - afficher les 20 mots les plus frequents """
print("Top 20 mots frequents")
print(Counter(all_tokens).most_common(20))