import re
import string
import unicodedata

from nltk.corpus import stopwords  #

class DatasetCleaner:
    def __init__(self,language_stopwords):
        # configuration de la langue du traitement des stopwords
        # self.language_stopwords = set(stopwords.words(language_stopwords))
        '''
        je ne vois pas encore le besoin dactiver cette partie vu que le tokeniseur est dans un autre
        fichier et donc je peux definir la langue dans ce fichier la. mais meme ici c'est pas un probleme
        '''
        pass

    """NORMALISATION c-a-d: remove convertir en minuscule et retirer les accents"""
    def convert_to_lowercase(self, dataset):
        return dataset.lower()

    def remove_accents(self,dataset):
        # normalisation NFD: decompose les caracteres accentues en caractere de base + accents
        # puis supprime tous les caracteres dans la categrie "Mark spacing" (les accents) representer par Mn

        return ''.join(
            c for c in unicodedata.normalize('NFD',dataset) if unicodedata.category(c) !="Mn" # je ne comprend pas le Mn ci
        )


    """NETTOYAGE DU TEXTE c-a-d: remove le html et punctuations"""
    def remove_html(self, dataset):
        # Suppression des balises html avec une expression reguliere
        # On va utiliser le patern r'<.*?>' pour chercher tout ce qui est entre < et >
        return re.sub(r'<.*?>','',dataset)

    def romove_puntuation(self, dataset):
        # supprime toute la punctuation en utilisant string.punctuation (!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~)

        return dataset.translate(str.maketrans('','',string.punctuation))


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

    def correct_spelling(self, dataset):
        # Corrections des fautes d'orthographes
        pass

    def normalize_entities(self, dataset):
        # Normalisation des entites (dates, nombres,noms etc...)
        pass

    """EVALUATION Et TEST"""

    def evaluation_cleaning(self, dataset, cleaned_tokens):
        # messure de l'efficassiter du notoyage
        pass

    """PARAMETRE CONTEXTUELL"""

    def add_domain_specific_stopwords(self, domain_stopwords):
        # Ajout des mots vides specifiques aux domaines
        pass


    '''Enrichissement du prétraitement'''

    """LEMMATISATION/STEMMING c-a-d: pour reduire les mots a leurs racine"""

    def lemmatize(self, tokens):  # a ajouter dans le pipeline apres la tokenisation car ici on agi sur les tokens
        pass

    """GESTION DES N-GRAMMES c-a-d: pour capturer des expressions multi-mots"""

    def extract_ngrams(self, tokens, n=2):  # a ajouter dans le pipeline apres la tokenisation car ici on agi sur les tokens
        pass



    '''Fin Enrichissement du prétraitement'''


    """PIPELINE c-a-d: la chaine d'etapes successive que j'applique a mon Dataset """
    def datasetcleaner_pipeline(self,dataset):
        # pipeline complet du nettoyage du dataset
        if not isinstance(dataset, str):
            print(f"\n {dataset} n'est pas une chaine de caracteres.")
            return ' '

        else:
            result_step = self.convert_to_lowercase(dataset)
            result_step = self.remove_accents(result_step)
            result_step = self.remove_html(result_step)
            result_step = self.romove_puntuation(result_step)
            result_step = self.remove_emojis(result_step)

        return result_step

    #Bloc d'execution si le script est executer directement ici
if __name__=="__main__": # je dis que si le fichier actuel est le main . c-a-d, le fichier unique du projet. et dans ce cas vu que j'ai une classe il me faut creer l'objet ou les objects pour son execution
    obj_datasetcleaner_1 = DatasetCleaner('english')
    sample_dataset =  "J'adore ce produit ! 😍 Livraison <b>rapide</b>, et tres efficace. "
    # Le résultat devrait être: ['adore', 'produit', 'livraison', 'rapide', 'tres', 'efficace']
    cleaned_dataset = obj_datasetcleaner_1.datasetcleaner_pipeline(sample_dataset)# donc je pars dans le DatasetCleaner a
    # travers l'object obj_datasetcleaner_1 et je recupere la methode "datasetcleaner_pipeline" pour appliquer sur mon "sample_dataset"
    print(f"\nApplication du pretraitement:", cleaned_dataset )








