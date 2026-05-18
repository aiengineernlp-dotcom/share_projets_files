import re # module pour les expressios regulieres
import string
import unicodedata
from unicodedata import category

from nltk import word_tokenize
from nltk.corpus import stopwords
class DatasetCleaner:
    def __init__(self, language):
        # ici on informe le model que on va utiliser les stopwords
        # donc on le regle (set) a la langue qui sera passer a en argument a l'object lors de l'appel de la classe DatasetCleaner
        self.stopwords = set(stopwords.words(language))

        """Normalisation c'est a dire convertir le dataset en minuscule et retrait des accents  """
    def to_lowercase(self,text):
        return text.lower()

    def remove_accents(self,text):
        #Normalization NFD . decompose les carracteres accentues en caractere de base+ accents
        # Puis supprime tous les accents  c'est a dire les caractere de la categories "Mark nonspacing"
        return ''.join(
            c for c in unicodedata.normalize('NFD',text) if category(c) !="Mn" # Pour c dans unicodedata.normalize('NFD',text) si la categorie de c est diffrent de Mn, alors affiche c
        )

    """Nettoyage du dataset c-a-d: retire le html et les ponctuations"""

    def remove_html(self,text):
        # on retire le html avec les expressiosn regulieres
        # on utilise le pattern r'<.*?> qui cherche tout ce qui est compris entre < et >
        return re.sub('r<.*?>','',text)


    def remove_punctuation(self,text):
        # on retire la punctuation avec string.punctuation
        return text.translate(str.maketrans('', '', string.punctuation))

    """Tokenisation"""

    def tokenizer(self,text):
        # ici on decoupe le texte en mots ou phrases que l'on appele token
        return word_tokenize(text)

    def remove_stopwords(self,tokens):
        #filtre les mots vides (articles,prepositions,etc...)
        # qui n'apportent pas de valeur semantique a l'analyse
        return [t for t in tokens if t.lower() not in self.stopwords]



    def clean_pipeline(self,text):
        #ici c'est lexeccution en ordre du nettoya du dataset
        text = self.to_lowercase(text)
        text = self.remove_accents(text)
        text = self.remove_html(text)
        text = self.remove_punctuation(text)
        tokens = self.tokenizer(text)
        tokens = self.remove_stopwords(tokens)
        return tokens


# vu que on veut rendre ce fichier indepandant alors on va faire:

if __name__=="__main__":
    clean = DatasetCleaner('english')
    sample = "J'adore ce produit ! 😍 Livraison <b>rapide</b>, et tres efficace. "
    print(clean.clean_pipeline(sample))  # on appelle la classe, "DatasetCleaner"; on lui applique le pipeline "clean_pipeline" et on met la phrase pour l'exemple qui est 'sample'




