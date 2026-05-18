import re
import time
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from cleaner import DatasetCleaner
from tqdm import tqdm
tqdm.pandas()


# ============================================================================
# CLASSE
# ============================================================================
class Tokenizer:
    def __init__(self,stopword_language):
        self.stopword_language = set (stopwords.words(stopword_language))
        self.Obj_datasetCleaner_1 = DatasetCleaner('english')

    def methode_avec_split(self,dataset)->[]:
        #tokenise un texte avec la methode la plus simple: str.split()
        return dataset.split()

    def methode_avec_regex_re_find_all(self,dataset)->[]:
        return re.findall(r'\w+',dataset)

    def methode_avec_nltk(self, dataset)->[]:
        return word_tokenize(dataset)

    def remove_stopwords(self,TOKENS)->[]:
        return [token for token in TOKENS if token.lower() not in self.stopword_language]


    def Tokenizer_Pipeline(self,dataset,method='nltk',remove_stops=True):


        # Etape 1:  Nettoyage du texte
        result_step_1= self.Obj_datasetCleaner_1.DatasetCleaner_pipeline(dataset)  # donc ici on a recuperer
        # le Nettoyeur du fichier cleaner // ou si on veut, l'etape ou on fait le nottoyage // ou alors l'etape avant la
        # tokenisation et le remove stopwords // d'ou s'en suivra la tokenization

        #Etape 2 : Tokenization selon la methode choisie

        if method=='split':
            tokens = self.methode_avec_split(result_step_1)
        elif method=='regex':
            tokens  = self.methode_avec_regex_re_find_all(result_step_1)
        else:#Methode par default
            tokens = self.methode_avec_nltk(result_step_1)

        #Etape 3 : Option pour retirer les stopwords
        if remove_stops:  # car on suppose que on ne veut pas retirer les stopwords partout genre a toute les methodes . on a le choix
            tokens = self.remove_stopwords(tokens)
        return tokens



    def comparer_methodes(self,dataset):
        # ici on va faire une sorte de compareur de methodes pour voir quelle methode
        # est la meilleur donc on va les passer dans ce comparateur et donc comparer.

        '''DECLARATION DES (ce que je me permet d'appeller le VARIABLES) de la methode comparer_methodes() '''
        '''J'aurai besoin de 1-  # le resultat de la comparaison sera stoker ici '''
        resultat = {}

        '''J'aurai besoin de 2-  # definition de mes methodes a comparees dans un dictionnaire  '''
        all_methode = {
            'split' : self.methode_avec_split,
            'regex' : self.methode_avec_regex_re_find_all,
            'nltk'  : self.methode_avec_nltk
        }

        '''J'aurai besoin de 3- # Nettoyage du texte une seule fois pour toutes les methodes afin de ne pas biaiser la comparaison  '''
        # chargement des donnees nettoyees via la pipeline
        result_step_1 = self.Obj_datasetCleaner_1.DatasetCleaner_pipeline(dataset)

        # Pour chaque methode on va messurer le temps d'execution et de la collecte des resultats

        for name,method in all_methode.items():  # la methodes .items() s'applique aux dictionnaires
            '''1- mesure du temps d'execution'''
            start_time = time.time()
            #tokens = all_methode(result_step_1) # cf NOTES ligne 88
            TOKENS = result_step_1
            tokens_no_stop = self.remove_stopwords(TOKENS)
            execution_time = time.time()- start_time

            '''2- stokage des resultats pour la methode'''
            resultat[name] = {
                'tokens' : TOKENS, #
                'tokens_no_stop': tokens_no_stop, #
                'count': len(TOKENS), #
                'count_tokens_no_stop':len(tokens_no_stop), #
                'execution_time': execution_time #
            }

        return resultat

# ============================================================================
# CLASSE TOKENIZERANALYZER - ANALYSE ET VISUALISATION
# ============================================================================

class TokeniserAnalyser:
    """
    cette classe pour analyser et visualiser les performances des diffrenetes methodes de tokenisation sur un corpus de texte
    """
    def __init__(self,tokeniser:Tokenizer):
        self.tokeniser = tokeniser

    """Analyse corpus"""
    def analyse_corpus(self,df:pd.DataFrame,Text_column:str,sample_size:int=None):
        results = []
        #Echantillonage optionnelle pour accelerer l'analyse sur de grands corpus
        if sample_size:
            df = df.sample(sample_size).reset_index(drop=True)

        # Analyse de chaque texte du corpus avec une barre de progression

        for idx,row in tqdm (df.iterrows(), total = len(df), desc = "Analyzing texts"):
            text = row[Text_column]
            # Comparaison des methodes sur ce texte
            comparison = self.tokeniser.comparer_methodes(text)

            #ajout des resultats au DataFrame de resultats

            for method, metrics in comparison.items():
                results.append(
                    {
                        'text_id': idx,
                        'method':method,
                        'token_count':metrics['count'],
                        'token_count_no_stop':metrics['count_tokens_no_stop'],
                        'execution_time': metrics['execution_time']
                    }
                )

            return pd.DataFrame(results)

    def visualise_resultats(self,resultats_df):
        """
        Creer les visualisations grahphiques des reultats de l'analyse pour comparer facilement les diffrentes methodes
        :param resultats_df:  dataframe conetenant les resultats de l'analyse
        :return:
        """

        #Configuration de la taille de la figure
        plt.figure(figsize=(15,10))

        # style des graphiques avec seaborn
        sns.set_style("whitegrid")    # possible faut negatif

        #1. comparison du nombre de tokens par methodes
        plt.subplot(2,2,1) # premier graphique en haut a gauche
        sns.boxplot(x='method',y='token_count', data = resultats_df) # possible faut negatif
        plt.title('Nombre de tokens par methodes')
        plt.xlabel('Methode')
        plt.ylabel('Nombre de tokens')


        #2. comparaison du nombre de tokens sans stopwords
        plt.subplot(2,2,2)#Deuxieme graphique en haut a droite
        sns.boxplot(x='method',y='token_count_no_stop',data=resultats_df)
        plt.title("Nombre de tokens sans stopwords par methodes")
        plt.xlabel("Methode")
        plt.ylabel("Nombre de tokens")

        #3. Comparaison du temps dexecution
        plt.subplot(2,2,3) # Troisieme graphique en bas a gauche
        sns.boxplot(x='method',y='efficiency',data=resultats_df)
        plt.title("Temps d'execution par methode")
        plt.xlabel("Methode")
        plt.ylabel("Temps (seconde)")

        #4. Rapport efficassiter (Tokens/temps)

        plt.subplot(2,2,4) # Quatrieme Graphique (en bas a droite)
        #Calcul d'un indicateur d'efficacite, nombre de tokens traite par secondes
        resultats_df['efficiency'] = resultats_df['token_count'] / resultats_df['execution_time']
        sns.boxplot(x='method',y='efficiency',data=resultats_df)
        plt.title('Efficaciter (Tokens/seconde) par methode')
        plt.xlabel('Methode')
        plt.ylabel('Tokens/seconde')


        #Ajustement de la mise en page et sauvegarde

        plt.tigth_layout()
        plt.savefig('tokenisation_comparaison.png')
        plt.show()

        # affichage des statistques supplememtaires

        print("Statistiques detaillee par methodes: ")
        stats = resultats_df.groupby('method').agg({
            'token_count': ['mean','std','min','max'], # stat sur le nombre de tokens
            'token_count_no_stop':['mean','std','min','max'], #sans stopwords
            'execution_time': ['mean','std','min','max'],# Temps dexecution
            'efficiency':['mean','std',] # efficacite
        })
        print(stats)









# ============================================================================
# CLASSE
# ============================================================================
if __name__=="__main__":
    obj_tokenizer = Tokenizer('english')

    try:
        # tentative de charger les donnees depuis le fichier csv
        df = pd.read_csv('../../data/raw/Reviews 16.27.13.csv')
        df = df.dropna(subset=['Text'])  # suppression des lignes sans texte


        '''    # pretraitement du dataset '''
        print('Pretraitement du dataset ...')
        # 1. Ajout dune collonne avec le texte nettoye sans tokenization
        df['clean_text'] = df['Text'].progress_apply(obj_tokenizer.Tokenizer_Pipeline)

        #2. ajout d'une collonne pour chaque methode de tokenisation
        print('Application des diffrentes methodes de tokenisation...')

        df['tokens_split']= df['clean_text'].progress_apply(lambda x: obj_tokenizer.Tokenizer_Pipeline(x,method='split'))
        df['tokens_regex'] =df['clean_text'].progress_apply(lambda x : obj_tokenizer.Tokenizer_Pipeline(x,method='regex'))
        df['tokens_nltk'] = df['clean_text'].progress_apply(lambda x: obj_tokenizer.Tokenizer_Pipeline(x,method='nltk'))

        #3. Sauvegarde des resultats
        print("SAuvegarde des resultats....")
        df.to_csv('../../data/processed/Reviews_processed.csv',index=False)

        #4- Analyse comparative sur un echantillon

        print('Analyse comparative des methodes.....')
        analyzer = TokeniserAnalyser(obj_tokenizer)
        results = analyzer.analyse_corpus(df, 'Text',sample_size=100)

        #5 visualise les resultats
        print('Creation des visualisations...')
        analyzer.visualise_resultats(results)

        #6. Affichage de quelques exemples

        print("\nExemple de tokenization sur 5 textes")
        sample = df.sample(5) # Echantillon alleatoi de 5 textes

        for idx, row, in sample.iterrows():
            print(f"\nTexte original : {row['Text'][:100]}...") # les 100 premiers tokens
            print(f"Texte nettoye : {row['clean_text'][:100]}...")
            print(f" Tokens (splits) : {row['tokens_split'][:10]}...")#les 10 premiers tokens
            print(f" Tokens (regex) : {row['tokens_regex'][:10]}...")
            print(f"Tokens (nltk) : {row['tokens_nltk'][:10]}...")
    except FileNotFoundError:
        # si le fichier de donnees (dataset) n'est pas trouvee on utilise des exemple de demonstration
        print("Fichier de donnees non trouver demonstration avec les exemples: ")

            # Exemple varier en francais et en anglais pour tester diffrents aspects
        examples = [
            "Bonjour! Je travaille sur un texte contenant des <b>balises HTML</b> et des caractères spéciaux (€, $, %).",

            "L'analyse de texte est une tâche importante en NLP. C'est un domaine très intéressant!",

            "The quick brown fox jumps over the lazy dog. This is a common pangram in English.",

            "Je vais à l'école en bus. J'étudie les mathématiques et la physique.",

            "Machine learning algorithms are powerful tools for data analysis and prediction."

        ]


        # Analyse de chaque exemple
        for i, example in enumerate(examples):
            print(f"\n Exemple {i+1}: {example}")
            # Comparaison des methodes sur cet exemple
            comaparison = obj_tokenizer.comparer_methodes(example)

            # Affiche des resultats pour chaque methode

            for method, result, in comaparison.items():
                print(f"\n Methode: {method}")
                print(f"Tokens: {result['tokens']}")
                print(f" Sans stopwords: {result['token_no_stop']}")
                print(f"Nombre: {result['count']}(sans stopwords){result['count_no_stop']}")
                print(f"Temps d'execution: {result['executio_time']:.6f} secondes")




