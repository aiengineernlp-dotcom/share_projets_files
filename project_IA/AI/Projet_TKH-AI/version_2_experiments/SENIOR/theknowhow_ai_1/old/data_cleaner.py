"""
Module de nettoyage et structuration des données
"""
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from langdetect import detect
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging

# Configurer le logger directement au lieu d'utiliser app.utils.logger
logger = logging.getLogger("data_cleaner")

class DataCleaner:
    """Classe pour le nettoyage et la structuration des données"""
    
    def __init__(self):
        # Chargement des modèles et ressources
        try:
            import nltk
            nltk.download("punkt")
            nltk.download("stopwords")
            
            # Vérifier si spaCy est disponible
            self.spacy_available = False
            try:
                import spacy
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    self.spacy_available = True
                    logger.info("SpaCy initialisé avec succès")
                except Exception as e:
                    logger.warning(f"Impossible de charger le modèle spaCy: {e}")
                    logger.warning("L'extraction d'entités sera limitée")
            except ImportError:
                logger.warning("SpaCy n'est pas disponible, l'extraction d'entités sera limitée")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du DataCleaner: {e}")
            raise
            
    def clean_text(self, text: str) -> str:
        """
        Nettoie un texte
        
        Args:
            text: Texte à nettoyer
            
        Returns:
            str: Texte nettoyé
        """
        if not text:
            return ""
            
        # Suppression du HTML
        text = BeautifulSoup(text, "html.parser").get_text()
        
        # Normalisation des espaces
        text = re.sub(r"\s+", " ", text)
        
        # Suppression des caractères spéciaux
        text = re.sub(r"[^\w\s]", "", text)
        
        return text.strip()
        
    def remove_stopwords(self, text: str, language: str = "en") -> str:
        """
        Supprime les mots vides
        
        Args:
            text: Texte à traiter
            language: Code de langue
            
        Returns:
            str: Texte sans mots vides
        """
        try:
            stop_words = set(stopwords.words(language))
            words = word_tokenize(text)
            filtered_words = [word for word in words if word.lower() not in stop_words]
            return " ".join(filtered_words)
        except Exception as e:
            logger.warning(f"Erreur lors de la suppression des mots vides: {e}")
            return text
            
    def detect_language(self, text: str) -> Optional[str]:
        """
        Détecte la langue d'un texte
        
        Args:
            text: Texte à analyser
            
        Returns:
            Optional[str]: Code de langue ou None
        """
        try:
            return detect(text)
        except:
            return None
            
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extrait les entités nommées
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict[str, List[str]]: Entités par type
        """
        if not self.spacy_available:
            # Méthode alternative simple basée sur des mots-clés médicaux
            medical_keywords = {
                'DISEASE': ['cancer', 'diabetes', 'asthma', 'arthritis', 'hypertension'],
                'SYMPTOM': ['pain', 'fever', 'headache', 'cough', 'fatigue'],
                'TREATMENT': ['surgery', 'medication', 'therapy', 'vaccine', 'antibiotic'],
                'BODY_PART': ['heart', 'lung', 'brain', 'liver', 'kidney'],
                'DRUG': ['aspirin', 'ibuprofen', 'paracetamol', 'insulin', 'antibiotic']
            }
            
            entities = {}
            text_lower = text.lower()
            
            for entity_type, keywords in medical_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        if entity_type not in entities:
                            entities[entity_type] = []
                        entities[entity_type].append(keyword)
            
            return entities
        
        try:
            doc = self.nlp(text)
            entities = {}
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)
            return entities
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des entités: {e}")
            return {}
            
    def standardize_date(self, date_str: str) -> Optional[datetime]:
        """
        Standardise un format de date
        
        Args:
            date_str: Date en chaîne
            
        Returns:
            Optional[datetime]: Date standardisée ou None
        """
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%m-%d-%Y"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        return None
        
    def clean_medical_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nettoie des données médicales
        
        Args:
            data: Données à nettoyer
            
        Returns:
            Dict[str, Any]: Données nettoyées
        """
        cleaned = {}
        
        try:
            # Nettoyage des champs textuels
            for field in ["content", "title", "description"]:
                if field in data:
                    cleaned[field] = self.clean_text(data[field])
                    
            # Détection de la langue
            if "content" in cleaned:
                cleaned["language"] = self.detect_language(cleaned["content"])
                
            # Extraction des entités
            if "content" in cleaned:
                cleaned["entities"] = self.extract_entities(cleaned["content"])
                
            # Standardisation des dates
            for field in ["date", "created_at", "updated_at"]:
                if field in data and isinstance(data[field], str):
                    cleaned[field] = self.standardize_date(data[field])
                    
            # Conservation des métadonnées
            for field in ["id", "url", "author", "source"]:
                if field in data:
                    cleaned[field] = data[field]
                    
            # Ajout de la date de nettoyage
            cleaned["cleaned_at"] = datetime.now()
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des données: {e}")
            return data
            
        return cleaned
        
    def clean_dataset(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Nettoie un ensemble de données
        
        Args:
            dataset: Liste de données à nettoyer
            
        Returns:
            List[Dict[str, Any]]: Données nettoyées
        """
        cleaned_data = []
        
        for item in dataset:
            try:
                cleaned_item = self.clean_medical_data(item)
                if cleaned_item:
                    cleaned_data.append(cleaned_item)
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage d'un élément: {e}")
                continue
                
        return cleaned_data
        
    def remove_duplicates(self, dataset: List[Dict[str, Any]],
                         key_fields: List[str]) -> List[Dict[str, Any]]:
        """
        Supprime les doublons
        
        Args:
            dataset: Données à dédupliquer
            key_fields: Champs à utiliser pour la déduplication
            
        Returns:
            List[Dict[str, Any]]: Données dédupliquées
        """
        try:
            df = pd.DataFrame(dataset)
            df = df.drop_duplicates(subset=key_fields, keep="first")
            return df.to_dict("records")
        except Exception as e:
            logger.error(f"Erreur lors de la déduplication: {e}")
            return dataset 