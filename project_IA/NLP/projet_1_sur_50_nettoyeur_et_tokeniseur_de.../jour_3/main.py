from collections import Counter

import pandas as pd
import nltk
from src.pretraitement.dataset_cleaner import DatasetCleaner

nltk.download('punkt_tab') # telecharge les regles de tokenisations
nltk.download('stopwords') # telecharde la liste des stopwords
from tqdm import tqdm

tqdm.pandas() # me permet de voir la progression  des traitements des donnees

#recevoir et lire le fichier dataset qui va etre utiliser pour le traitement
df = pd.read_csv('data/raw/Reviews.csv')

# retirer les ligne qui sont vide dans la colonne "Text" de mon dataset

df = df.dropna(subset=["Text"]) #a partir d'ici mon fichier  brut est pret

#instanciation de la classe/ creation de mon object
dataset_cleaner_1 = DatasetCleaner ('english')

df['cleaned_tokens']  = df["Text"].progress_apply(dataset_cleaner_1.clean_pipeline)

# je sauvegarde les resultats dans un nouveau fichier:

df.to_csv('data/prosseced/Reviews_prosseced.csv',index=False)

# affiche les 5 premieres ligne du dataframe

print(df[["Text",'cleaned_tokens']].head(5))

"""OPTIONNELL"""

#Creer une nouvelle collonnes avec les tokens rejoins en une seule chaine

df["all_text"] = df["cleaned_tokens"].apply(lambda tokens:"".join(tokens))


# creer une liste plate pour touts les tokens de toutes les lignes

all_tokens = [token for tokens in df["cleaned_tokens"] for token in tokens]


# afficher les 20 mots les plus frequents

print("afficher les 20 mots les plus frequents")

print(Counter(all_tokens).most_common(20))