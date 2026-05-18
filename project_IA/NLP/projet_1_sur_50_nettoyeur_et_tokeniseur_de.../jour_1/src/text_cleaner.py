# import re # Module pour les expressions regulieres
# import string # module contenant les caractere de ponctuations
# import unicodedata # module pour gerer les caracteres Unicode (comme les accents)
import re
import string
import unicodedata

from nltk import word_tokenize
from nltk.corpus import stopwords


class TextCleaner:
    def __init__(self,language = 'english'):
        # initialisation avec les mots vides dans une langue donnee
        self.stopwords = set(stopwords.words(language))
        pass

    def to_lowercase(self,text):
        # convertit tout le text en minuscule pour uniformiser
        return text.lower()

    def remove_html(self, text):
        return re.sub(r'<.*?>','', text)

    def remove_accents(self, text):
        return ''.join(
            c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) !='Mn'
        )

    def remove_punctuation(self,text):
        return text.translate(str.maketrans('', '', string.punctuation))


    def tokenize(self,text):
        return word_tokenize(text)

    def remove_stopwords(self,tokens):
        return [t for t in tokens if t.lower() not in self.stopwords]



    def clean(self,text):
        # pipeline complet de nettoyage du texte
        text = self.to_lowercase(text)
        text = self.remove_html(text)
        text = self.remove_accents(text)
        text = self.remove_punctuation(text)
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        return tokens

    #Bloc d'execution si le script est execute directement

if __name__=="__main__":
    cleaner = TextCleaner()
    sample = "j'adore ce produit ! ❤️ livreiason <b>rapide</b> et tres efficace."

    print(cleaner.clean(sample))






