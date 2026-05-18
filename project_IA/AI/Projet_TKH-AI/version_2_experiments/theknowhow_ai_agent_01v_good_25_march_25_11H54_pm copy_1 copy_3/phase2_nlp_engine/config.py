"""
Configuration du système NLP.
"""

from pathlib import Path

# Chemins des répertoires
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"

# Configuration du modèle
MODEL_CONFIG = {
    "base_model": "microsoft/BioGPT-large",
    "max_length": 512,
    "batch_size": 8,
    "learning_rate": 5e-5,
    "num_epochs": 3
} 