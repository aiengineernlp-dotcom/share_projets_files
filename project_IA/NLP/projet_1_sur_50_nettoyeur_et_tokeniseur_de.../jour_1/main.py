from collections import Counter
import pandas as pd
from src.text_cleaner import TextCleaner
from tqdm import tqdm
import nltk
nltk.download('stopwords')
nltk.download('punkt')


#La barre de progressions lors du traitement des donnees
tqdm.pandas()

#charger le fichier CSV contenant les avis
df = pd.read_csv("data/raw/Reviews.csv")

#Supprimer les lignes qui sont vides dans le fichier csv dans la colonne 'Text'
df = df.dropna(subset=["Text"])

# cree une instance de TextCleaner
cleaner_1 = TextCleaner(language='english')


df ["cleaned_tokens"] = df ["Text"].progress_apply(cleaner_1.clean)


#Sauvegarder les data dans un fichier
df.to_csv("data/processed_data/processed_data.csv", index=False)

#affiche les 5 premiere lignes du dataframe avec les collones 'Text' et 'cleand_tokens'
print(df[["Text","cleaned_tokens"]].head(5))


'''OPtionnel'''

# creer une nouvelle colone avec les tokens rejoins en une seule chaine

df["clean_text"] = df["cleaned_tokens"].apply(lambda tokens:"".join(tokens))

all_tokens = [token for tokens in df["cleaned_tokens"] for token in tokens]
counter = Counter(all_tokens)

print("Top 20 mots frequents: ")
print(Counter(all_tokens).most_common(20))




