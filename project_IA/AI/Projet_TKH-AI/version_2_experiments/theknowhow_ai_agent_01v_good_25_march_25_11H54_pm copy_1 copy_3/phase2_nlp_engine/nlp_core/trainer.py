"""
Module d'entraînement pour le modèle médical NLP.
"""
import logging
from typing import List, Tuple, Dict
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    EarlyStoppingCallback
)
from datasets import Dataset
import numpy as np
from sklearn.model_selection import KFold
import gc

class MedicalModelTrainer:
    """Classe pour l'entraînement du modèle médical."""
    
    def __init__(self, model_name: str, output_dir: str):
        """
        Initialise le trainer.
        
        Args:
            model_name: Nom du modèle à utiliser
            output_dir: Répertoire de sortie
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.output_dir = output_dir
        
        # Détection du type de GPU et configuration optimale
        if torch.cuda.is_available():
            self.device = "cuda"
            self.use_fp16 = True
            torch.backends.cudnn.benchmark = True  # Optimisation CUDA
            torch.cuda.empty_cache()  # Nettoyage de la mémoire CUDA
        elif torch.backends.mps.is_available():
            self.device = "mps"
            self.use_fp16 = False
        else:
            self.device = "cpu"
            self.use_fp16 = False
            
        self.logger.info(f"Utilisation du device: {self.device} (fp16: {self.use_fp16})")
        
        # Initialisation optimisée du tokenizer et du modèle
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if self.use_fp16 else torch.float32,
            low_cpu_mem_usage=True,
            device_map="auto" if self.device == "cuda" else None,
            gradient_checkpointing=True  # Activation du gradient checkpointing
        ).to(self.device)
        
        # Configuration du token de padding
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.model.config.eos_token_id
            
    def _prepare_dataset(self, data: List[Tuple[str, str]], max_samples: int = 100) -> Dataset:
        """
        Prépare un dataset pour l'entraînement ou l'évaluation.
        
        Args:
            data: Liste de tuples (entrée, sortie)
            max_samples: Nombre maximum d'échantillons à utiliser
            
        Returns:
            Dataset: Dataset formaté pour l'entraînement
        """
        # Limitation du nombre d'échantillons
        if len(data) > max_samples:
            indices = np.random.choice(len(data), max_samples, replace=False)
            data = [data[i] for i in indices]
            
        # Tokenization optimisée des données
        encodings = self.tokenizer(
            [pair[0] for pair in data],  # Entrées
            [pair[1] for pair in data],  # Sorties
            truncation=True,
            max_length=256,  # Longueur optimisée
            padding="max_length",
            return_tensors="pt"
        )
        
        # Conversion optimisée en numpy
        dataset = Dataset.from_dict({
            'input_ids': encodings['input_ids'].cpu().numpy(),
            'attention_mask': encodings['attention_mask'].cpu().numpy(),
            'labels': encodings['input_ids'].cpu().numpy().copy()
        })
        
        # Nettoyage de la mémoire
        del encodings
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        return dataset
            
    def optimize_hyperparameters(self, 
                               train_data: List[Tuple[str, str]],
                               val_size: float = 0.2,
                               num_trials: int = 5) -> Dict:
        """
        Optimise les hyperparamètres du modèle avec validation croisée.
        
        Args:
            train_data: Données d'entraînement
            val_size: Proportion des données pour la validation
            num_trials: Nombre d'essais pour l'optimisation
            
        Returns:
            Dict: Meilleurs hyperparamètres trouvés
        """
        self.logger.info("Début de l'optimisation des hyperparamètres")
        
        # Configuration de la validation croisée
        kf = KFold(n_splits=3, shuffle=True, random_state=42)
        train_indices = np.arange(len(train_data))
        
        # Plages de valeurs optimisées
        learning_rates = [1e-5, 2e-5, 5e-5]
        batch_sizes = [4, 8, 16]
        num_epochs = [2, 3, 4]
        
        best_params = None
        best_val_loss = float('inf')
        
        for _ in range(num_trials):
            # Sélection optimisée des hyperparamètres
            lr = np.random.choice(learning_rates)
            bs = int(np.random.choice(batch_sizes))
            epochs = int(np.random.choice(num_epochs))
            
            # Validation croisée
            cv_losses = []
            for train_idx, val_idx in kf.split(train_indices):
                train_subset = [train_data[i] for i in train_idx]
                val_subset = [train_data[i] for i in val_idx]
                
                val_loss = self._train_with_params(train_subset, val_subset, lr, bs, epochs)
                cv_losses.append(val_loss)
                
                # Nettoyage de la mémoire après chaque fold
                gc.collect()
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            # Moyenne des pertes de validation
            avg_val_loss = np.mean(cv_losses)
            
            # Mise à jour des meilleurs paramètres
            if avg_val_loss < best_val_loss:
                best_val_loss = avg_val_loss
                best_params = {
                    'learning_rate': lr,
                    'batch_size': bs,
                    'num_epochs': epochs
                }
                
        self.logger.info(f"Meilleurs hyperparamètres trouvés: {best_params}")
        return best_params
        
    def _train_with_params(self,
                          train_data: List[Tuple[str, str]],
                          val_data: List[Tuple[str, str]],
                          learning_rate: float,
                          batch_size: int,
                          num_epochs: int) -> float:
        """
        Entraîne le modèle avec des paramètres spécifiques et retourne la perte de validation.
        
        Args:
            train_data: Données d'entraînement
            val_data: Données de validation
            learning_rate: Taux d'apprentissage
            batch_size: Taille du batch
            num_epochs: Nombre d'époques
            
        Returns:
            float: Perte de validation
        """
        # Préparation optimisée des datasets
        train_dataset = self._prepare_dataset(train_data)
        val_dataset = self._prepare_dataset(val_data)
        
        # Configuration optimisée de l'entraînement
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            logging_steps=10,
            save_steps=50,
            fp16=self.use_fp16,
            gradient_accumulation_steps=4,
            warmup_ratio=0.1,
            dataloader_drop_last=True,
            weight_decay=0.01,
            max_grad_norm=1.0,
            optim="adamw_torch",
            lr_scheduler_type="cosine",
            report_to="none",
            gradient_checkpointing=True,  # Activation du gradient checkpointing
            load_best_model_at_end=True,  # Chargement du meilleur modèle
            metric_for_best_model="eval_loss",  # Métrique pour le meilleur modèle
            greater_is_better=False  # La perte doit être minimisée
        )
        
        # Initialisation optimisée du trainer avec early stopping
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]  # Early stopping
        )
        
        # Entraînement optimisé
        trainer.train()
        
        # Évaluation finale
        eval_results = trainer.evaluate()
        
        # Nettoyage de la mémoire
        del trainer
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        return eval_results['eval_loss']
        
    def train(self, 
              train_data: List[Tuple[str, str]],
              num_epochs: int = 2,
              batch_size: int = 4,
              learning_rate: float = 2e-5,
              optimize: bool = True) -> None:
        """
        Entraîne le modèle.
        
        Args:
            train_data: Données d'entraînement
            num_epochs: Nombre d'époques
            batch_size: Taille du batch
            learning_rate: Taux d'apprentissage
            optimize: Si True, optimise les hyperparamètres
        """
        try:
            if optimize:
                # Optimisation des hyperparamètres
                best_params = self.optimize_hyperparameters(train_data)
                num_epochs = best_params['num_epochs']
                batch_size = best_params['batch_size']
                learning_rate = best_params['learning_rate']
                
            # Préparation optimisée du dataset
            train_dataset = self._prepare_dataset(train_data)
            
            # Configuration optimisée de l'entraînement
            training_args = TrainingArguments(
                output_dir=self.output_dir,
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                learning_rate=learning_rate,
                logging_steps=10,
                save_steps=50,
                fp16=self.use_fp16,
                gradient_accumulation_steps=4,
                warmup_ratio=0.1,
                dataloader_drop_last=True,
                weight_decay=0.01,
                max_grad_norm=1.0,
                optim="adamw_torch",
                lr_scheduler_type="cosine",
                report_to="none",
                gradient_checkpointing=True,
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False
            )
            
            # Initialisation du trainer avec early stopping
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=3)]
            )
            
            # Entraînement
            trainer.train()
            
            # Sauvegarde du modèle
            trainer.save_model()
            
            # Nettoyage de la mémoire
            del trainer
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'entraînement : {str(e)}")
            raise 