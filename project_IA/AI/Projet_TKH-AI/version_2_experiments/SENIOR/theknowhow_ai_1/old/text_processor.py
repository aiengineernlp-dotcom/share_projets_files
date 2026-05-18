"""
Module de prétraitement des textes médicaux.
"""

import re
import logging
from typing import List, Dict, Any
from datetime import datetime
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

class TextProcessor:
    """Classe pour le prétraitement des textes médicaux."""
    
    def __init__(self):
        """Initialise le processeur de texte."""
        self.spacy_available = False
        try:
            import spacy
            try:
                self.nlp = spacy.load('en_core_web_sm')
                self.spacy_available = True
                logger.info("SpaCy initialisé avec succès")
            except Exception as e:
                logger.warning(f"Impossible de charger le modèle spaCy: {e}")
                logger.warning("L'extraction d'entités médicales sera limitée")
        except ImportError:
            logger.warning("SpaCy n'est pas disponible, l'extraction d'entités médicales sera limitée")
            
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Mots à conserver même s'ils sont des stop words
        self.medical_stop_exceptions = {
            'no', 'not', 'nor', 'pain', 'cold', 'heart', 'blood'
        }
        self.stop_words = self.stop_words - self.medical_stop_exceptions
        
    def preprocess_text(self, text: str) -> str:
        """
        Prétraite un texte médical.
        
        Args:
            text: Texte à prétraiter
            
        Returns:
            Texte prétraité
        """
        if not text:
            return ""
            
        # Conversion en minuscules
        text = text.lower()
        
        # Suppression des URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Suppression des caractères spéciaux
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Suppression des chiffres isolés
        text = re.sub(r'\b\d+\b', '', text)
        
        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
        
    def extract_medical_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extrait les entités médicales du texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste des entités médicales trouvées
        """
        if not self.spacy_available:
            # Méthode alternative simple basée sur des mots-clés médicaux
            medical_keywords = [
                'pain', 'symptom', 'disease', 'treatment', 'doctor', 'hospital',
                'medication', 'drug', 'diagnosis', 'surgery', 'blood', 'heart',
                'cancer', 'diabetes', 'fever', 'headache', 'allergy', 'infection'
            ]
            entities = []
            text_lower = text.lower()
            for keyword in medical_keywords:
                if keyword in text_lower:
                    start = text_lower.find(keyword)
                    entities.append({
                        'text': keyword,
                        'label': 'MEDICAL_TERM',
                        'start': start,
                        'end': start + len(keyword)
                    })
            return entities
        
        # Si spaCy est disponible, utiliser l'extraction d'entités avancée
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            if ent.label_ in {'DISEASE', 'SYMPTOM', 'TREATMENT', 'BODY_PART', 'DRUG'}:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
                
        return entities
        
    def tokenize_and_clean(self, text: str) -> List[str]:
        """
        Tokenize et nettoie un texte.
        
        Args:
            text: Texte à tokenizer
            
        Returns:
            Liste de tokens nettoyés
        """
        # Tokenization
        tokens = word_tokenize(text)
        
        # Nettoyage et lemmatisation
        cleaned_tokens = []
        for token in tokens:
            # Ignore les stop words sauf exceptions médicales
            if token in self.stop_words:
                continue
                
            # Lemmatisation
            lemma = self.lemmatizer.lemmatize(token)
            cleaned_tokens.append(lemma)
            
        return cleaned_tokens
        
    def process_medical_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite un post médical complet.
        
        Args:
            post_data: Données du post à traiter
            
        Returns:
            Post traité avec métadonnées enrichies
        """
        processed_data = post_data.copy()
        
        # Prétraitement du titre et du contenu
        processed_data['processed_title'] = self.preprocess_text(post_data.get('title', ''))
        processed_data['processed_content'] = self.preprocess_text(post_data.get('content', ''))
        
        # Extraction des entités médicales
        title_entities = self.extract_medical_entities(post_data.get('title', ''))
        content_entities = self.extract_medical_entities(post_data.get('content', ''))
        processed_data['medical_entities'] = {
            'title': title_entities,
            'content': content_entities
        }
        
        # Tokenization et nettoyage
        processed_data['tokens'] = {
            'title': self.tokenize_and_clean(processed_data['processed_title']),
            'content': self.tokenize_and_clean(processed_data['processed_content'])
        }
        
        # Ajout des métadonnées de traitement
        processed_data['preprocessing_metadata'] = {
            'processed_at': datetime.utcnow().timestamp(),
            'num_entities': len(title_entities) + len(content_entities),
            'num_tokens': len(processed_data['tokens']['title']) + len(processed_data['tokens']['content']),
            'spacy_available': self.spacy_available
        }
        
        return processed_data 