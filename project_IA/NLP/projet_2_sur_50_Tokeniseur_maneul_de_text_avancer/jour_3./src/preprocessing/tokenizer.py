import re
import time

import pandas as pd
from nltk.tokenize import word_tokenize

from src.preprocessing.cleaner import DatasetCleaner
from nltk.corpus import stopwords

class TokenizerDatasetCleaner:
    def __init__(self, language_stopwords):
        self.language_stopwords = set(stopwords.words(language_stopwords))
        #   Ici je fais une importation qui me permetra d'utiliser les methodes qui sont dans la classe
        #   DatasetCleaner et je choisit de ne pas passer le paramettre de la langue car le l'ai commenter derriere
        #   dans l'autre fichier. deplus je peux l'avoir directement ici dans ce fichier tokenizer.py
        self.obj_DatasetCleaner_1 = DatasetCleaner('')

    def tokeniser_avec_split(self,dataset_cleaned):
        '''plus simple et moins sauphistiquer sans aucune condition comme pourrait le fairait une regex'''
        return dataset_cleaned.split()

    def tokeniser_avec_re_find_all(self,dataset_cleaned):
        """plus complex/t que la derrniere car utilise une regex. ici je vais uutiliser le pattern r'\w+' .
        le pattern r'\w+': permet d'afficher les chiffres et les lettres"""
        return re.findall(r'<\w+>',dataset_cleaned)

    def tokeniser_avec_nltk(self,dataset_cleaned):
        """plus directe et precise  que les precedantes en retournant uniquement ce que je veux:  les tokens """
        return word_tokenize(dataset_cleaned)

    def remove_stopwords(self,tokens:str):
        return [t for t in tokens if t.lower() not in self.language_stopwords]

    def Tokenizer_pipeline(self,dataset_cleaned:str,method:str='nltk',remove_stopwords: bool=True):
        if not isinstance(dataset_cleaned,str):
            #
            # | Tu veux faire quoi ?                       | Valeur par défaut sûre |
            # | ------------------------------------------ | ---------------------- |
            # | Nettoyer un texte brut (préprocessing)     | `''` (chaîne vide)     |
            # | Retourner une liste de mots (tokenisation) | `[]` (liste vide)      |
            # | Retourner un dictionnaire vide             | `{}`                   |
            #
            # qui n'est pas une chaine de caractere alors
            # il devra retoutner une liste vide sinon il lance l'execution normalement
            # Si text n'est pas une chaîne de caractères (str), alors retourne une liste vide []
            # Retourner [] serait logique uniquement si ta méthode devait retourner une liste de tokens, .


            print(f"\n {dataset_cleaned} n'est pas une chaine de caracteres.")
            return []  # donc si on appel le Tokenizer_pipeline du Tokenizer sur une donnee

        else:
            # ici on nettoye le dataset
            cleaned_dataset = self.obj_DatasetCleaner_1.datasetcleaner_pipeline(dataset_cleaned)

            if method == 'split':
                tokens = self.tokeniser_avec_split(cleaned_dataset)
            elif method == 'regex':
                tokens =self.tokeniser_avec_re_find_all(cleaned_dataset)
            else: # par default on a mise avec le nltk lors de la definition de la methode

                tokens = self.tokeniser_avec_nltk(cleaned_dataset)
            if remove_stopwords:
                tokens = self.remove_stopwords(tokens)

        return tokens

    def comparer_methodes(self,dataset_cleaned): # Comparaison de l'effet des methodes sur le dataset_cleaned et pour cela on a les 10 etapes
        '''
        compare les diffrentes methodes de tokenisarion sur le dataset_cleaned. et devra retourner un
        dictionnaire car on a une collection de donnees a comparer
        :param dataset_cleaned:
        :return:
        '''

        # 1. Créer un dictionnaire vide pour stocker les résultats
        results = {}
        # 2. Définir les méthodes à comparer
        methods = {
            'split': self.tokeniser_avec_split,
            'regex':  self.tokeniser_avec_re_find_all,
            'nltk':  self.tokeniser_avec_nltk
        }

        '''verifie les reactions avec lambda et sans lambda'''
        # methods = {
        # # Utilisation des fonctions lambda pour encapsuler l'appel avec self afin que le self ne disparaisse pas
        # # lors de l'appel de la methode reference: https://claude.ai/share/02ecb020-a826-457b-a921-cbd93fed6ee2
        #     'split': lambda x :self.tokeniser_avec_split(x),
        #     'regex': lambda  x : self.tokeniser_avec_re_find_all(x),
        #     'nltk': lambda x: self.tokeniser_avec_nltk(x)
        # }

        """#===START==>>>>>>>>>>>>>>>pourquoi pas une ecriture genre:"""


        """#===END==>>>>>>>>>>>>>>>pourquoi pas une ecriture genre:"""
        # 3. Nettoyer le texte une seule fois (pour toutes les méthodes)
        cleaned_dataset = self.obj_DatasetCleaner_1.datasetcleaner_pipeline(dataset_cleaned)

        # 4. Pour chaque méthode...
        for name,method in methods.items():
            # 5. Mesurer le temps de début
            start_time = time.time()
            # 6. Appliquer la méthode
            tokens = method(cleaned_dataset) ##### CETTE ERREUR EST UN FAUX NEGATIF car le code est bien fait mais l'editeur le signale
            # 7. Supprimer les stopwords
            tokens_no_stop = self.remove_stopwords(tokens)
            # 8. Calculer le temps écoulé
            execution_time = time.time()-start_time
            # 9. Enregistrer les résultats pour cette méthode
            results[name]= {
                'tokens': tokens,
                'tokens_no_stop': tokens_no_stop,
                'count_tokens' : len(tokens),
                'count_tokens_no_stop':len(tokens_no_stop),
                'execution_time':execution_time
            }
            # 10. Retourner tous les résultats
        return results

# ============================================================================
# CLASSE TOKENIZERANALYZER - ANALYSE ET VISUALISATION
# ============================================================================

class TokenizerAnalyser:
    '''
    cette classe pour ananlyser et visualiser les diffrentes methodes de tokenisation
    '''

    def __init__(self,):
        self.obj_TokenizerDatasetCleaner_1 = TokenizerDatasetCleaner('')

    def analyse_corpus(self,df: pd.DataFrame,text_column:str,sample_size:int):
        '''
        :param df: dataframme contenant les textes (mon dataset)
        :param text_column: le nom de ma collonne que je veux travailler ici c'est "Text"
        :param sample_size: Taille de mon echantillon a analyser
        :return: dataframe avec les resultats de l'analyse
        '''

        if sample_size:

            pass












if __name__=="__main__":
    obj_tokenizer = TokenizerDatasetCleaner('english')
    sample_clean_dataset = "Voici un exemple de texte à tokeniser. Ce texte contient plusieurs mots et ponctuations!"
    resultats = obj_tokenizer.comparer_methodes(sample_clean_dataset)

    # # Comparer les méthodes
    # # Afficher les résultats
    # for nom_methode, resultats_methode in resultats.items():
    #     print(f"Méthode: {nom_methode}")
    #     print(f"  Nombre de tokens: {resultats_methode['count_tokens']}")
    #     print(f"  Nombre de tokens sans stopwords: {resultats_methode['count_tokens_no_stop']}")
    #     print(f"  Temps d'exécution: {resultats_methode['execution_time']:.6f} secondes")
    #     print()















