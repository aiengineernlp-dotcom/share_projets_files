"""
Générateur de réponses pour les posts Reddit.
"""
import logging
from typing import Dict, List, Optional
import random
from datetime import datetime

class ResponseGenerator:
    """Générateur de réponses pour les posts Reddit."""
    
    def __init__(self, config: dict):
        """
        Initialise le générateur de réponses.
        
        Args:
            config: Configuration du bot
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def generate_response(self, post: Dict, analysis: Dict) -> str:
        """
        Génère une réponse appropriée pour un post.
        
        Args:
            post: Post original
            analysis: Résultats de l'analyse du post
            
        Returns:
            str: Réponse générée
        """
        try:
            # Sélection du template de base en fonction du sujet
            base_template = self._select_base_template(analysis['topic'])
            
            # Personnalisation de la réponse
            response = self._personalize_response(
                base_template,
                post,
                analysis
            )
            
            # Ajout d'une signature naturelle
            if random.random() < 0.7:  # 70% de chance d'ajouter une signature
                response += self._generate_natural_signature()
                
            return response
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de la réponse: {str(e)}")
            return "Je suis désolé, je ne peux pas générer de réponse appropriée pour le moment."
            
    def _select_base_template(self, topic: str) -> str:
        """
        Sélectionne un template de base en fonction du sujet.
        
        Args:
            topic: Sujet du post
            
        Returns:
            str: Template de base
        """
        templates = {
            'vaccination': (
                "Je comprends vos préoccupations concernant la vaccination. "
                "Il est important de noter que {specific_info}. "
                "Pour votre situation, {personalized_advice}. "
                "N'hésitez pas à me poser des questions supplémentaires."
            ),
            'symptômes': (
                "Je vois que vous décrivez des symptômes. "
                "Il est important de noter que {specific_info}. "
                "Dans votre cas, {personalized_advice}. "
                "Souhaitez-vous en discuter plus en détail ?"
            ),
            'diagnostic': (
                "Je comprends votre inquiétude concernant le diagnostic. "
                "Il est important de noter que {specific_info}. "
                "Pour votre situation, {personalized_advice}. "
                "Voulez-vous partager plus d'informations ?"
            ),
            'traitement': (
                "Je vois que vous avez des questions sur le traitement. "
                "Il est important de noter que {specific_info}. "
                "Dans votre cas, {personalized_advice}. "
                "Avez-vous d'autres questions ?"
            ),
            'prévention': (
                "Je comprends votre intérêt pour la prévention. "
                "Il est important de noter que {specific_info}. "
                "Pour votre situation, {personalized_advice}. "
                "N'hésitez pas à me demander plus d'informations."
            ),
            'général': (
                "Je comprends vos préoccupations concernant {topic}. "
                "Il est important de noter que {specific_info}. "
                "Dans votre cas, {personalized_advice}. "
                "Souhaitez-vous en discuter plus en détail ?"
            )
        }
        
        return templates.get(topic, templates['général'])
        
    def _personalize_response(self, template: str, post: Dict, analysis: Dict) -> str:
        """
        Personnalise la réponse en fonction du post et de son analyse.
        
        Args:
            template: Template de base
            post: Post original
            analysis: Résultats de l'analyse
            
        Returns:
            str: Réponse personnalisée
        """
        # Extraction des informations spécifiques
        specific_info = self._extract_specific_info(post, analysis)
        
        # Génération de conseils personnalisés
        personalized_advice = self._generate_personalized_advice(post, analysis)
        
        # Remplacement des placeholders
        response = template.format(
            specific_info=specific_info,
            personalized_advice=personalized_advice,
            topic=analysis['topic']
        )
        
        return response
        
    def _extract_specific_info(self, post: Dict, analysis: Dict) -> str:
        """
        Extrait des informations spécifiques du post.
        
        Args:
            post: Post original
            analysis: Résultats de l'analyse
            
        Returns:
            str: Informations spécifiques
        """
        content = f"{post['title']} {post['content']}".lower()
        
        # Extraction des informations en fonction du sujet
        if analysis['topic'] == 'vaccination':
            return self._extract_vaccination_info(content)
        elif analysis['topic'] == 'symptômes':
            return self._extract_symptoms_info(content)
        elif analysis['topic'] == 'diagnostic':
            return self._extract_diagnosis_info(content)
        elif analysis['topic'] == 'traitement':
            return self._extract_treatment_info(content)
        elif analysis['topic'] == 'prévention':
            return self._extract_prevention_info(content)
            
        return "chaque situation est unique et nécessite une évaluation personnalisée"
        
    def _generate_personalized_advice(self, post: Dict, analysis: Dict) -> str:
        """
        Génère des conseils personnalisés en fonction du post et de son analyse.
        
        Args:
            post: Post original
            analysis: Résultats de l'analyse
            
        Returns:
            str: Conseils personnalisés
        """
        # Adaptation du ton en fonction du sentiment
        tone = "rassurant" if analysis['sentiment'] == 'negative' else "informé"
        
        # Adaptation en fonction de l'urgence
        if analysis['urgency_level'] == 'high':
            return f"je vous conseille de {tone} consulter rapidement un professionnel de santé"
        elif analysis['urgency_level'] == 'medium':
            return f"je vous suggère de {tone} prendre rendez-vous avec votre médecin"
            
        return f"je vous recommande de {tone} discuter de cela avec votre médecin lors de votre prochaine consultation"
        
    def _generate_natural_signature(self) -> str:
        """
        Génère une signature naturelle pour la réponse.
        
        Returns:
            str: Signature naturelle
        """
        signatures = [
            "\n\nJ'espère que ces informations vous seront utiles.",
            "\n\nN'hésitez pas si vous avez d'autres questions.",
            "\n\nPrenez soin de vous.",
            "\n\nBonne journée à vous."
        ]
        
        return random.choice(signatures)
        
    def _extract_vaccination_info(self, content: str) -> str:
        """
        Extrait des informations spécifiques sur la vaccination.
        
        Args:
            content: Contenu du post
            
        Returns:
            str: Informations sur la vaccination
        """
        if 'hépatite' in content:
            return "le vaccin contre l'hépatite A nécessite généralement deux doses espacées de 6 mois pour une protection optimale"
        elif 'grippe' in content:
            return "le vaccin contre la grippe est recommandé chaque année, particulièrement pour les personnes à risque"
            
        return "les vaccins sont un moyen important de prévention des maladies"
        
    def _extract_symptoms_info(self, content: str) -> str:
        """
        Extrait des informations spécifiques sur les symptômes.
        
        Args:
            content: Contenu du post
            
        Returns:
            str: Informations sur les symptômes
        """
        if 'fièvre' in content:
            return "la fièvre est un symptôme non spécifique qui peut avoir de nombreuses causes"
        elif 'douleur' in content:
            return "les douleurs peuvent avoir des origines très diverses"
            
        return "les symptômes doivent toujours être évalués dans leur contexte global"
        
    def _extract_diagnosis_info(self, content: str) -> str:
        """
        Extrait des informations spécifiques sur le diagnostic.
        
        Args:
            content: Contenu du post
            
        Returns:
            str: Informations sur le diagnostic
        """
        if 'test' in content:
            return "les tests médicaux doivent être interprétés dans leur contexte clinique"
        elif 'résultat' in content:
            return "les résultats médicaux nécessitent une expertise professionnelle pour être correctement interprétés"
            
        return "un diagnostic médical nécessite une évaluation complète par un professionnel de santé"
        
    def _extract_treatment_info(self, content: str) -> str:
        """
        Extrait des informations spécifiques sur le traitement.
        
        Args:
            content: Contenu du post
            
        Returns:
            str: Informations sur le traitement
        """
        if 'antibiotique' in content:
            return "les antibiotiques doivent être utilisés de manière appropriée pour éviter la résistance"
        elif 'médicament' in content:
            return "les médicaments doivent être pris selon les prescriptions médicales"
            
        return "le traitement doit être adapté à chaque situation individuelle"
        
    def _extract_prevention_info(self, content: str) -> str:
        """
        Extrait des informations spécifiques sur la prévention.
        
        Args:
            content: Contenu du post
            
        Returns:
            str: Informations sur la prévention
        """
        if 'voyage' in content:
            return "la préparation aux voyages nécessite une planification adaptée à la destination"
        elif 'alimentation' in content:
            return "une alimentation équilibrée est un pilier important de la prévention"
            
        return "la prévention est un aspect essentiel de la santé" 