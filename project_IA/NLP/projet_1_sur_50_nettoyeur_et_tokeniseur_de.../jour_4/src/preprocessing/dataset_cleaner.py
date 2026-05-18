# corrige et met dataset au lieux de text comme tu as fait pour le projet-2, jour3.

import string
from nltk import word_tokenize
from nltk.corpus import stopwords
import unicodedata
import re

class DatasetCleaner:
    def __init__(self, language):
        # configuration de la langue du traitement des stopwords
        self.stopwords = set(stopwords.words(language))

    """NORMALISATION c-a-d: remove convertir en minuscule et retirer les accents"""
    def to_lowercase(self,dataset):
        return dataset.lower()

    def remove_accents(self, dataset):
        # normalisation NFD: decompose les caracteres accentues en caractere de base + accents
        # puis supprime tous les caracteres dans la categrie "Mark spacing" (les accents) representer par Mn
        return ''.join(
            c for c in unicodedata.normalize('NFD',dataset) if unicodedata.category(c) !='Mn'  # je ne comprend pas le Mn ci
        )

    """NETTOYAGE DU TEXTE c-a-d: remove le html et punctuations"""
    def remove_html(self,dataset):
        # Suppression des balises html avec une expression reguliere
        # On va utiliser le patern r'<.*?>' pour chercher tout ce qui est entre < et >
        return re.sub(r'<.*?>','',dataset)

    def remove_punctuations(self,dataset):
        # supprime toute la punctuation en utilisant string.punctuation (!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~)
        return dataset.translate(str.maketrans('','',string.punctuation))

    """TOKENIZATION c-a-d: diviser le texte en tokens (mots individuels)"""
    def tokenizer(self,dataset):
        # word_tokenize est plus sophistique qu'un simple split()
        # car il gere mieux la punctuation et certains cas particuliers
        return word_tokenize(dataset)

    def remove_stopwords(self,tokens):
        #filetre les mots vides (articles, prepositions, etc...)
        # qui n'apportent pas beaucoup de valeur semantique a l'analyse
        return [t for t in tokens if t.lower() not in self.stopwords] # je le lis que : pour t in tokens affiche dans une liste [t] si t.lower() n'est pas dans self.stopwords

    '''Enrichissement du prétraitement'''

    """LEMMATISATION/STEMMING c-a-d: pour reduire les mots a leurs racine"""

    def lemmatize(self, tokens):  # a ajouter dans le pipeline apres la tokenisation car ici on agi sur les tokens
        pass

    """GESTION DES N-GRAMMES c-a-d: pour capturer des expressions multi-mots"""

    def extract_ngrams(self, tokens, n=2):  # a ajouter dans le pipeline apres la tokenisation car ici on agi sur les tokens
        pass



    '''Fin Enrichissement du prétraitement'''

    """AUTRES c-a-d: les autres methodes  que j'applique a mon Dataset """

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


    """PIPELINE c-a-d: la chaine d'etapes successive que j'applique a mon Dataset """
    def clean_pipeline(self,dataset):
        # pipeline complet du nettoyage du dataset
        result_step = self.to_lowercase(dataset)
        result_step = self.remove_accents(result_step)
        result_step = self.remove_html(result_step)
        result_step = self.remove_emojis(result_step) # "AUTRES c-a-d: les autres methodes  que j'applique a mon Dataset
        result_step = self.remove_punctuations(result_step)
        tokens = self.tokenizer(result_step)
        tokens = self.remove_stopwords(tokens)
        return tokens


    #Bloc d'execution si le script est executer directement ici
if __name__=="__main__": # je dis que si le fichier actuel est le main . c-a-d, le fichier unique du projet. et dans ce cas vu que j'ai une classe il me faut creer l'objet ou les objects pour son execution
    obj_datasetcleaner_1 = DatasetCleaner('english')
    sample_dataset =  "J'adore ce produit ! 😍 Livraison <b>rapide</b>, et tres efficace. "
    # Le résultat devrait être: ['adore', 'produit', 'livraison', 'rapide', 'tres', 'efficace']
    print(f"\nApplication du pretraitement:", obj_datasetcleaner_1.datasetcleaner_pipeline(sample_dataset)) # donc je pars dans le DatasetCleaner a
    # travers l'object obj_datasetcleaner_1 et je recupere la methode "datasetcleaner_pipeline" pour appliquer sur mon "sample_dataset"











