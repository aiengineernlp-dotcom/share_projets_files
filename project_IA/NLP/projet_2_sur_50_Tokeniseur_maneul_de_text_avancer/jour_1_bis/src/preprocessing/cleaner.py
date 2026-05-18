import string
import unicodedata
import re

import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# ============================================================================
# CLASSE
# ============================================================================
class DatasetCleaner:
    def __init__(self,stopword_language:str):
        # Initialise l'objet de nettoyage avec la langue specifiee pour les stopwords
        # chargement de la liste des mots vides de la langue specifie afin que
        # mon models les reconnaissent
        self.stopword_language = set(stopwords.words(stopword_language))

    """NORMALISATION c-a-d: remove convertir en minuscule et retirer les accents"""
    def convert_to_lowercase(self,dataset):
        return dataset.lower()

    def remove_accents(self,dataset):
        # normalisation NFD: decompose les caracteres accentues en caractere de base + accents
        # puis supprime tous les caracteres dans la categrie "Mark spacing" (les accents) representer par Mn
        return ''.join(
            # c for c in dataset if c.lower() in unicodedata.normalize("NFD", dataset) if unicodedata.category(c) !="Mn"
            c for c in unicodedata.normalize("NFD", dataset) if unicodedata.category(c) != "Mn"
        )

    """NETTOYAGE DU TEXTE c-a-d: remove le html et punctuations"""

    def remove_html(self, dataset):
        # Suppression des balises html avec une expression reguliere
        # On va utiliser le patern r'<.*?>' pour chercher tout ce qui est entre < et >
        return re.sub(r'<.*?>','', dataset)

    def remove_punctuation(self, dataset):
        # supprime toute la punctuation en utilisant string.punctuation (!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~)
        return dataset.translate(str.maketrans('','',string.punctuation))

    """TOKENIZATION c-a-d: diviser le texte en tokens (mots individuels)"""

    def tokeniser(self, dataset):
        #Divise le texte en tokens (mots individuels)
        #world_tokenize est  plus sophistiquer qu'un simple split () ou regex car il gere mieux
        # la punctuation et certains cas particuliers
        return word_tokenize(dataset)

    def remove_stopword(self,TOKENS):
        # filtre les mots vides(articles, prepositions, etc...) qui n'apportent pas beaucoup de valeur
        # semantique a l'analyse
        return  [token for token in TOKENS if token.lower() not in self.stopword_language] # ici il est question d'afficher
        # les "token", trouver dans TOKENS qui sont minuscules et ne sont pas dans la liste des  self.language (les stopwords)


    '''Enrichissement du prétraitement'''

    """LEMMATISATION/STEMMING c-a-d: pour reduire les mots a leurs racine"""

    def lemmatize(self, tokens):  # a ajouter dans le pipeline apres la tokenisation car ici on agi sur les tokens
        pass

    """GESTION DES N-GRAMMES c-a-d: pour capturer des expressions multi-mots"""

    def extract_ngrams(self, tokens, n=2):  # a ajouter dans le pipeline apres la tokenisation car ici on agi sur les tokens
        pass

    '''Fin Enrichissement du prétraitement'''


    """DEBUT---->AUTRES c-a-d: les autres methodes  que j'applique a mon Dataset """

    def remove_emojis(self, dataset):
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
        return emoji_pattern.sub(r'', dataset)

    def correct_spelling(self,dataset):
        # Corrections des fautes d'orthographes
        pass

    def normalize_entities(self,dataset):
        # Normalisation des entites (dates, nombres,noms etc...)
        pass

    """EVALUATION Et TEST"""

    def evaluation_cleaning(self,dataset,cleaned_tokens):
        #messure de l'efficassiter du notoyage
        pass

    """PARAMETRE CONTEXTUELL"""
    def add_domain_specific_stopwords(self,domain_stopwords):
        #Ajout des mots vides specifiques aux domaines
        pass

    """ FIN---->AUTRES c-a-d: les autres methodes  que j'applique a mon Dataset """


    """PIPELINE c-a-d: la chaine d'etapes successive que j'applique a mon Dataset """

    def DatasetCleaner_pipeline(self,dataset):
        # pipeline complet du nettoyage du dataset

        if not isinstance(dataset,str):  # comparaison
            # Verification que le texte est bien une chaine de caracteres
            return f'LA DONNEE A TRAITER N.EST PAS UNE CHAINE DE CARACTERES C.EST UNE donnee de type:  '  # Si dataset n.est pas une chaine de caracteres on retourne vide
        else:
            result_step = self.convert_to_lowercase(dataset)
            result_step = self.remove_accents(result_step)
            result_step = self.remove_emojis(result_step)
            result_step = self.remove_html(result_step)
            result_step = self.remove_punctuation(result_step)
            # tokens = self.tokeniser(result_step)
            # TOKENS = self.remove_stopword(tokens)
            return result_step


if __name__=="__main__": # Ce bloc initialise par cette ligne est juste parceque je veux faire executer le fichier directement ici dans cette page
    obj_DatasetCleaner_1 = DatasetCleaner('english')
    sample_dataset =  "J'adore ce produit ! 😍 Livraison <b>rapide</b>, et tres efficace. "
    #sample_dataset =()
    Traitement =obj_DatasetCleaner_1.DatasetCleaner_pipeline(sample_dataset)
    print("\n-->> VOICI LE RESULTAT:  ", Traitement)






