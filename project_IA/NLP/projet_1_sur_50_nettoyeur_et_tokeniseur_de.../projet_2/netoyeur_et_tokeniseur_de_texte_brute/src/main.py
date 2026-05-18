
import pandas as pd
from text_cleaner import TextCleaner
from tqdm import tqdm
from collections import Counter
import nltk
nltk.download('stopwords')
nltk.download('punkt_tab')

# pour mettre la barre de progresseion avec tqdm
tqdm.pandas()

#charger le fichier CSV
df = pd.read_csv("../data/raw/Reviews.csv")

#Supprimer les lignes avec les valeurs manquantes dans le 'Text'
df = df.dropna(subset=["Text"])

#Initialiser le nettoyeur
cleaner = TextCleaner(language='french')

#Appliquer le nettoyage sur la collonne 'Text'
df["cleaned_tokens"] = df["Text"].progress_apply(cleaner.clean)

#Sauvegarder les resultats
df.to_csv("../data/procceded/procceded_amazon_reviews.csv",index=False)

#afficher un exemple
print(df[["Text", "cleaned_tokens"]].head(5))



'''OPTIONELLE'''
# ajouter la collonne cleaned_text
df["cleaned_text"]  = df ["cleaned_tokens"].apply(lambda tokens: "".join(tokens))

# Afficher les top 20 mots les plus frequents

all_tokens = [token for tokens in df["cleaned_tokens"] for token in tokens]

print("Top 20 mots frequents : ")
print(Counter.most_common(20))

#return [t for t in tokens if t.lower() not in self.stopwords]  je le lis que : pour t in tokens affiche dans une liste [t] si t.lower() n'est pas dans self.stopwords
