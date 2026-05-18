import re
import pandas as pd
from tqdm import tqdm
import nltk
nltk.download('stopwords')
nltk.download('punkt_tab')
import time
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from src.preprocessing.cleaner import DatasetCleaner
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
tqdm.pandas()


class Tokenizer:
    def __init__(self, language):
        self.stopwords = set(stopwords.words(language))
        """
        Ici je fais une importation qui me permetra d'utiliser les methodes qui sont dans la classe DatasetCleaner
        """
        self.obj_DatasetCleaner_1 = DatasetCleaner('english')

        """
       Tokenizer  permet de decomposer le dataset en mots unique dans une liste 
         on doit le faire avec de trois facons et plus tard comparer les resultats

         on va utiliser la methode split(), la methode re.findall() et enfin utiliser word_tokenize de nltk
         """

    def tokenise_methode_avec_split(self, text):
        '''plus simple et moins sauphistiquer sans aucune condition comme pourrait le faire une regex'''
        return text.split()

    def tokenise_methode_avec_re_find_all(self, text):
        """plus complex que la derrniere car utilise une regex. ici je vais uutiliser le pattern r'\w+' .
        le pattern r'\w+': permet d'afficher les chiffres et les lettres"""
        return re.findall(r'\w+', text)

    def tokenise_methode_avec_nltk(self, text):
        """plus directe et precise  en retournant uniquement ce que je veux:  les tokens """
        return word_tokenize(text)

    def remove_stopwords(self, tokens):
        return [t for t in tokens if t.lower() not in self.stopwords]

    def Tokenizer_pipeline(self, text, method, remove_stops):
        if not isinstance(text, str):

            #
            # | Tu veux faire quoi ?                       | Valeur par défaut sûre |
            # | ------------------------------------------ | ---------------------- |
            # | Nettoyer un texte brut (préprocessing)     | `''` (chaîne vide)     |
            # | Retourner une liste de mots (tokenisation) | `[]` (liste vide)      |
            # | Retourner un dictionnaire vide             | `{}`                   |
            #
            return []  # donc si on appel le Tokenizer_pipeline du Tokenizer sur une donnee
            # qui n'est pas une chaine de caractere alors
            # il devra retoutner une liste vide sinon il lance l'execution normalement
            # Si text n'est pas une chaîne de caractères (str), alors retourne une liste vide []
            # Retourner [] serait logique uniquement si ta méthode devait retourner une liste de tokens, .
        else:
            # ici on nettoye le dataset
            clean_dataset = self.obj_DatasetCleaner_1.DatasetCleaner_pipeline(text)
            # puis on choit la methode de tokenisation
            ###⚠️###⚠️ je ne sais pas pourquoi on se met dans une position ou on selectionne alors que je ne vois pas un input (pour l'instannn)
            if method == "split":
                tokens = self.tokenise_methode_avec_split(clean_dataset)
            elif method == "regex":
                tokens = self.tokenise_methode_avec_re_find_all(clean_dataset)
            else:  # default: nltk
                tokens = self.tokenise_methode_avec_nltk(clean_dataset)

            if remove_stops:  ### 🚩🚩🚩🚩🚩 je ne sais pas pourquoi on a besoin me mettre ce if ici.
                # Car moi je me disais que il suffissait de mettre
                # juste la ligne  tokens = self.remove_stopwords(tokens) et faire return tokens
                tokens = self.remove_stopwords(tokens)
            return tokens

    def compare_methodes(self, text):
        '''
        compare les diffrentes methodes de tokenisarion sur un texte. et devra retourner un
        dictionnaire car on a une collection de donnee a comparer
        :param text:
        :return:
        '''

        # 1. Créer un dictionnaire vide pour stocker les résultats
        results = {}

        # 2. Définir les méthodes à comparer
        methods = {
            # Utilisation des fonctions lambda pour encapsuler l'appel avec self afin que le self ne disparaisse pas
            # lors de l'appel de la methode reference: https://claude.ai/share/02ecb020-a826-457b-a921-cbd93fed6ee2
            'split': lambda x: self.tokenise_methode_avec_split(x),
            'regex': lambda x: self.tokenise_methode_avec_re_find_all(x),
            'nltk': lambda x: self.tokenise_methode_avec_nltk(x)
        }

        # 3. Nettoyer le texte une seule fois (pour toutes les méthodes)
        clean_dataset = self.obj_DatasetCleaner_1.DatasetCleaner_pipeline(text)

        # 4. Pour chaque méthode...
        for name, method in methods.items():
            # 5. Mesurer le temps de début
            start_time = time.time()

            # 6. Appliquer la méthode
            tokens = method(clean_dataset)

            # 7. Supprimer les stopwords
            tokens_no_stop = self.remove_stopwords(tokens)

            # 8. Calculer le temps écoulé
            execute_time = time.time() - start_time

            # 9. Enregistrer les résultats pour cette méthode
            results[name] = {
                'tokens': tokens,
                'tokens_no_stop': tokens_no_stop,
                'count': len(tokens),
                'count_no_stop': len(tokens_no_stop),
                'execution_time': execute_time
            }

        # 10. Retourner tous les résultats
        return results


class TokenizerAnalyzer:
    '''
    cette classe pour ananlyser et visualiser les diffrentes methodes de tokenisation
    '''

    def __init__(self, ):
        self.obj_tokenizer_1 = Tokenizer  # tokenizer (Tokenizer): Instance de la classe Tokenizer

    def analyse_corpus(self, df, text_column, sample_size):
        '''

        :param df: dataframme contenant les textes (mon dataset)
        :param text_column: le nom de ma collonne que je veux travailler ici c'est "Text"
        :param sample_size: Taille de mon echantillon a analyser
        :return: dataframe avec les resultats de l'analyse
        '''
        if sample_size:  #
            df = df.sample(sample_size).reset_index(
                drop=True)  # 🚩🚩🚩🚩🚩🚩🚩🚩 je ne sais pas ce qui vien de se passer.
            # 🚩🚩🚩🚩🚩🚩🚩🚩 mais je me dis que on retire les places ou l'index de mon df est vide

        else:
            pass

        results = []

        for idx, row in tqdm(df.iterrows(), total=len(df), desc='Analysing Texts'):  # Corrigé: iterrows au lieu de interrows

            text = row[text_column]

            comparison = self.obj_tokenizer_1.compare_methodes(text)

            # Ajouter l'index du texte et les resultats au dataframe

            for method, metrics in comparison.items():
                results.append({
                    'text_id': idx,
                    'method': method,
                    'token_count': metrics['count'],
                    'token_count_no_stop': metrics['count_no_stop'],
                    'execution_time': metrics['execution_time']
                })
        return pd.DataFrame(results)


    def visualise_results(self, results_df:pd.DataFrame):
        '''
        visualise les resultats de l'analyse
        :param results_df:  dataframe contenant les resultats de l'analyse
        :return:
        '''

        plt.figure(figsize=(15,10))

        # configuration du style:
        sns.set_style('Whitegrid')

        # 1- Comparaison du nombre de tokens

        plt.subplot(2,2,1)
        sns.boxplot(x='method',y='token_count',data=results_df)
        plt.title('Nombre de tokens par methode')
        plt.xlabel('Methode')
        plt.ylabel('Nombre de tokens')

        # 2- comparaisons du nombre de tokens sans stopwords

        plt.subplot(2,2,2)
        sns.boxplot(x='method',y='token_count_no_stop',data=results_df)
        plt.title('Nombre de tokens (sans stopwords) par methode')
        plt.xlabel('Methode')
        plt.ylabel('Nombre de Tokens')

        # 3- Comparaison du temps d'execution
        plt.subplot(2,2,3)
        sns.boxplot(x='method',y='execution_time',data=results_df)
        plt.title("Temps d'execution par methode")
        plt.xlabel('Methode')
        plt.ylabel('Temps (secondes)')

        # 4- rapport tokens/temps

        plt.subplot(2,2,4)
        results_df['efficiency'] = results_df['token_count']/results_df['execution_time']
        sns.boxplot(x='Method',y='efficiently',data=results_df)
        plt.title("Efficacite (tokens/secondes) par methode")
        plt.xlabel ('Methode')
        plt.ylabel('Tokens/secondes')

        plt.tight_layout()
        plt.savefig('Tokenisation_comparaison.png')
        plt.show()


        # STATISTIQUES SUPPlementaires

        print("Statistique par methodes: ")
        stats = results_df.groupby('method').agg({
            'token_count':['mean','std','min','max'],
            'token_count_no_stop':['mean','std','min','max'],
            'execution_time':['mean','std','min','max'],
            'efficiency':['mean','std','min','max']
        })
        print(stats)



# Fonction principale pour demarer l'utilisation

if __name__== "__main__":
    """
    vu que je veus que ce fichier sexecute lui seul genre on puisse se rendre dans de dossier et faire
    python tokeniser.py  //// donc c'est un peu comme l'executeur
    """
    obj_Tokenizer_1 = Tokenizer('english')
    # sample = "he!!!!!je travaille sur un texte mais je fais le tokenizeur pour gerer mes <b>projects ❤️</b>."
    #
    # print(obj_Tokenizer_1.Tokenizer_pipeline(sample,method='nltk',remove_stops=True))

    try:
        # chargement des donnees
        df = pd.read_csv('../../data/raw/Reviews.csv')
        #retirer les lignes vides das le fichier
        df = df.dropna(subset=['Text'])

        # Ajouter une colonne avec le texte nettoyer
        df['clean_text'] = df['Text'].progress_apply(obj_Tokenizer_1.Tokenizer_pipeline)

        # ajouter les colonnes pour chaque methodes de tokenisation

        df['tokens_split']=df['clean_text'].progress_apply(lambda x:obj_Tokenizer_1.Tokenizer_pipeline(x,method='split',remove_stops=True))        #⚠️ les remove_stops=True que j'ai mise ici je ne suis pas sur de ce que jai fait!!!!!

        df['tokens_regex']=df['clean_text'].progress_apply(lambda x: obj_Tokenizer_1.Tokenizer_pipeline(x,method='regex',remove_stops=True))        #⚠️ les remove_stops=True que j'ai mise ici je ne suis pas sur de ce que jai fait!!!!!

        df['tokens_nltk'] = df['clean_text'].progress_apply(lambda x:obj_Tokenizer_1.Tokenizer_pipeline(x,method='nltk',remove_stops=True))        #⚠️ les remove_stops=True que j'ai mise ici je ne suis pas sur de ce que jai fait!!!!!


        # sauvegarder les resultats

        df.to_csv('../../data/processed/Reviews_processed.csv',index=False)# pourquoi on le met a false.
        # non pas que on pouvais le mettre a True c'est juste que  je ne comprend pas le pourquoie de l'index....


        # Exemple de l'analyse sur un echantillon
        analyzer = TokenizerAnalyzer() #⚠️
        results = analyzer.analyse_corpus(df,'Text',sample_size=100)
        analyzer.visualise_results(results)

        # afficher quelques exemples

        print("\nExemple de tokenisation sur 5 etapes:")
        sample = df.sample(5)

        for idx,row in sample.iterrows():
            print(f"\nTexte original: {row['Text'][:100]}....")
            print(f"Text nettoyer: {row['clean_text'][:100]}...." )
            print(f"Tokens (split): {row['tokens_split'][:10]}....")
            print(f"Tokens (regex): {row['tokens_regex'][:10]}....")
            print(f"Tokens (nltk): {row['tokens_nltk'][:10]}....")

    except FileNotFoundError:
        print("Fichier de donnees nons trouve. Demonstrations avec un exemple: ")
        exemples = [
            "Bonjour! Je travaille sur un texte contenant des <b>balises HTML</b> et des caractères spéciaux (€, $, %).",
            "L'analyse de texte est une tâche importante en NLP. C'est un domaine très intéressant!",
            "The quick brown fox jumps over the lazy dog. This is a common pangram in English.",
            "Je vais à l'école en bus. J'étudie les mathématiques et la physique.",
            "Machine learning algorithms are powerful tools for data analysis and prediction."
        ]

        for i,exemple in enumerate(exemples):
            print(f"\nExemple {i+1}:{exemple}")

            comparison = obj_Tokenizer_1.compare_methodes(exemple)

            for method,result in comparison.items():
                print(f"\nMethode: {method}")
                print(f"\nTokens: {result['tokens']}")
                print(f"\n Sans stopswords: {result['tokens_no_stop']}")
                print(f"\n Nombre: {result['count']} (sans stopwords {result['count_no_stop']})")
                print(f"\nTemps d'execution: {result['execution_time']:.6f} secondes")


# Exemple de CLI minimal

import argparse

def run_cli():

    pass


