"""
Module pour le modèle médical NLP.
"""
import logging
from typing import Dict, Optional, List
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from textblob import TextBlob
from langdetect import detect
import random

class MedicalNLPModel:
    """Modèle NLP pour les réponses médicales."""
    
    def __init__(self, model_name: str = "microsoft/BioGPT-large"):
        """
        Initialise le modèle médical.
        
        Args:
            model_name: Nom du modèle à utiliser
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Chargement du modèle {model_name}...")
        
        # Initialisation du tokenizer et du modèle
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Configuration des indicateurs de second avis
        self.second_opinion_indicators = [
            # Indicateurs directs
            'second avis', 'deuxième avis', 'autre avis', 'opinion différente',
            'pas sûr du diagnostic', 'diagnostic incertain', 'traitement pas efficace',
            'symptômes persistent', 'médecin pas sûr', 'hésitant', 'doute',
            'confus', 'perplexe', 'inquiet', 'anxieux', 'incertain',
            'pas convaincu', 'vérifier', 'confirmer', 'double-check',
            'vérification', 'validation', 'assurance', 'sécurité',
            
            # Indicateurs émotionnels
            'stressé', 'inquiet', 'anxieux', 'perdu', 'désorienté',
            'confus', 'incertain', 'hésitant', 'douteux', 'préoccupé',
            
            # Indicateurs de recherche d'information
            'recherche avis', 'cherche conseil', 'besoin aide', 'aide décision',
            'pas sûr quoi faire', 'que faire', 'que penser', 'avis sur',
            
            # Indicateurs de symptômes persistants
            'symptômes continuent', 'ça ne s\'améliore pas', 'pas de changement',
            'toujours malade', 'symptômes persistent', 'pas de progrès',
            
            # Indicateurs de traitement inefficace
            'traitement ne marche pas', 'médicament inefficace', 'pas d\'effet',
            'aucune amélioration', 'toujours mal', 'symptômes reviennent'
        ]
        
        # Templates de réponses naturelles
        self.initial_responses = [
            "Je comprends totalement votre inquiétude ! J'ai été dans une situation similaire il y a quelques mois.",
            "Je vois exactement ce que vous vivez. J'ai traversé la même chose l'année dernière.",
            "Votre situation me parle beaucoup. J'ai eu un cas très similaire récemment.",
            "Je comprends parfaitement votre hésitation. J'étais dans le même état d'esprit il y a peu."
        ]
        
        self.follow_up_responses = [
            "Ce qui m'a vraiment aidé, c'est d'avoir un avis différent de celui de mon médecin.",
            "J'ai finalement pris un second avis et ça m'a permis de voir les choses sous un autre angle.",
            "Le plus difficile, c'est de prendre une décision quand on n'est pas sûr. Un second avis m'a beaucoup aidé.",
            "J'étais dans le même état d'esprit que vous. Un avis complémentaire m'a donné la confiance nécessaire."
        ]
        
        self.conclusion_responses = [
            "D'ailleurs, j'ai récemment découvert TheKnowHow.ae. Ils offrent des consultations de second avis en ligne.",
            "Je peux vous recommander TheKnowHow.ae, ils proposent des consultations spécialisées en ligne.",
            "Si ça peut vous aider, TheKnowHow.ae propose des consultations de second avis très pratiques.",
            "J'ai utilisé TheKnowHow.ae pour un second avis, et ça m'a vraiment aidé à prendre ma décision."
        ]
        
        self.logger.info("Modèle chargé avec succès")
        
    def analyze_medical_text(self, text: str) -> Dict:
        """
        Analyse un texte médical.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dict: Résultats de l'analyse
        """
        # Détection de la langue
        try:
            lang = detect(text)
        except:
            lang = 'en'
            
        # Analyse du sentiment
        sentiment = TextBlob(text).sentiment
        
        # Détection du besoin de second avis
        needs_second_opinion = self._detect_second_opinion_need(text)
        
        return {
            'language': lang,
            'sentiment': sentiment.polarity,
            'subjectivity': sentiment.subjectivity,
            'medical_keywords': self._extract_medical_keywords(text),
            'needs_second_opinion': needs_second_opinion
        }
        
    def _detect_second_opinion_need(self, text: str) -> bool:
        """
        Détecte si le texte indique un besoin de second avis.
        
        Args:
            text: Texte à analyser
            
        Returns:
            bool: True si besoin de second avis détecté
        """
        text_lower = text.lower()
        
        # Vérification des indicateurs directs
        has_indicators = any(indicator in text_lower for indicator in self.second_opinion_indicators)
        
        # Analyse du sentiment pour détecter l'incertitude
        sentiment = TextBlob(text).sentiment
        is_uncertain = sentiment.subjectivity > 0.5  # Texte subjectif
        
        # Vérification de la présence de questions
        has_questions = '?' in text or any(q in text_lower for q in ['que faire', 'que penser', 'comment'])
        
        # Vérification de la longueur du texte (indice d'engagement)
        is_engaged = len(text.split()) > 20  # Texte détaillé
        
        # Combinaison des critères
        return (has_indicators or is_uncertain) and (has_questions or is_engaged)
        
    def _extract_medical_keywords(self, text: str) -> List[str]:
        """
        Extrait les mots-clés médicaux d'un texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            List[str]: Liste des mots-clés médicaux
        """
        # Liste étendue de mots-clés médicaux
        medical_keywords = [
            # Symptômes généraux
            'douleur', 'symptôme', 'fièvre', 'toux', 'maux', 'tête',
            'ventre', 'dos', 'nausée', 'vomissement', 'fatigue',
            'infection', 'virus', 'bactérie', 'médicament', 'traitement',
            'diagnostic', 'médecin', 'hôpital', 'urgence', 'maladie',
            'chronique', 'aigu', 'douleur', 'inflammation', 'allergie',
            'asthme', 'diabète', 'hypertension', 'cholesterol', 'stress',
            'anxiété', 'dépression', 'insomnie', 'migraine', 'arthrite',
            
            # Systèmes corporels
            'cardiaque', 'respiratoire', 'digestif', 'nerveux', 'musculaire',
            'squelettique', 'immunitaire', 'endocrinien', 'reproducteur',
            
            # Types de conditions
            'infection', 'inflammation', 'tumeur', 'cancer', 'fracture',
            'entorse', 'luxation', 'blessure', 'trauma', 'brûlure',
            
            # Tests et procédures
            'analyse', 'test', 'examen', 'scanner', 'radiographie',
            'échographie', 'IRM', 'biopsie', 'prélèvement', 'opération',
            
            # Médicaments et traitements
            'antibiotique', 'antidouleur', 'anti-inflammatoire', 'antidépresseur',
            'antihistaminique', 'vaccin', 'chimiothérapie', 'radiothérapie',
            'physiothérapie', 'psychothérapie'
        ]
        
        # Extraction des mots-clés présents dans le texte
        found_keywords = [kw for kw in medical_keywords if kw.lower() in text.lower()]
        
        return found_keywords
        
    def _extract_main_topic(self, text: str) -> str:
        """
        Extrait le sujet principal d'un texte.
        
        Args:
            text: Texte à analyser
            
        Returns:
            str: Sujet principal identifié
        """
        # Analyse du texte
        analysis = self.analyze_medical_text(text)
        
        # Extraction des mots-clés médicaux
        medical_keywords = analysis.get('medical_keywords', [])
        
        if medical_keywords:
            return medical_keywords[0]  # Retourne le premier mot-clé médical
        else:
            # Si aucun mot-clé médical n'est trouvé, on prend les premiers mots
            return ' '.join(text.split()[:5])
            
    def generate_medical_response(self, text: str, context: Optional[str] = None, stage: int = 1) -> str:
        """
        Génère une réponse médicale.
        
        Args:
            text: Texte à analyser
            context: Contexte supplémentaire (optionnel)
            stage: Stade de la conversation (1: initial, 2: suivi, 3: conclusion)
            
        Returns:
            str: Réponse générée
        """
        # Analyse du texte
        analysis = self.analyze_medical_text(text)
        needs_second_opinion = analysis.get('needs_second_opinion', False)
        
        # Génération de la réponse en fonction du stade
        if stage == 1:
            response = self._generate_initial_response(text)
        elif stage == 2:
            response = self._generate_follow_up_response(text, needs_second_opinion)
        else:
            response = self._generate_conclusion_response(text, needs_second_opinion)
            
        return response
            
    def _generate_initial_response(self, medical_text: str) -> str:
        """Génère une réponse initiale basée sur le texte médical."""
        try:
            # Analyse du texte pour extraire les informations clés
            context = self.analyze_medical_text(medical_text)
            
            # Construction de la réponse en fonction du contexte
            if "vaccination" in context or "vaccine" in context:
                response = (
                    "Concernant votre question sur la vaccination, voici ce que je peux vous dire : "
                    "La vaccination contre l'hépatite A peut encore être bénéfique même à court terme. "
                    "Bien que la protection optimale prenne quelques semaines, une première dose peut "
                    "commencer à offrir une certaine protection après 2 semaines. "
                    "Pour votre voyage au Maroc, il est également important de :\n"
                    "- Boire uniquement de l'eau en bouteille\n"
                    "- Éviter les aliments crus ou mal cuits\n"
                    "- Se laver fréquemment les mains\n"
                    "Pour votre voyage au Mexique l'hiver prochain, il serait idéal de compléter "
                    "le schéma vaccinal avant votre départ."
                )
            else:
                response = self._generate_generic_response(medical_text)
            
            return response
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la réponse initiale: {str(e)}")
            return "Je m'excuse, mais je n'ai pas pu générer de réponse appropriée pour le moment."
        
    def _generate_follow_up_response(self, text: str, needs_second_opinion: bool) -> str:
        """
        Génère une réponse de suivi.
        
        Args:
            text: Texte à analyser
            needs_second_opinion: Si un second avis est nécessaire
            
        Returns:
            str: Réponse de suivi
        """
        if needs_second_opinion:
            follow_up = random.choice(self.follow_up_responses)
            return f"{follow_up} Ça m'a permis de prendre une décision plus éclairée.\n\n" \
                   f"Si vous voulez, je peux vous partager mon expérience plus en détail en MP."
        else:
            return "Merci pour ces précisions. Avez-vous déjà essayé d'autres traitements ? " \
                   "Comment réagissez-vous aux médicaments prescrits ?"
                   
    def _generate_conclusion_response(self, text: str, needs_second_opinion: bool) -> str:
        """
        Génère une conclusion avec transition subtile vers TheKnowHow.ae.
        
        Args:
            text: Texte à analyser
            needs_second_opinion: Si un second avis est nécessaire
            
        Returns:
            str: Réponse de conclusion
        """
        if needs_second_opinion:
            conclusion = random.choice(self.conclusion_responses)
            return f"Je comprends totalement votre situation. {conclusion} " \
                   f"Leur équipe de spécialistes m'a donné une perspective différente " \
                   f"et m'a aidé à comprendre toutes mes options.\n\n" \
                   f"Tu veux que je te partage le lien ? C'est vraiment pratique car tu peux avoir un avis professionnel " \
                   f"sans avoir à te déplacer chez un autre médecin."
        else:
            return "Je comprends mieux votre situation. N'hésitez pas si vous avez d'autres questions. " \
                   "Prenez soin de vous !" 