"""
Module de base pour les modèles NLP.
"""
import logging
from typing import Dict, List, Optional

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class BaseNLPModel:
    """Classe de base pour les modèles NLP."""
    
    def __init__(self, model_name: str):
        """
        Initialise le modèle de base.
        
        Args:
            model_name (str): Nom du modèle pré-entraîné
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        
        # Initialisation du tokenizer et du modèle
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        # Configuration du token de padding
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.model.config.eos_token_id
            
    def generate(self, 
                prompt: str, 
                max_length: int = 100,
                num_return_sequences: int = 1,
                temperature: float = 0.7) -> List[str]:
        """
        Génère du texte à partir d'un prompt.
        
        Args:
            prompt (str): Texte d'entrée
            max_length (int): Longueur maximale de la sortie
            num_return_sequences (int): Nombre de séquences à générer
            temperature (float): Température pour la génération
            
        Returns:
            List[str]: Liste des textes générés
        """
        try:
            # Tokenization du prompt
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Génération
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=max_length,
                num_return_sequences=num_return_sequences,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id
            )
            
            # Décodage des sorties
            generated_texts = [
                self.tokenizer.decode(output, skip_special_tokens=True)
                for output in outputs
            ]
            
            return generated_texts
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération: {str(e)}")
            raise
            
    def encode(self, text: str) -> torch.Tensor:
        """
        Encode un texte en vecteur.
        
        Args:
            text (str): Texte à encoder
            
        Returns:
            torch.Tensor: Vecteur encodé
        """
        try:
            inputs = self.tokenizer(text, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                return outputs.hidden_states[-1][:, 0, :]  # [CLS] token
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'encodage: {str(e)}")
            raise
            
    def save(self, output_dir: str) -> None:
        """
        Sauvegarde le modèle.
        
        Args:
            output_dir (str): Répertoire de sortie
        """
        try:
            self.model.save_pretrained(output_dir)
            self.tokenizer.save_pretrained(output_dir)
            self.logger.info(f"Modèle sauvegardé dans {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            raise
            
    def load(self, model_dir: str) -> None:
        """
        Charge un modèle sauvegardé.
        
        Args:
            model_dir (str): Répertoire du modèle
        """
        try:
            self.model = AutoModelForCausalLM.from_pretrained(model_dir)
            self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
            self.logger.info(f"Modèle chargé depuis {model_dir}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement: {str(e)}")
            raise 