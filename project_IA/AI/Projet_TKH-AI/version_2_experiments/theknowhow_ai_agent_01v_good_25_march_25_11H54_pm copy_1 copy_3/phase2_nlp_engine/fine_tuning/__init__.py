"""
Module d'entraînement et de fine-tuning des modèles.
"""
from ..nlp_core.trainer import MedicalModelTrainer as ModelTrainer
from .training_config import TrainingConfig
from .data_loader import TrainingDataLoader

__all__ = [
    'ModelTrainer',
    'TrainingConfig',
    'TrainingDataLoader'
] 