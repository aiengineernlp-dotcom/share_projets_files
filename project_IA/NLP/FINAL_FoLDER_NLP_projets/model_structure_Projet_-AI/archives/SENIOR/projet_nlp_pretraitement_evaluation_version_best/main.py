import pandas as pd
from scr.preprocessing.dataset_cleaner import DatasetCleaner
from tqdm import tqdm
from collections import Counter
import nltk
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
datasetcleaner_1 = DatasetCleaner('english')

"""STEP 4 -  APPLICATION DU  datasetcleaner_1 sur le PIPELINE  """

# Applique la methode clean a chaque entree de la colonne 'Text'
# progress_apply montre une barre de progression pendant le traitement

df["cleaned_tokens"] = df["Text"].progress_apply(datasetcleaner_1.clean_pipeline)

#Sauvegarde les resultats dans un nouveau fichier CSV

df.to_csv('./data/processed_data/donnees_traitees.csv', index=False)

#Affiche les 5 premiere ligne du dataframe (df) avec les collones 'Text' et cleaned_tokens

print(df[["Text","cleaned_tokens"]].head(5))


"""OPTIONNELL"""

# creer une nouvelle colone avec les tokens rejoins en une seules chaines
df["clean_text"] = df["cleaned_tokens"].apply(lambda tokens: "".join(tokens))


# cree une liste plate de tous les tokens de toutes les lignes

all_tokens = [token for tokens in df["cleaned_tokens"]for token in tokens]

#affiche les 20 mots les pplus frequents

print("Top 20 mots frequents: ")
print(Counter(all_tokens).most_common(20))


