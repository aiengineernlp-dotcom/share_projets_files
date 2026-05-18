import re
import string
import unicodedata
import time
from typing import List, Dict, Any

from nltk import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

# Active la barre de progression pour les opérations pandas
tqdm.pandas()


# ============================================================================
# CLASSE CLEANDATASET - PRÉTRAITEMENT ET NETTOYAGE DU TEXTE
# ============================================================================
class CleanDataset:
    """
    Cette classe est responsable du prétraitement et nettoyage des textes.
    Elle applique diverses opérations comme la conversion en minuscules,
    la suppression des accents, des balises HTML et de la ponctuation.
    """

    def __init__(self, language: str):
        """
        Initialise l'objet de nettoyage avec la langue spécifiée pour les stopwords.

        Args:
            language (str): Code de langue pour les stopwords (ex: 'english', 'french')
                            Il est important de choisir la bonne langue pour avoir
                            la liste appropriée de mots vides.
        """
        # Chargement des stopwords depuis NLTK pour la langue spécifiée
        # et conversion en ensemble (set) pour des recherches plus rapides
        self.stopwords = set(stopwords.words(language))
        self.language = language

    def convert_to_lower_case(self, text: str) -> str:
        """
        Convertit tous les caractères du texte en minuscules.
        Cette étape est importante pour standardiser le texte et éviter
        les différences dues aux majuscules/minuscules.

        Args:
            text (str): Texte à convertir en minuscules

        Returns:
            str: Texte en minuscules
        """
        return text.lower()

    def remove_accents(self, text: str) -> str:
        """
        Retire les accents du texte en utilisant la normalisation NFD Unicode.

        Le processus se fait en deux étapes:
        1. Normalisation NFD qui décompose les caractères accentués
           (ex: 'é' devient 'e' + accent)
        2. Filtrage pour ne garder que les caractères qui ne sont pas des marques
           diacritiques (catégorie Unicode 'Mn')

        Args:
            text (str): Texte avec potentiellement des accents

        Returns:
            str: Texte sans accents
        """
        return ''.join(
            # Pour chaque caractère dans le texte normalisé:
            # - Si ce n'est pas une marque diacritique (accent), on le garde
            # - Sinon, on l'ignore
            c for c in unicodedata.normalize("NFD", text)
            if unicodedata.category(c) != "Mn"
        )

    def remove_html(self, text: str) -> str:
        """
        Retire les balises HTML du texte en utilisant une expression régulière.
        L'expression r'<.*?>' capture toute séquence commençant par '<',
        suivie de n'importe quels caractères (non gourmands avec '?'),
        et se terminant par '>'.

        Args:
            text (str): Texte pouvant contenir des balises HTML

        Returns:
            str: Texte sans balises HTML
        """
        return re.sub(r'<.*?>', '', text)

    def remove_punctuation(self, text: str) -> str:
        """
        Supprime tous les signes de ponctuation du texte en utilisant
        la constante string.punctuation qui contient tous les caractères
        de ponctuation standard.

        La méthode translate avec str.maketrans remplace chaque caractère
        de ponctuation par une chaîne vide.

        Args:
            text (str): Texte avec ponctuation

        Returns:
            str: Texte sans ponctuation
        """
        return text.translate(str.maketrans('', '', string.punctuation))

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Retire les stopwords (mots vides) d'une liste de tokens.
        Les stopwords sont des mots très communs comme les articles,
        les prépositions, etc. qui apportent peu de valeur sémantique.

        Args:
            tokens (List[str]): Liste de tokens/mots

        Returns:
            List[str]: Liste de tokens sans les stopwords
        """
        return [t for t in tokens if t.lower() not in self.stopwords]

    def clean_pipeline(self, text: str) -> str:
        """
        Applique séquentiellement toutes les étapes de nettoyage au texte.
        Cette méthode sert de point d'entrée unique pour nettoyer un texte.

        Le pipeline de traitement est:
        1. Conversion en minuscules
        2. Suppression des accents
        3. Suppression des balises HTML
        4. Suppression de la ponctuation

        Args:
            text (str): Texte brut à nettoyer

        Returns:
            str: Texte nettoyé
        """
        # Vérification que le texte est bien une chaîne de caractères
        if not isinstance(text, str):
            return ""

        # Application séquentielle des étapes de nettoyage
        text = self.convert_to_lower_case(text)
        text = self.remove_accents(text)
        text = self.remove_html(text)
        text = self.remove_punctuation(text)
        return text


# ============================================================================
# CLASSE TOKENIZER - MÉTHODES DE TOKENISATION
# ============================================================================
class Tokenizer:
    """
    Classe responsable de la tokenisation de texte avec différentes méthodes.
    Elle implémente trois approches de complexité croissante:
    1. Simple (split)
    2. Intermédiaire (regex)
    3. Avancée (NLTK)
    """

    def __init__(self, language: str):
        """
        Initialise le tokenizer avec une langue pour les stopwords
        et crée une instance de CleanDataset pour le prétraitement.

        Args:
            language (str): Langue pour les stopwords (ex: 'english', 'french')
        """
        self.language = language
        # Chargement des stopwords pour la langue spécifiée
        self.stopwords = set(stopwords.words(language))
        # Création d'une instance de CleanDataset pour réutiliser ses méthodes
        self.cleaner = CleanDataset(language)

    def methode_avec_split(self, text: str) -> List[str]:
        """
        Tokenise un texte avec la méthode la plus simple: str.split()
        Cette méthode découpe simplement le texte aux espaces.

        Limitations:
        - Ne gère pas bien la ponctuation collée aux mots
        - Ne reconnaît pas les contractions (comme l'apostrophe)
        - Sensible aux espaces multiples

        Args:
            text (str): Texte à tokeniser

        Returns:
            List[str]: Liste de tokens
        """
        return text.split()

    def methode_avec_re_find_all(self, text: str) -> List[str]:
        """
        Tokenise un texte avec des expressions régulières via re.findall()

        L'expression \w+ capture des séquences d'un ou plusieurs caractères
        alphanumériques ou underscore.

        Avantages par rapport à split():
        - Gère mieux la ponctuation
        - Ignore automatiquement les espaces multiples

        Limitations:
        - Ne gère pas bien les contractions
        - Ne capture pas certains caractères spéciaux

        Args:
            text (str): Texte à tokeniser

        Returns:
            List[str]: Liste de tokens
        """
        return re.findall(r'\w+', text)

    def methode_avec_nltk(self, text: str) -> List[str]:
        """
        Tokenise un texte avec la méthode avancée word_tokenize de NLTK

        Avantages:
        - Gère intelligemment la ponctuation
        - Reconnaît les contractions
        - Traite correctement de nombreux cas particuliers
        - Basé sur des règles linguistiques

        Args:
            text (str): Texte à tokeniser

        Returns:
            List[str]: Liste de tokens
        """
        return word_tokenize(text)

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Retire les stopwords (mots vides) d'une liste de tokens

        Args:
            tokens (List[str]): Liste de tokens/mots

        Returns:
            List[str]: Liste de tokens sans stopwords
        """
        return [t for t in tokens if t.lower() not in self.stopwords]

    def tokeniser_pipeline(self, text: str, method: str = 'nltk', remove_stops: bool = True) -> List[str]:
        """
        Applique un pipeline complet de traitement sur un texte:
        1. Nettoyage du texte
        2. Tokenisation selon la méthode choisie
        3. Option pour retirer les stopwords

        Args:
            text (str): Texte brut à traiter
            method (str): Méthode de tokenisation ('split', 'regex', 'nltk')
            remove_stops (bool): Si True, retire les stopwords

        Returns:
            List[str]: Liste de tokens nettoyés
        """
        # Vérification du type de l'entrée
        if not isinstance(text, str):
            return []

        # Étape 1: Nettoyage du texte
        clean_text = self.cleaner.clean_pipeline(text)

        # Étape 2: Tokenisation selon la méthode choisie
        if method == 'split':
            tokens = self.methode_avec_split(clean_text)
        elif method == 'regex':
            tokens = self.methode_avec_re_find_all(clean_text)
        else:  # Par défaut: nltk
            tokens = self.methode_avec_nltk(clean_text)

        # Étape 3: Option pour retirer les stopwords
        if remove_stops:
            tokens = self.remove_stopwords(tokens)

        return tokens

    def compare_methods(self, text: str) -> Dict[str, Any]:
        """
        Compare les différentes méthodes de tokenisation sur un même texte
        et mesure leurs performances (temps d'exécution, nombre de tokens)

        Args:
            text (str): Texte à tokeniser

        Returns:
            Dict: Dictionnaire avec les résultats et métriques pour chaque méthode
        """
        results = {}
        # Définition des méthodes à comparer
        methods = {
            'split': self.methode_avec_split,
            'regex': self.methode_avec_re_find_all,
            'nltk': self.methode_avec_nltk
        }

        # Nettoyage du texte une seule fois pour toutes les méthodes
        # afin de ne pas biaiser la comparaison
        clean_text = self.cleaner.clean_pipeline(text)

        # Pour chaque méthode, mesure du temps d'exécution et collecte des résultats
        for name, method in methods.items():
            # Mesure du temps d'exécution
            start_time = time.time()
            tokens = method(clean_text)
            tokens_no_stop = self.remove_stopwords(tokens)
            execution_time = time.time() - start_time

            # Stockage des résultats pour cette méthode
            results[name] = {
                'tokens': tokens,  # Liste complète des tokens
                'tokens_no_stop': tokens_no_stop,  # Liste sans stopwords
                'count': len(tokens),  # Nombre total de tokens
                'count_no_stop': len(tokens_no_stop),  # Nombre sans stopwords
                'execution_time': execution_time  # Temps d'exécution en secondes
            }

        return results


# ============================================================================
# CLASSE TOKENIZERANALYZER - ANALYSE ET VISUALISATION
# ============================================================================
class TokenizerAnalyzer:
    """
    Classe pour analyser et visualiser les performances des différentes
    méthodes de tokenisation sur un corpus de textes
    """

    def __init__(self, tokenizer: Tokenizer):
        """
        Initialise l'analyseur avec un tokenizer

        Args:
            tokenizer (Tokenizer): Instance de la classe Tokenizer
        """
        self.tokenizer = tokenizer

    def analyze_corpus(self, df: pd.DataFrame, text_column: str, sample_size: int = None) -> pd.DataFrame:
        """
        Analyse un corpus de textes avec les différentes méthodes de tokenisation
        et collecte des statistiques de performance

        Args:
            df (pd.DataFrame): DataFrame contenant les textes
            text_column (str): Nom de la colonne contenant les textes
            sample_size (int, optional): Taille de l'échantillon à analyser
                                        (utile pour les grands corpus)

        Returns:
            pd.DataFrame: DataFrame avec les résultats d'analyse
        """
        # Échantillonnage optionnel pour accélérer l'analyse sur de grands corpus
        if sample_size:
            df = df.sample(sample_size).reset_index(drop=True)

        results = []

        # Analyse de chaque texte du corpus avec une barre de progression
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Analyzing texts"):
            text = row[text_column]
            # Comparaison des méthodes sur ce texte
            comparison = self.tokenizer.compare_methods(text)

            # Ajout des résultats au DataFrame de résultats
            for method, metrics in comparison.items():
                results.append({
                    'text_id': idx,  # Identifiant du texte
                    'method': method,  # Méthode de tokenisation
                    'token_count': metrics['count'],  # Nombre de tokens
                    'token_count_no_stop': metrics['count_no_stop'],  # Sans stopwords
                    'execution_time': metrics['execution_time']  # Temps d'exécution
                })

        return pd.DataFrame(results)

    def visualize_results(self, results_df: pd.DataFrame):
        """
        Crée des visualisations graphiques des résultats de l'analyse
        pour comparer facilement les différentes méthodes

        Args:
            results_df (pd.DataFrame): DataFrame contenant les résultats d'analyse
        """
        # Configuration de la taille de la figure
        plt.figure(figsize=(15, 10))

        # Style des graphiques avec seaborn
        sns.set_style("whitegrid")

        # 1. Comparaison du nombre de tokens par méthode
        plt.subplot(2, 2, 1)  # Premier graphique (en haut à gauche)
        sns.boxplot(x='method', y='token_count', data=results_df)
        plt.title('Nombre de tokens par méthode')
        plt.xlabel('Méthode')
        plt.ylabel('Nombre de tokens')

        # 2. Comparaison du nombre de tokens sans stopwords
        plt.subplot(2, 2, 2)  # Deuxième graphique (en haut à droite)
        sns.boxplot(x='method', y='token_count_no_stop', data=results_df)
        plt.title('Nombre de tokens (sans stopwords) par méthode')
        plt.xlabel('Méthode')
        plt.ylabel('Nombre de tokens')

        # 3. Comparaison du temps d'exécution
        plt.subplot(2, 2, 3)  # Troisième graphique (en bas à gauche)
        sns.boxplot(x='method', y='execution_time', data=results_df)
        plt.title('Temps d\'exécution par méthode')
        plt.xlabel('Méthode')
        plt.ylabel('Temps (secondes)')

        # 4. Rapport efficacité (tokens/temps)
        plt.subplot(2, 2, 4)  # Quatrième graphique (en bas à droite)
        # Calcul d'un indicateur d'efficacité: nombre de tokens traités par seconde
        results_df['efficiency'] = results_df['token_count'] / results_df['execution_time']
        sns.boxplot(x='method', y='efficiency', data=results_df)
        plt.title('Efficacité (tokens/seconde) par méthode')
        plt.xlabel('Méthode')
        plt.ylabel('Tokens/seconde')

        # Ajustement de la mise en page et sauvegarde
        plt.tight_layout()
        plt.savefig('tokenization_comparison.png')
        plt.show()

        # Affichage de statistiques supplémentaires
        print("Statistiques détaillées par méthode:")
        stats = results_df.groupby('method').agg({
            'token_count': ['mean', 'std', 'min', 'max'],  # Statistiques sur le nombre de tokens
            'token_count_no_stop': ['mean', 'std', 'min', 'max'],  # Sans stopwords
            'execution_time': ['mean', 'std', 'min', 'max'],  # Temps d'exécution
            'efficiency': ['mean', 'std']  # Efficacité
        })
        print(stats)


# ============================================================================
# PARTIE PRINCIPALE - DÉMONSTRATION D'UTILISATION
# ============================================================================
if __name__ == "__main__":
    # Instancier le tokenizer avec la langue souhaitée
    tokenizer = Tokenizer('french')  # ou 'english' selon le corpus

    try:
        # Tentative de chargement des données depuis un fichier CSV
        df = pd.read_csv('../../data/raw/Reviews.csv')
        df = df.dropna(subset=['Text'])  # Suppression des lignes sans texte

        # Prétraitement du dataset
        print("Prétraitement du dataset...")

        # 1. Ajout d'une colonne avec le texte nettoyé (sans tokenisation)
        df['clean_text'] = df['Text'].progress_apply(tokenizer.cleaner.clean_pipeline)

        # 2. Ajout d'une colonne pour chaque méthode de tokenisation
        print("Application des différentes méthodes de tokenisation...")
        df['tokens_split'] = df['clean_text'].progress_apply(
            lambda x: tokenizer.tokeniser_pipeline(x, method='split')
        )
        df['tokens_regex'] = df['clean_text'].progress_apply(
            lambda x: tokenizer.tokeniser_pipeline(x, method='regex')
        )
        df['tokens_nltk'] = df['clean_text'].progress_apply(
            lambda x: tokenizer.tokeniser_pipeline(x, method='nltk')
        )

        # 3. Sauvegarde des résultats
        print("Sauvegarde des résultats...")
        df.to_csv('../../data/processed/Reviews_processed.csv', index=False)

        # 4. Analyse comparative sur un échantillon
        print("Analyse comparative des méthodes...")
        analyzer = TokenizerAnalyzer(tokenizer)
        results = analyzer.analyze_corpus(df, 'Text', sample_size=100)

        # 5. Visualisation des résultats
        print("Création des visualisations...")
        analyzer.visualize_results(results)

        # 6. Affichage de quelques exemples
        print("\nExemples de tokenisation sur 5 textes:")
        sample = df.sample(5)  # Échantillon aléatoire de 5 textes
        for idx, row in sample.iterrows():
            print(f"\nTexte original: {row['Text'][:100]}...")  # 100 premiers caractères
            print(f"Texte nettoyé: {row['clean_text'][:100]}...")
            print(f"Tokens (split): {row['tokens_split'][:10]}...")  # 10 premiers tokens
            print(f"Tokens (regex): {row['tokens_regex'][:10]}...")
            print(f"Tokens (nltk): {row['tokens_nltk'][:10]}...")

    except FileNotFoundError:
        # Si le fichier de données n'est pas trouvé, on utilise des exemples de démonstration
        print("Fichier de données non trouvé. Démonstration avec des exemples:")

        # Exemples variés en français et anglais pour tester différents aspects
        examples = [
            "Bonjour! Je travaille sur un texte contenant des <b>balises HTML</b> et des caractères spéciaux (€, $, %).",
            "L'analyse de texte est une tâche importante en NLP. C'est un domaine très intéressant!",
            "The quick brown fox jumps over the lazy dog. This is a common pangram in English.",
            "Je vais à l'école en bus. J'étudie les mathématiques et la physique.",
            "Machine learning algorithms are powerful tools for data analysis and prediction."
        ]

        # Analyse de chaque exemple
        for i, example in enumerate(examples):
            print(f"\nExemple {i + 1}: {example}")

            # Comparaison des méthodes sur cet exemple
            comparison = tokenizer.compare_methods(example)

            # Affichage des résultats pour chaque méthode
            for method, result in comparison.items():
                print(f"\nMéthode: {method}")
                print(f"Tokens: {result['tokens']}")
                print(f"Sans stopwords: {result['tokens_no_stop']}")
                print(f"Nombre: {result['count']} (sans stopwords: {result['count_no_stop']})")
                print(f"Temps d'exécution: {result['execution_time']:.6f} secondes")

# ============================================================================
# INTERFACE EN LIGNE DE COMMANDE (CLI)
# ============================================================================
import argparse


def run_cli():
    """
    Fonction principale pour l'interface en ligne de commande.
    Permet d'utiliser le tokenizer directement depuis le terminal.
    """
    # Configuration du parser d'arguments
    parser = argparse.ArgumentParser(description='Tokeniseur de texte avec différentes méthodes')
    parser.add_argument('--text', type=str, help='Texte à tokeniser')
    parser.add_argument('--method', type=str, choices=['split', 'regex', 'nltk'], default='nltk',
                        help='Méthode de tokenisation à utiliser')
    parser.add_argument('--language', type=str, default='french', help='Langue pour les stopwords')
    parser.add_argument('--no-stopwords', action='store_true', help='Ne pas retirer les stopwords')
    parser.add_argument('--file', type=str, help='Fichier texte à tokeniser')

    # Analyse des arguments
    args = parser.parse_args()

    # Création du tokenizer avec la langue spécifiée
    tokenizer = Tokenizer(args.language)

    # Récupération du texte à tokeniser (fichier, argument ou saisie)
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"Erreur: Le fichier {args.file} n'existe pas.")
            return
    elif args.text:
        text = args.text
    else:
        # Si ni fichier ni texte n'est fourni, demander à l'utilisateur
        text = input("Entrez le texte à tokeniser: ")

    # Tokenisation du texte avec les paramètres spécifiés
    tokens = tokenizer.tokeniser_pipeline(
        text,
        method=args.method,
        remove_stops=not args.no_stopwords
    )

    # Affichage des résultats
    print(f"\nMéthode: {args.method}")
    print(f"Langue: {args.language}")
    print(f"Stopwords retirés: {not args.no_stopwords}")
    print(f"\nNombre de tokens: {len(tokens)}")
    print(f"\nTokens: {tokens}")

# Pour exécuter le CLI, décommentez la ligne suivante:
if __name__ == "__main__":
    run_cli()