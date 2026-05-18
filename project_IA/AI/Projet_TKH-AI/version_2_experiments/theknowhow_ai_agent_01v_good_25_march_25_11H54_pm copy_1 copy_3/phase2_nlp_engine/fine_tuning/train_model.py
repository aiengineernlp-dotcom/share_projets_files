"""
Script pour l'entraînement du modèle avec OLAMA.
"""
import os
import logging
import ollama
from training_config import TrainingConfig
from data_loader import TrainingDataLoader
from langdetect import detect

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("theknowhow_ai")

def get_system_prompt(lang):
    """Retourne le prompt système approprié selon la langue détectée."""
    prompts = {
        'fr': "Tu es un assistant médical qui aide les patients avec leurs questions de santé. Réponds toujours en français.",
        'en': "You are a medical assistant helping patients with their health questions. Always respond in English.",
        'ar': "أنت مساعد طبي يساعد المرضى في أسئلتهم الصحية. دائماً أجب باللغة العربية."
    }
    return prompts.get(lang, prompts['en'])  # Par défaut en anglais

def detect_language(text):
    """Détecte la langue du texte."""
    try:
        return detect(text)
    except:
        return 'en'  # Par défaut en anglais

def main():
    # Chargement de la configuration
    config = TrainingConfig()
    
    # Création des répertoires nécessaires
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.logging_dir, exist_ok=True)
    os.makedirs(config.cache_dir, exist_ok=True)
    
    # Chargement des données
    logger.info("Chargement des données...")
    data_loader = TrainingDataLoader()
    data = data_loader.load_data()
    split_data = data_loader.split_data(data)
    train_data = split_data['train']
    val_data = split_data['val']
    
    # Préparation des données pour l'entraînement
    logger.info("Préparation des données pour l'entraînement...")
    training_data = []
    for item in train_data:
        training_data.append({
            "input": item["text"],
            "output": data_loader._generate_expected_response(item)
        })
    
    # Configuration du modèle
    logger.info("Configuration du modèle...")
    model_name = "mistral"
    
    # Téléchargement du modèle
    logger.info("Téléchargement du modèle...")
    ollama.pull(model_name)
    
    # Entraînement du modèle
    logger.info("Démarrage de l'entraînement...")
    for epoch in range(config.num_epochs):
        logger.info(f"Époque {epoch + 1}/{config.num_epochs}")
        for item in training_data:
            # Détection de la langue
            lang = detect_language(item["input"])
            system_prompt = get_system_prompt(lang)
            
            response = ollama.generate(
                model=model_name,
                prompt=item["input"],
                system=system_prompt,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_ctx": 2048
                }
            )
            logger.info(f"Entraînement: {item['input'][:50]}...")
            logger.info(f"Réponse: {response.response[:100]}...")
    
    logger.info("Entraînement terminé avec succès!")

if __name__ == "__main__":
    main() 