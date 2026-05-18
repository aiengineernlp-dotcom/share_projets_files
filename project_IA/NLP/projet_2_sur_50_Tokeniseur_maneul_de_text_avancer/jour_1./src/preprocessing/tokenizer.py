import re
from nltk.corpus import stopwords
from nltk import word_tokenize
import pandas as pd
from src.preprocessing.cleaner import CleanDataset
from tqdm import tqdm
tqdm.pandas()

class Tokenizer:
    """
    Classe responsable de la tokenisation de texte :
    - Nettoie le texte via la classe CleanDataset
    - Applique une méthode de tokenisation (split, regex, nltk)
    - Supprime les stopwords
    """
    def __init__(self,language):
        """
        Initialise le tokenizer avec une langue pour les stopwords
        et instancie la classe de nettoyage.
        """
        self.stopwords = set(stopwords.words(language))
        self.obj_CleanDataset_1 = CleanDataset('english')

        # On instancie CleanDataset pour pouvoir appeler ses méthodes de nettoyage dans cette classe


    def methode_avec_split(self,text):
        # la plus simple methode avec split()
        return text.split()

    def methode_avec_re_find_all(self,text):
        #la methode moyenne avec refindall()
        return re.findall(r'\w+',text)

    def methode_avec_nltk(self,text):
        #la methode plus avancer ici:
        return word_tokenize(text)

    def remove_stopwords(self,tokens):
        return [t for t in tokens if t.lower() not in self.stopwords]


    def tokeniser_pipeline(self,text):
        """
        Applique un pipeline complet de traitement sur un texte :
        1. Nettoyage (lowercase, accents, HTML, ponctuation)
        2. Tokenisation (via nltk)
        3. Suppression des stopwords

        Args:
            text (str): Texte brut à traiter

        Returns:
            list: Liste de tokens nettoyés
        """
        text = self.obj_CleanDataset_1.clean_pipeline(text) #
        #j'ecris cette ligne parceque avant de faire la tokenisation
        # on a besoin du texte traiter au moins partiellement c'est ce qui a ete fait dans le fichier cleaner.py
        # je met text ici car dans le fichier cleaner.py, on passe
        # un parametre text. je veux note que j'ai importer clean_pipeline de la methode CleanDataset du
        # fichier cleaner
        tokens = self.methode_avec_nltk(text)   # je met cette ligne car je veux travailler
        # avec la methode_avec_nltk dans un premier temps pour la tokenisation
        tokens = self.remove_stopwords(tokens)
        return tokens


if __name__=='__main__':
    tokeniser = Tokenizer('english')
    df = pd.read_csv('../../data/raw/Reviews.csv')
    df = df.dropna(subset=['Text'])
    df['tokens'] = df['Text'].progress_apply(tokeniser.tokeniser_pipeline)
    df.to_csv('../../data/processed/Reviews_processed.csv')
    print(df[['Text','tokens']].head(20))







    """
    
Si tu veux aller plus loin :

Ajouter une colonne clean_text (texte nettoyé sans tokenisation).

Gérer les erreurs dans les lignes corrompues (try/except dans la fonction).

Ajouter une CLI ou un notebook pour tester interactivement.
    """


