import re
import string
import unicodedata
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords # importation du module qui va permetre a ce que les stopwords soient chargee
from spacy.symbols import punct


class DatasetCleaner:
    def __init__(self, language):
        self.stopwords = set(stopwords.words(language))

    #Normalisation du dataset (convertir en minuscule et retirer les accents)

    def convert_to_lowercase(self,text):
        return text.lower()

    def remove_accents(self,text):
        #On va utiliser la normalisation NFD qui va decomposer le mot en caractere de base + accent et apres retirer les accents
        return ''.join(
            c for c in unicodedata.normalize('NFD',text) if unicodedata.category(c) != "Mn"
        )

    # Nottoyage du dataset (retirer tout le html et retirer la punctuation)

    def remove_html(self,text):
        # on va utiliser les expressions regulierers
        #donc principalement le patern 'r<.*?>' qui va retirer tout de qui se trouvnent entre < et >
        return re.sub('r<.*?>','',text)

    def remove_puntuation(self,text):
        return text.translate(str.maketrans('','',string.punctuation))

    #Tokenization (qui consiste a spliter le texte, et a retirer les stopswords)
    def tokenizer(self,text):
        return word_tokenize(text)

    def remove_stopwords(self,tokens):
        return [t for t in tokens if t.lower() not in self.stopwords]

    '''Enrichissement du prétraitement'''

    """LEMMATISATION/STEMMING c-a-d: pour reduire les mots a leurs racine"""

    def lemmatize(self, tokens):  # a ajouter dans le pipeline
        pass

    """GESTION DES N-GRAMMES c-a-d: pour capturer des expressions multi-mots"""

    def extract_ngrams(self, tokens, n=2):  # a ajouter dans le pipeline
        pass

    '''Fin Enrichissement du prétraitement'''

    """AUTRES c-a-d: les autres methodes  que j'applique a mon Dataset """

    def remove_emojis(self, text):
        # Motif pour détecter les emojis et autres caractères non-ASCII
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symboles & pictogrammes
                                   u"\U0001F680-\U0001F6FF"  # transport & symboles
                                   u"\U0001F700-\U0001F77F"  # symboles alchemiques
                                   u"\U0001F780-\U0001F7FF"  # symboles géométriques
                                   u"\U0001F800-\U0001F8FF"  # symboles supplémentaires
                                   u"\U0001F900-\U0001F9FF"  # symboles supplémentaires
                                   u"\U0001FA00-\U0001FA6F"  # symboles supplémentaires
                                   u"\U0001FA70-\U0001FAFF"  # symboles supplémentaires
                                   u"\U00002702-\U000027B0"  # dingbats
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)

    def correct_spelling(self, text):
        # Corrections des fautes d'orthographes
        pass

    def normalize_entities(self, text):
        # Normalisation des entites (dates, nombres,noms etc...)
        pass

    """EVALUATION Et TEST"""

    def evaluation_cleaning(self, original_text, cleaned_tokens):
        # messure de l'efficassiter du notoyage
        pass

    """PARAMETRE CONTEXTUELL"""

    def add_domain_specific_stopwords(self, domain_stopwords):
        # Ajout des mots vides specifiques aux domaines
        pass

    def clean_pipeline(self,text):
        text = self.convert_to_lowercase(text)
        text = self.remove_accents(text)
        text = self.remove_html(text)
        text = self.remove_puntuation(text)
        tokens = self.tokenizer(text)
        tokens = self.remove_stopwords(tokens)
        return tokens


if __name__ == "__main__":
    clean = DatasetCleaner(language='english')
    sample = "J'adore ce produit ! 😍 Livraison <b>rapide</b>, et tres efficace. "
    print(clean.clean_pipeline(sample))


