import re
import string
import unicodedata
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class TextCleaner:
    def __init__(self,language = 'french',):
        self.stopwords = set(stopwords.words(language))

    def to_lowercase(self,text):
        return text.lower()

    def remove_html(self,text):
        return re.sub(r'<.*?>','', text)

    def remove_accent(self,text):
        return ''.join(
            c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn'  # revoit ici
        )

    def remove_punctuation(self,text):
        return text.translate(str.maketrans('', '', string.punctuation))

    def tokenize(self,text): # (split manuel ou nltk.word_tokenize)
        return word_tokenize(text)

    def remove_stopwords(self,tokens):
        return [t for t in tokens if t.lower() not in self.stopwords]


    def clean(self,text):
        text = self.to_lowercase(text)
        text = self.remove_html(text)
        text = self.remove_accent(text)
        text = self.remove_punctuation(text)
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        return tokens

if __name__=="__main__":
    cleaner =TextCleaner()
    sample = "J'adore ce produit ! 😍 Livraison <b>rapide</b>, et tres efficace. "
    print(cleaner.clean(sample))