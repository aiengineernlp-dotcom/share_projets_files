import string
from nltk import word_tokenize
from nltk.corpus import stopwords
import unicodedata
import re

class DatasetCleaner:
    def __init__(self, language):
        # chargement de la liste des mots vides des diffrentes langues afin que
        # mon models les reconnaissent
        self.stopwords = set(stopwords.words(language))
        pass

    """NORMALISATION c-a-d: remove convertir en minuscule et retirer les accents"""
    def to_lowercase(self,text):
        return text.lower()

    def remove_accents(self, text):
        # normalisation NFD: decompose les caracteres accentues en caractere de base + accents
        # puis supprime tous les caracteres dans la categrie "Mark spacing" (les accents)
        return ''.join(
            c for c in unicodedata.normalize('NFD',text) if unicodedata.category(c) !='Mn'  # je ne comprend pas le Mn ci
        )

    """NETTOYAGE DU TEXTE c-a-d: remove le html et punctuations"""
    def remove_html(self,text):
        # Suppression des balises html avec une expression reguliere
        # On va utiliser le patern r'<.*?>' pour chercher tout ce qui est entre < et >
        return re.sub(r'<.*?>','',text)

    def remove_punctuations(self,text):
        # supprime toute la punctuation en utilisant string.punctuation (!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~)
        return text.translate(str.maketrans('','',string.punctuation))

    """TOKENIZATION c-a-d: diviser le texte en tokens (mots individuels)"""
    def tokenizer(self,text):
        # word_tokenize est plus sophistique qu'un simple split()
        # car il gere mieux la punctuation et certains cas particuliers
        return word_tokenize(text)

    def remove_stopwords(self,tokens):
        #filetre les mots vides (articles, prepositions, etc...)
        # qui n'apportent pas beaucoup de valeur semantique a l'analyse
        return [t for t in tokens if t.lower() not in self.stopwords] # ici il est question d'afficher 
        # les "token", trouver dans TOKENS qui sont minuscules et ne sont pas dans la liste des  self.language (les stopwords)

    '''Enrichissement du prétraitement'''

    """LEMMATISATION/STEMMING c-a-d: pour reduire les mots a leurs racine"""

    def lemmatize(self, tokens):  # a ajouter dans le pipeline
        pass

    """GESTION DES N-GRAMMES c-a-d: pour capturer des expressions multi-mots"""
    def extract_ngrams(self,tokens,n=2): # a ajouter dans le pipeline
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

    def correct_spelling(self,text):
        # Corrections des fautes d'orthographes
        pass

    def normalize_entities(self,text):
        # Normalisation des entites (dates, nombres,noms etc...)
        pass

    """EVALUATION Et TEST"""

    def evaluation_cleaning(self,original_text,cleaned_tokens):
        #messure de l'efficassiter du notoyage
        pass

    """PARAMETRE CONTEXTUELL"""
    def add_domain_specific_stopwords(self,domain_stopwords):
        #Ajout des mots vides specifiques aux domaines
        pass


    """PIPELINE c-a-d: la chaine d'etapes successive que j'applique a mon Dataset """
    def clean_pipeline(self,text):
        # pipeline complet du nettoyage du dataset
        text = self.to_lowercase(text)
        text = self.remove_accents(text)
        text = self.remove_html(text)
        text = self.remove_emojis(text) # "AUTRES c-a-d: les autres methodes  que j'applique a mon Dataset
        text = self.remove_punctuations(text)
        tokens = self.tokenizer(text)
        tokens = self.remove_stopwords(tokens)
        return tokens

    #Bloc d'execution si le script est executer directement

if __name__=="__main__":
    obj_datasetcleaner_1 = DatasetCleaner(language='english')
    sample = "J'adore ce produit ! 😍 Livraison <b>rapide</b>, et tres efficace. "
    # Le résultat devrait être: ['adore', 'produit', 'livraison', 'rapide', 'tres', 'efficace']
    print(obj_datasetcleaner_1.clean_pipeline(sample)) # donc je pars dans le DatasetCleaner a
    # travers l'object obj_datasetcleaner_1 et je recupere la methode "clean_pipeline" pour appliquer sur mon "sample"















