"""
Configuration pour l'entraînement du modèle.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class TrainingConfig:
    """Configuration pour l'entraînement du modèle."""
    
    # Paramètres du modèle
    model_name: str = "microsoft/BioGPT-large"
    tokenizer_name: Optional[str] = None
    
    # Paramètres d'entraînement
    batch_size: int = 4
    learning_rate: float = 5e-5
    num_epochs: int = 3
    warmup_steps: int = 500
    weight_decay: float = 0.01
    
    # Paramètres de génération
    max_length: int = 512
    num_beams: int = 4
    temperature: float = 0.7
    top_p: float = 0.9
    repetition_penalty: float = 1.2
    
    # Chemins
    output_dir: str = "models/fine_tuned"
    logging_dir: str = "logs"
    cache_dir: str = "cache"
    
    # Autres paramètres
    seed: int = 42
    fp16: bool = True
    gradient_accumulation_steps: int = 4
    save_steps: int = 1000
    eval_steps: int = 500
    logging_steps: int = 100
    
    def __post_init__(self):
        """Initialisation post-création."""
        if self.tokenizer_name is None:
            self.tokenizer_name = self.model_name 