import re
import string
import unicodedata

from nltk import word_tokenize
from nltk.corpus import stopwords
class CleanDataset:
    def __init__(self,language):
        self.stopwords = set(stopwords.words(language))

    "NORMALIZATION (lowercase and accents)"
    def convert_to_lower_case(self,text):
        # convertir en miniscule car apres le traitement e l'analyse sera plus facile
        return text.lower()

    def remove_accents(self,text):
        # ICi on applique la normalisation NFD. qui consite a decomposer les mots avec accents en les
        # cassant et en les mettant quote a cote puis a retier les accents
        return ''.join(
            # pour tous les mots cote a cote c'est dire join, suivant la normalisation NFD,
            # il ne faut afficher que les mot qui sont different de "Mn". Mn etant les accents
            c for c in unicodedata.normalize("NFD",text) if unicodedata.category(c) != "Mn"

        )

    """NETOYAGE (html et punctuation)"""
    def remove_html(self,text):
        # on va utiliser les regex pour le faire
        # precisement le patern 'r<.*?>'
        return re.sub(r'<.*?>','',text)

    def remove_punctuation(self, text):
        # on supprime toutes les puctuations avec string.punctuation
        return text.translate(str.maketrans('','',string.punctuation))



    """TOKENIZATION (tokens and stopwords)"""

    # def tokeniser(self,text):
    #     return word_tokenize(text)

    def remove_stopwords(self,tokens):
        return [t for t in tokens if t.lower() not in self.stopwords]


    """PIPELINE D"EXECUTION"""

    def clean_pipeline(self,text):
        text = self.convert_to_lower_case(text)  # on convertie le text en lower
        text = self.remove_accents(text) # on retire les accents sur lr texte
        text = self.remove_html(text) # on ritire le html sur le text
        text = self.remove_punctuation(text) # on ritire la ponct sur le text
        # tokens = self.remove_stopwords(text)
        return text


# si je veux executer le script direcetement dans ce repertoire je fais ceci
if __name__=="__main__":

    cleandataset_1 = CleanDataset('english') # creation de mon object/instantiation

    sample = "he!!!!!je travaille sur un texte mais je fais le tokenizeur pour gerer mes <b>projects ❤️</b>."

    print(f'This is the exemple result:\n--> {cleandataset_1.clean_pipeline(sample)}')
