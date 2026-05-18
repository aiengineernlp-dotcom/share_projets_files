from collections import Counter

import pandas as pd
from src.preprocessing.dataset_cleaner import DatasetCleaner
import nltk
from tqdm import tqdm

nltk.download("stopwords") # module pour le techargement des mots vides de la langue sugerer

nltk.download("punkt_tab")  #module pour telecharger les regles de Tokenisation

tqdm.pandas() # permet d'afficher une bare de progression lors du traitement des donnees

# j'importe le fichier dataset a traiter grace a pandas car lui il est pour la gestion des donnees
df = pd.read_csv("data/raw/Reviews.csv")

# ----je vais supprimer toutes les lignes vides qui sont dans la colonne 'Text' de mon dataset

df = df.dropna(subset=['Text'])

# je cree une instance de dataset
dataset_cleaner_1 = DatasetCleaner('english')

#j'applique la methode clean a chaque entree de la colonne 'Text'
#
df['cleaned_tokens']  = df["Text"].progress_apply(dataset_cleaner_1.clean_pipeline)


#------- je vais creer le dossier ou sera renger mes resultas
df.to_csv('data/processed/donnees_traitees.csv',index=False)

#afficher les 5 premiere lignes di dataframe avec les colones 'Text' et 'cleaned_tokens'
print(df[["Text","'cleaned_tokens'"]].head(5))

"OPTIONNELLE"

#creer une nouvelle colonne avec les tokens rejoints en une seule chaines

df["cleaned_text"] = df["cleaned_tokens"].apply(lambda tokens: "".join(tokens))


# creer une liste plates de tous les tokens de toutes les lignes
all_tokens = [token for tokens in df["cleaned_tokens"] for token in tokens]

#affiche les 20 mots les plus frequents

print("les 20 mots les plus frequents")

print(Counter(all_tokens).most_common(20))
