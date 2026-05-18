"""
Fonctions utilitaires.
Code source extrait de phase__traitement_du_langage_naturel.py (lignes 201-350 : utilitaires)
"""

from typing import Any, Dict, List, Optional, Set, Union
import re
from datetime import datetime
from collections import Counter

# Fonctions de traitement de texte
def clean_text(text: str) -> str:
    """Nettoie le texte en supprimant les caractères spéciaux et en normalisant les espaces.
    
    Args:
        text (str): Texte à nettoyer
        
    Returns:
        str: Texte nettoyé
    """
    if not isinstance(text, str):
        return ""
    
    # Suppression des caractères spéciaux
    text = re.sub(r'[^\w\s]', ' ', text)
    # Normalisation des espaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def normalize_text(text: str) -> str:
    """Normalise le texte en minuscules et standardise les caractères accentués.
    
    Args:
        text (str): Texte à normaliser
        
    Returns:
        str: Texte normalisé
    """
    if not isinstance(text, str):
        return ""
    
    # Conversion en minuscules
    text = text.lower()
    # Standardisation des caractères accentués
    text = text.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
    text = text.replace('à', 'a').replace('â', 'a')
    text = text.replace('î', 'i').replace('ï', 'i')
    text = text.replace('ô', 'o').replace('ö', 'o')
    text = text.replace('û', 'u').replace('ü', 'u')
    return text

def tokenize_text(text: str) -> List[str]:
    """Découpe le texte en tokens.
    
    Args:
        text (str): Texte à tokeniser
        
    Returns:
        List[str]: Liste des tokens
    """
    if not isinstance(text, str):
        return []
    
    return text.split()

def remove_stopwords(text: str, stopwords: Set[str]) -> str:
    """Supprime les mots vides du texte.
    
    Args:
        text (str): Texte à traiter
        stopwords (Set[str]): Ensemble des mots vides
        
    Returns:
        str: Texte sans les mots vides
    """
    if not isinstance(text, str):
        return ""
    
    words = text.split()
    return ' '.join(word for word in words if word not in stopwords)

def extract_ngrams(text: str, n: int) -> List[str]:
    """Extrait les n-grammes du texte.
    
    Args:
        text (str): Texte à traiter
        n (int): Taille des n-grammes
        
    Returns:
        List[str]: Liste des n-grammes
    """
    if not isinstance(text, str):
        return []
    
    words = text.split()
    return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]

def count_word_frequencies(text: str) -> Dict[str, int]:
    """Compte la fréquence des mots dans le texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        Dict[str, int]: Dictionnaire des fréquences
    """
    if not isinstance(text, str):
        return {}
    
    return dict(Counter(text.split()))

def extract_phrases(text: str) -> List[str]:
    """Extrait les phrases du texte.
    
    Args:
        text (str): Texte à traiter
        
    Returns:
        List[str]: Liste des phrases
    """
    if not isinstance(text, str):
        return []
    
    return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

def calculate_text_metrics(text: str) -> Dict[str, Union[int, float]]:
    """Calcule diverses métriques du texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        Dict[str, Union[int, float]]: Dictionnaire des métriques
    """
    if not isinstance(text, str):
        return {
            'char_count': 0,
            'word_count': 0,
            'sentence_count': 0,
            'avg_word_length': 0.0,
            'avg_sentence_length': 0.0
        }
    
    sentences = extract_phrases(text)
    words = text.split()
    
    return {
        'char_count': len(text),
        'word_count': len(words),
        'sentence_count': len(sentences),
        'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0.0,
        'avg_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0.0
    }

def extract_hashtags(text: str) -> List[str]:
    """Extrait les hashtags du texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        List[str]: Liste des hashtags
    """
    if not isinstance(text, str):
        return []
    
    return re.findall(r'#\w+', text)

def extract_mentions(text: str) -> List[str]:
    """Extrait les mentions du texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        List[str]: Liste des mentions
    """
    if not isinstance(text, str):
        return []
    
    return re.findall(r'@\w+', text)

def extract_urls(text: str) -> List[str]:
    """Extrait les URLs du texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        List[str]: Liste des URLs
    """
    if not isinstance(text, str):
        return []
    
    return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

def remove_urls(text: str) -> str:
    """Supprime les URLs du texte.
    
    Args:
        text (str): Texte à traiter
        
    Returns:
        str: Texte sans les URLs
    """
    if not isinstance(text, str):
        return ""
    
    return re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

def extract_emojis(text: str) -> List[str]:
    """Extrait les emojis du texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        List[str]: Liste des emojis
    """
    if not isinstance(text, str):
        return []
    
    return re.findall(r'[\U0001F300-\U0001F9FF]', text)

def remove_emojis(text: str) -> str:
    """Supprime les emojis du texte.
    
    Args:
        text (str): Texte à traiter
        
    Returns:
        str: Texte sans les emojis
    """
    if not isinstance(text, str):
        return ""
    
    return re.sub(r'[\U0001F300-\U0001F9FF]', '', text)

def extract_numbers(text: str) -> List[str]:
    """Extrait les nombres du texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        List[str]: Liste des nombres
    """
    if not isinstance(text, str):
        return []
    
    return re.findall(r'\d+', text)

def remove_numbers(text: str) -> str:
    """Supprime les nombres du texte.
    
    Args:
        text (str): Texte à traiter
        
    Returns:
        str: Texte sans les nombres
    """
    if not isinstance(text, str):
        return ""
    
    return re.sub(r'\d+', '', text)

def extract_punctuation(text: str) -> List[str]:
    """Extrait la ponctuation du texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        List[str]: Liste des signes de ponctuation
    """
    if not isinstance(text, str):
        return []
    
    return re.findall(r'[^\w\s]', text)

def remove_punctuation(text: str) -> str:
    """Supprime la ponctuation du texte.
    
    Args:
        text (str): Texte à traiter
        
    Returns:
        str: Texte sans la ponctuation
    """
    if not isinstance(text, str):
        return ""
    
    return re.sub(r'[^\w\s]', '', text)

def extract_whitespace(text: str) -> List[str]:
    """Extrait les espaces du texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        List[str]: Liste des espaces
    """
    if not isinstance(text, str):
        return []
    
    return re.findall(r'\s+', text)

def normalize_whitespace(text: str) -> str:
    """Normalise les espaces dans le texte.
    
    Args:
        text (str): Texte à traiter
        
    Returns:
        str: Texte avec les espaces normalisés
    """
    if not isinstance(text, str):
        return ""
    
    return re.sub(r'\s+', ' ', text).strip()

# Fonctions de validation
def validate_text(text: str) -> bool:
    """Valide si le texte est valide.
    
    Args:
        text (str): Texte à valider
        
    Returns:
        bool: True si le texte est valide
    """
    return isinstance(text, str) and len(text.strip()) > 0

def validate_text_length(text: str, min_length: int = 1, max_length: Optional[int] = None) -> bool:
    """Valide la longueur du texte.
    
    Args:
        text (str): Texte à valider
        min_length (int): Longueur minimale
        max_length (Optional[int]): Longueur maximale
        
    Returns:
        bool: True si la longueur est valide
    """
    if not validate_text(text):
        return False
    
    length = len(text.strip())
    if length < min_length:
        return False
    
    if max_length is not None and length > max_length:
        return False
    
    return True

def validate_text_content(text: str, allowed_chars: Optional[Set[str]] = None) -> bool:
    """Valide le contenu du texte.
    
    Args:
        text (str): Texte à valider
        allowed_chars (Optional[Set[str]]): Caractères autorisés
        
    Returns:
        bool: True si le contenu est valide
    """
    if not validate_text(text):
        return False
    
    if allowed_chars is not None:
        return all(char in allowed_chars for char in text)
    
    return True

def validate_text_pattern(text: str, pattern: str) -> bool:
    """Valide le texte selon un pattern.
    
    Args:
        text (str): Texte à valider
        pattern (str): Pattern à vérifier
        
    Returns:
        bool: True si le texte correspond au pattern
    """
    if not validate_text(text):
        return False
    
    return bool(re.match(pattern, text))

def validate_text_language(text: str, language: str) -> bool:
    """Valide la langue du texte.
    
    Args:
        text (str): Texte à valider
        language (str): Langue attendue
        
    Returns:
        bool: True si la langue est valide
    """
    if not validate_text(text):
        return False
    
    # TODO: Implémenter la validation de la langue
    return True

def validate_text_encoding(text: str, encoding: str = 'utf-8') -> bool:
    """Valide l'encodage du texte.
    
    Args:
        text (str): Texte à valider
        encoding (str): Encodage attendu
        
    Returns:
        bool: True si l'encodage est valide
    """
    if not validate_text(text):
        return False
    
    try:
        text.encode(encoding)
        return True
    except UnicodeEncodeError:
        return False

def validate_text_sentiment(sentiment: Dict[str, float]) -> bool:
    """Valide les valeurs de sentiment.
    
    Args:
        sentiment (Dict[str, float]): Valeurs de sentiment
        
    Returns:
        bool: True si les valeurs sont valides
    """
    if not isinstance(sentiment, dict):
        return False
    
    required_keys = {'polarity', 'subjectivity'}
    if not all(key in sentiment for key in required_keys):
        return False
    
    if not isinstance(sentiment['polarity'], (int, float)):
        return False
    
    if not isinstance(sentiment['subjectivity'], (int, float)):
        return False
    
    if not -1 <= sentiment['polarity'] <= 1:
        return False
    
    if not 0 <= sentiment['subjectivity'] <= 1:
        return False
    
    return True

def validate_text_urgency(urgency: Dict[str, Any]) -> bool:
    """Valide les valeurs d'urgence.
    
    Args:
        urgency (Dict[str, Any]): Valeurs d'urgence
        
    Returns:
        bool: True si les valeurs sont valides
    """
    if not isinstance(urgency, dict):
        return False
    
    required_keys = {'level', 'score', 'confidence'}
    if not all(key in urgency for key in required_keys):
        return False
    
    if not isinstance(urgency['level'], str):
        return False
    
    if not isinstance(urgency['score'], (int, float)):
        return False
    
    if not isinstance(urgency['confidence'], (int, float)):
        return False
    
    if not 0 <= urgency['score'] <= 1:
        return False
    
    if not 0 <= urgency['confidence'] <= 1:
        return False
    
    return True

def validate_text_location(location: Dict[str, Any]) -> bool:
    """Valide les informations de localisation.
    
    Args:
        location (Dict[str, Any]): Informations de localisation
        
    Returns:
        bool: True si les informations sont valides
    """
    if not isinstance(location, dict):
        return False
    
    required_keys = {'country', 'city', 'coordinates', 'confidence'}
    if not all(key in location for key in required_keys):
        return False
    
    if not isinstance(location['country'], str):
        return False
    
    if not isinstance(location['city'], str):
        return False
    
    if not isinstance(location['coordinates'], tuple):
        return False
    
    if len(location['coordinates']) != 2:
        return False
    
    if not all(isinstance(coord, (int, float)) for coord in location['coordinates']):
        return False
    
    if not isinstance(location['confidence'], (int, float)):
        return False
    
    if not 0 <= location['confidence'] <= 1:
        return False
    
    return True

def validate_text_entities(entities: List[Dict[str, Any]]) -> bool:
    """Valide les entités extraites.
    
    Args:
        entities (List[Dict[str, Any]]): Liste des entités
        
    Returns:
        bool: True si les entités sont valides
    """
    if not isinstance(entities, list):
        return False
    
    required_keys = {'text', 'label', 'start', 'end'}
    
    for entity in entities:
        if not isinstance(entity, dict):
            return False
        
        if not all(key in entity for key in required_keys):
            return False
        
        if not isinstance(entity['text'], str):
            return False
        
        if not isinstance(entity['label'], str):
            return False
        
        if not isinstance(entity['start'], int):
            return False
        
        if not isinstance(entity['end'], int):
            return False
        
        if entity['start'] < 0 or entity['end'] <= entity['start']:
            return False
    
    return True

def validate_text_keywords(keywords: List[str]) -> bool:
    """Valide les mots-clés extraits.
    
    Args:
        keywords (List[str]): Liste des mots-clés
        
    Returns:
        bool: True si les mots-clés sont valides
    """
    if not isinstance(keywords, list):
        return False
    
    return all(isinstance(keyword, str) and len(keyword.strip()) > 0 for keyword in keywords)

def validate_text_metrics(metrics: Dict[str, Union[int, float]]) -> bool:
    """Valide les métriques du texte.
    
    Args:
        metrics (Dict[str, Union[int, float]]): Métriques du texte
        
    Returns:
        bool: True si les métriques sont valides
    """
    if not isinstance(metrics, dict):
        return False
    
    required_keys = {'char_count', 'word_count', 'sentence_count', 'avg_word_length', 'avg_sentence_length'}
    if not all(key in metrics for key in required_keys):
        return False
    
    if not all(isinstance(value, (int, float)) for value in metrics.values()):
        return False
    
    if not all(value >= 0 for value in metrics.values()):
        return False
    
    return True

def validate_text_timestamp(timestamp: str) -> bool:
    """Valide le timestamp.
    
    Args:
        timestamp (str): Timestamp à valider
        
    Returns:
        bool: True si le timestamp est valide
    """
    if not isinstance(timestamp, str):
        return False
    
    try:
        datetime.fromisoformat(timestamp)
        return True
    except ValueError:
        return False

def validate_text_confidence(confidence: float) -> bool:
    """Valide le score de confiance.
    
    Args:
        confidence (float): Score de confiance
        
    Returns:
        bool: True si le score est valide
    """
    if not isinstance(confidence, (int, float)):
        return False
    
    return 0 <= confidence <= 1

def validate_text_severity(severity: str) -> bool:
    """Valide le niveau de sévérité.
    
    Args:
        severity (str): Niveau de sévérité
        
    Returns:
        bool: True si le niveau est valide
    """
    if not isinstance(severity, str):
        return False
    
    valid_levels = {'CRITIQUE', 'SÉVÈRE', 'MODÉRÉ', 'LÉGER', 'AUCUN'}
    return severity in valid_levels

def validate_text_zone(zone: str) -> bool:
    """Valide la zone géographique.
    
    Args:
        zone (str): Zone géographique
        
    Returns:
        bool: True si la zone est valide
    """
    if not isinstance(zone, str):
        return False
    
    valid_zones = {'GCC', 'AFRIQUE', 'NON DÉTERMINÉE'}
    return zone in valid_zones 