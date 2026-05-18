"""
Module de traitement du langage naturel.
"""
import spacy
import logging
from typing import Dict, List, Any

class TextProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.logger = logging.getLogger(__name__)

    def process_text(self, text: str) -> Dict[str, Any]:
        """
        Traite un texte avec NLP.
        """
        doc = self.nlp(text)
        return {
            'entities': [(ent.text, ent.label_) for ent in doc.ents],
            'tokens': [token.text for token in doc],
            'sentences': [str(sent) for sent in doc.sents]
        }

    def extract_medical_terms(self, text: str) -> List[str]:
        """
        Extrait les termes médicaux du texte.
        """
        doc = self.nlp(text)
        medical_terms = []
        for ent in doc.ents:
            if ent.label_ in ['CONDITION', 'SYMPTOM', 'TREATMENT']:
                medical_terms.append(ent.text)
        return medical_terms 