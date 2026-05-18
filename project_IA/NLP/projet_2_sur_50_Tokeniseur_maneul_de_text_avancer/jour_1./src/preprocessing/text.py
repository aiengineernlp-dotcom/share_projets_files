
from nltk import word_tokenize
import pandas as pd

# from main import cleandataset_1
from src.preprocessing.cleaner import CleanDataset
class Tokenizer:
    def __init__(self):
        pass
    def methode_avec_split(self,text):
        # la plus simple methode avec split()
        return text.split()

    def methode_avec_re_find_all(self,text):
        #la methode moyenne avec refindall()
        pass

    def methode_avec_nltk(self,text):
        #la methode plus avancer ici:
        return word_tokenize(text)


    # def tokeniser_pipeline(self,text):
    #     text = cleandataset_1.cleanpipeline(text)
    #     tokens = self.methode_avec_nltk(text)
    #     return tokens




if __name__=='__main__':
    tokeniser = Tokenizer()




