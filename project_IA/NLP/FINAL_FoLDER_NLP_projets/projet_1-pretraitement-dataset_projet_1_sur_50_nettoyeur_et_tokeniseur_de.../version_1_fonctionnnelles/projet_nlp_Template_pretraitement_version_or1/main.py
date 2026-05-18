import pandas as pd

from tqdm import tqdm
from collections import Counter
import nltk

from src.preprocessing.dataset_cleaner import DatasetCleaner

nltk.download('stopwords') # Telecharger la liste des mots vides
nltk.download('punkt_tab') # telecharger les regles de tokenisation

"""STEP 0 -  barre de prograssion """
# permet d'afficher la barre de prograssion
tqdm.pandas()

"""STEP 1 -  chargement du fichier brut """
# Chargement du dataset (le fichier csv a traiter)
df = pd.read_csv('./data/raw/Reviews.csv')  # donc on le met dans la variable df= dataframe


"""STEP 2 -  suppression des lignes vides """
#Elimine les lignes ou la colonne 'Text' est vide
df = df.dropna(subset=['Text']) # a partir d'ici mon fichier bruit est pret

"""STEP 3 -  instanciation de DatasetCleaner car on va deja l'utiliser  """
obj_datasetcleaner_1 = DatasetCleaner('english')

"""STEP 4 -  APPLICATION DU  PIPELINE "clean_pipeline" que on a creer dans la classe DatasetCleaner  sur la collonne "Text"  """

# Applique la methode clean_pipeline a chaque entree de la colonne 'Text'
# progress_apply montre une barre de progression pendant le traitement

df["cleaned_tokens"] = df["Text"].progress_apply(obj_datasetcleaner_1.clean_pipeline)  # ici on cree une variable selon
# les regles de pandas, en faisant df["cleaned_tokens"]. puis on  applique
# le PIPELINE<qui est dans la classe< DatasetCleaner representer par
# l'oject 'obj_datasetcleaner_1'< grace a la methode progress_apply()< sur notre dataset qui est "Text".
# --------------/// je crois que avec pandas, vu que il traite les donnees en particulier csv c'est a
# dire dans un fichier excel, le fait que j'ai a
# la notation df["Text"], et que je sais que "Text" est une colonne dans laquelle il ya les donnees,
# veut dire que c'est une variable qui existe deja donc on l'utilise juste.  je fais ce raprochement avec
# le fait que on a creer une collonne nommee df["cleaned_tokens"].
# cette collone est tout simplement comme la cration d'une variable; et le fait que df["Text"] y est directement
# utiliser veut dire que il existe deja c'est a dire deja creer depuis or il est venu avec le dataset
# -----/// Encore plus bas on creer un autre et cette fois on l'appelle exactement colonne. je parle de df["clean_text"]
# --------------//// j'ai l'impressions que ces variables/collonnes sont egalement des listes


"""CLAUDE

Votre raisonnement est très bon ! Je vais clarifier quelques points pour vous aider à mieux comprendre le fonctionnement de pandas.
Vous avez parfaitement raison sur la plupart des aspects :

df["cleaned_tokens"] crée effectivement une nouvelle colonne dans votre DataFrame.
df["Text"] est bien une colonne existante qui contient vos données textuelles d'origine.
.progress_apply(obj_datasetcleaner_1.clean_pipeline) applique votre fonction de nettoyage à chaque élément de la colonne "Text".

Quelques précisions :

Dans pandas, un DataFrame (df) est comme un tableau Excel où les colonnes sont accessibles via 
la notation df["nom_colonne"].
Quand vous écrivez df["cleaned_tokens"] = ..., vous créez une nouvelle colonne si elle n'existe pas déjà, ou vous 
la remplacez si elle existe.
Les colonnes de pandas sont techniquement des Series, qui sont similaires à des listes/arrays mais avec 
des fonctionnalités supplémentaires.
.progress_apply() est une variante de .apply() qui montre une barre de progression 
(fournie par la bibliothèque tqdm) pendant le traitement.
Le clean_pipeline que vous appliquez est probablement une fonction qui nettoie chaque texte individuellement 
(tokenisation, suppression de mots vides, lemmatisation, etc.).

Votre intuition est donc correcte : vous utilisez une colonne existante ("Text") pour créer une nouvelle colonne 
("cleaned_tokens") en appliquant une fonction de transformation à chaque élément.



"""



#Sauvegarde les resultats dans un nouveau fichier CSV

df.to_csv('./data/processed_data/donnees_traitees.csv', index=False)

#Affiche les 5 premiere ligne du dataframe (df) avec les collones 'Text' et cleaned_tokens

print(df[["Text","cleaned_tokens"]].head(5)) # ces crochets : [[]] car on a deux collonnes  "Text" et "cleaned_tokens"


"""OPTIONNELL"""

# creer une nouvelle colone avec les tokens rejoins en une seules chaines
df["clean_text"] = df["cleaned_tokens"].apply(lambda tokens: "".join(tokens))


# cree une liste plate de tous les tokens de toutes les lignes

all_tokens = [token for tokens in df["cleaned_tokens"]for token in tokens]

#affiche les 20 mots les pplus frequents

print("Top 20 mots frequents: ")
print(Counter(all_tokens).most_common(20))

