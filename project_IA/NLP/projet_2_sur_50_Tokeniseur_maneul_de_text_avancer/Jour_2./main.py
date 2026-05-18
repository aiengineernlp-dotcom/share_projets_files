from collections import Counter

import pandas as pd
from tqdm import tqdm
import nltk

from src.preprocessing.tokenizer import Tokenizer

nltk.download("stopwords") # pour charger tout les stop words
nltk.download("punkt_tab")# pour charger tou les regles lie a la tokenisation
tqdm.pandas()#  pour gerer la progression lors du traitement du fichier

# step01: j'ouvre et lit le fichier a traiter
df = pd.read_csv('data/raw/Reviews.csv')
#  step02: je supprime toutes les lignes vides qui sont dans la collone que je veux traitee
df = df.dropna(subset=['Text'])

#  step03: je fais appell a mon tokeniseur:  je vais le faire en instanciant la classe ici. c-a-d creer son objet
obj_Tokenizer_1 = Tokenizer('english')
# ici dans le fichier main.py, je ne me pose pas trop de question sur
# la classe DatasetCleaner car il est deja inclut dans ma classe Tokenizer      ::::: est que mon raisonnement est correct?

#step04, je creer une collone qui va recevoir les resultats
df['tokens_cleanned'] = df['Text'].progress_apply(obj_Tokenizer_1.Tokenizer_pipeline)

#step05 : sauvegarde les donnees

df.to_csv('data/processed/reviews_processed.csv',index=False)

#affiche les 5 premiere lignes du dataframe avec les collones 'Text' et 'cleand_tokens'
print(df[["Text","cleaned_tokens"]].head(5))


'''OPtionnel'''

# creer une nouvelle colone avec les tokens rejoins en une seule chaine

df["clean_text"] = df["cleaned_tokens"].apply(lambda tokens:"".join(tokens))

all_tokens = [token for tokens in df["cleaned_tokens"] for token in tokens]
counter = Counter(all_tokens)

print("Top 20 mots frequents: ")
print(Counter(all_tokens).most_common(20))

