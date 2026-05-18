import re
import string
import unicodedata
from nltk.tokenize import word_tokenize

from nltk.corpus import stopwords
class DatasetCleaner:

    """
    """
    def __init__(self,language):
        """

        :param language:
        """
        self.stopword = set(stopwords.words(language))


    """NORMALISATION :  minuscule et accents"""

    def to_lower_case(self,text):

        return text.lower()


    def remove_accent(self,text):

        return "".join(
            c for c in unicodedata.normalize("NFD",text) if unicodedata.category(c) != "Mn"
        )

    """Nettoyage : html et punctuation"""
    def remove_html(self,text):
        """
avec une regex pour le html et string.punctuation pour la pumctuation
        """
        return re.sub(r'<.*?>','',text)

    def remove_punctuation(self,text):
        return text.translate(str.maketrans('','',string.punctuation))


    """TOKENISATION"""

    """
    jai commenter car c'etais juste a titre de revision . 
    il ya deja un fichier dedier pour le tokeniseur separement de celui-ci

    """

    # def tokeniser(self,text):
    #     """
    #     :param : text
    #     :return:les tokens qui seront utiliser par remove_stopwords
    #     """
    #     return word_tokenize(text)
    #
    # def remove_stopwords(self,tokens):
    #     return [t for t in tokens if t.lower() not in self.stopword]

    """Pipeline de DatasetCleaner """


    def DatasetCleaner_pipeline(self,text):
        '''
Ici c'est le pipeline d'execution de mon DatasetCleaner
genre il va executer en ordre et a la fin renvoyer text
        '''

        if not isinstance(text,str):  #
            # vu que on va appeller le DatasetCleaner_pipeline sur une chaine de caracteres il faut bien penser que
            # ce peut ne pas etre une chaine de caractere dans ce cas la on retourne une chaine vide
            # Si text n'est pas une chaîne de caractères (str), alors retourne une chaîne vide ('')
            #////////////
            #Retourner '' est logique si tu veux que la méthode continue à renvoyer une chaîne .
            #
            print("invalide!!!!!!")

            #
            # | Tu veux faire quoi ?                       | Valeur par défaut sûre |
            # | ------------------------------------------ | ---------------------- |
            # | Nettoyer un texte brut (préprocessing)     | `''` (chaîne vide)     |
            # | Retourner une liste de mots (tokenisation) | `[]` (liste vide)      |
            # | Retourner un dictionnaire vide             | `{}`                   |
            #

            return ''
        else:

            text = self.to_lower_case(text)
            text = self.remove_accent(text)
            text = self.remove_html(text)
            text = self.remove_punctuation(text)

        """
        jai commenter car c'etais juste a titre de revision . 
        il ya deja un fichier dedier pour le tokeniseur separement de celui-ci
        
        
        """
        # tokens = self.tokeniser(text)
        # tokens = self.remove_stopwords(tokens)

        return text


if __name__== "__main__":
    """
    vu que je veus que ce fichier sexecute lui seul genre on puisse se rendre dans de dossier et faire
    python cleaner.py  //// donc c'est un peu comme l'executeur
    """
    obj_DatasetCleaner_1 = DatasetCleaner('english')

    sample = "he!!!!!je travaille sur un texte mais je fais le tokenizeur pour gerer mes <b>projects ❤️</b>."

    print(obj_DatasetCleaner_1.DatasetCleaner_pipeline(sample))


