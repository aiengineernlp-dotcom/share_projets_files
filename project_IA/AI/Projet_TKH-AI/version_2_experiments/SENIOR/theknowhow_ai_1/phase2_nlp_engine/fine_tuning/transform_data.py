"""
Script de transformation des données pour l'entraînement.
"""
import logging
import json
from pathlib import Path
from datetime import datetime
from data_loader import TrainingDataLoader
import re
from collections import Counter
import sys
import os
import sqlite3
import random
from textblob import TextBlob
from langdetect import detect
from typing import List, Dict
import spacy

# Ajout du répertoire racine au PYTHONPATH
project_root = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(project_root)

try:
    from config.reddit_config import SEARCH_TERMS
except ImportError:
    # Si l'import échoue, on utilise des valeurs par défaut
    SEARCH_TERMS = {
        'second_opinion': {
            'fr': ['avis', 'conseil', 'opinion'],
            'en': ['opinion', 'advice', 'help'],
            'ar': ['رأي', 'نصيحة', 'مساعدة']
        }
    }

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_data_from_sqlite(db_path: str) -> List[Dict]:
    """
    Charge les données depuis la base SQLite.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifie si la table posts existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
        if not cursor.fetchone():
            logging.error("La table 'posts' n'existe pas dans la base de données")
            return []

        # Extrait d'abord les mots-clés médicaux fréquents
        medical_keywords = extract_keywords_from_phase1()
        logging.info(f"Extracted {len(medical_keywords)} medical keywords from phase 1")

        # Sélectionne les entrées avec un titre ou un corps non vide
        cursor.execute("""
            SELECT title, body, medical_relevance_score, keywords, language 
            FROM posts 
            WHERE title IS NOT NULL OR body IS NOT NULL
        """)
        
        rows = cursor.fetchall()
        logging.info(f"Found {len(rows)} entries in database")
        
        conversations = []
        for row in rows:
            title, body, medical_relevance_score, keywords_str, language = row
            
            # Construction de la question à partir du titre et du corps
            question_parts = []
            if title:
                question_parts.append(title)
            if body:
                question_parts.append(body)
                
            if not question_parts:
                logging.warning("Question vide trouvée, ignorée")
                continue
                
            question = " - ".join(question_parts)
            
            # Extraction des mots-clés en utilisant notre système
            keywords = extract_keywords(question, medical_keywords)
            if not keywords:
                logging.warning(f"Aucun mot-clé extrait pour la question: {question[:100]}...")
            else:
                logging.info(f"Mots-clés extraits: {keywords}")
            
            # Valeurs par défaut pour les champs manquants
            medical_relevance_score = float(medical_relevance_score) if medical_relevance_score is not None else 0.0
            language = language if language else detect(question)  # Utilise langdetect si la langue n'est pas spécifiée
            
            conversations.append({
                'question': question,
                'keywords': keywords,
                'medical_relevance_score': medical_relevance_score,
                'language': language
            })
            
        conn.close()
        logging.info(f"Successfully loaded {len(conversations)} conversations")
        return conversations
        
    except sqlite3.Error as e:
        logging.error(f"Erreur SQLite lors du chargement des données : {e}")
        return []
    except Exception as e:
        logging.error(f"Erreur inattendue lors du chargement des données : {e}")
        return []

def extract_keywords_from_phase1():
    """Extrait les mots-clés fréquents des données de la phase 1."""
    try:
        # Liste de mots à exclure (stop words et mots communs non pertinents)
        stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 
                         'by', 'from', 'up', 'about', 'into', 'over', 'after', 'that', 'this', 'these', 'those',
                         'have', 'has', 'had', 'was', 'were', 'been', 'being', 'is', 'are', 'will', 'would',
                         'could', 'should', 'may', 'might', 'must', 'can', 'their', 'they', 'them', 'there',
                         'what', 'when', 'where', 'who', 'which', 'why', 'how', 'all', 'any', 'both', 'each',
                         'few', 'more', 'most', 'other', 'some', 'such', 'than', 'too', 'very', 'just', 'even',
                         'also', 'still', 'since', 'then', 'now', 'only', 'like', 'not', 'so', 'one', 'make',
                         'made', 'see', 'know', 'get', 'got', 'getting', 'think', 'going', 'went', 'gone',
                         'come', 'came', 'tell', 'told', 'said', 'say', 'says', 'feel', 'felt', 'feeling',
                         'want', 'wanted', 'need', 'needed', 'use', 'used', 'try', 'tried', 'trying'])

        # Mots-clés médicaux spécifiques à inclure
        medical_keywords = set([
            'pain', 'chronic', 'acute', 'symptoms', 'diagnosis', 'treatment', 'medication', 'surgery',
            'inflammation', 'infection', 'disease', 'condition', 'disorder', 'syndrome', 'injury',
            'emergency', 'severe', 'mild', 'moderate', 'critical', 'urgent', 'recurring', 'persistent',
            'doctor', 'specialist', 'hospital', 'clinic', 'examination', 'test', 'scan', 'mri', 'ct',
            'xray', 'ultrasound', 'blood test', 'urine test', 'biopsy', 'procedure', 'therapy',
            'recovery', 'healing', 'complication', 'side effect', 'allergic', 'reaction',
            'prescription', 'dosage', 'medical history', 'family history', 'genetic',
            'autoimmune', 'cancer', 'tumor', 'cyst', 'mass', 'growth', 'lesion', 'wound',
            'fracture', 'sprain', 'strain', 'swelling', 'inflammation', 'bleeding', 'bruising',
            'nausea', 'vomiting', 'diarrhea', 'constipation', 'fever', 'chills', 'fatigue',
            'weakness', 'dizziness', 'headache', 'migraine', 'seizure', 'tremor', 'numbness',
            'tingling', 'paralysis', 'stiffness', 'mobility', 'balance', 'coordination',
            'breathing', 'shortness of breath', 'cough', 'congestion', 'wheezing',
            'heart rate', 'blood pressure', 'pulse', 'circulation', 'swollen', 'tender',
            'sensitive', 'itching', 'burning', 'rash', 'hives', 'infection', 'bacterial',
            'viral', 'fungal', 'parasitic', 'chronic fatigue', 'fibromyalgia', 'arthritis',
            'diabetes', 'hypertension', 'asthma', 'copd', 'pneumonia', 'bronchitis',
            'gastritis', 'colitis', 'ibs', 'gerd', 'ulcer', 'hernia', 'appendicitis',
            'gallbladder', 'kidney stone', 'uti', 'std', 'hiv', 'hepatitis', 'thyroid',
            'hormone', 'vitamin deficiency', 'anemia', 'depression', 'anxiety', 'insomnia',
            'mental health', 'psychological', 'neurological', 'cognitive', 'memory loss',
            'confusion', 'disorientation', 'hallucination', 'delusion', 'psychosis',
            'bipolar', 'schizophrenia', 'ptsd', 'ocd', 'adhd', 'autism', 'developmental',
            'learning disability', 'speech', 'hearing loss', 'vision loss', 'blindness',
            'deafness', 'tinnitus', 'vertigo', 'balance disorder', 'multiple sclerosis',
            'parkinsons', 'alzheimers', 'dementia', 'stroke', 'tia', 'aneurysm',
            'heart attack', 'cardiac arrest', 'arrhythmia', 'palpitation', 'murmur',
            'chest pain', 'angina', 'high cholesterol', 'diabetes', 'prediabetes',
            'insulin', 'blood sugar', 'hypoglycemia', 'hyperglycemia', 'obesity',
            'malnutrition', 'eating disorder', 'anorexia', 'bulimia', 'dehydration',
            'electrolyte imbalance', 'mineral deficiency', 'osteoporosis', 'arthritis',
            'joint pain', 'muscle pain', 'back pain', 'neck pain', 'shoulder pain',
            'knee pain', 'hip pain', 'carpal tunnel', 'tendonitis', 'bursitis',
            'sciatica', 'herniated disc', 'spinal stenosis', 'scoliosis', 'fracture',
            'bone density', 'osteopenia', 'gout', 'lupus', 'rheumatoid arthritis',
            'psoriatic arthritis', 'fibromyalgia', 'chronic pain', 'neuropathy',
            'nerve pain', 'muscle weakness', 'atrophy', 'spasm', 'tremor', 'seizure',
            'epilepsy', 'concussion', 'head injury', 'brain injury', 'spinal cord injury',
            'paralysis', 'quadriplegia', 'paraplegia', 'amputation', 'prosthetic',
            'wheelchair', 'walker', 'cane', 'mobility aid', 'assistive device',
            'physical therapy', 'occupational therapy', 'speech therapy', 'rehabilitation',
            'recovery', 'prognosis', 'terminal', 'palliative', 'hospice', 'life expectancy',
            'quality of life', 'activities of daily living', 'independent living',
            'caregiver', 'support group', 'counseling', 'therapy', 'treatment plan',
            'second opinion', 'medical advice', 'consultation', 'referral', 'specialist',
            'primary care', 'emergency care', 'urgent care', 'intensive care', 'hospital',
            'clinic', 'outpatient', 'inpatient', 'admission', 'discharge', 'follow up',
            'health insurance', 'medical bill', 'prescription coverage', 'deductible',
            'copay', 'out of pocket', 'pre existing condition', 'disability', 'workers comp',
            'medical leave', 'fmla', 'ada accommodation', 'medical records', 'test results',
            'lab work', 'imaging', 'diagnostic', 'screening', 'preventive', 'routine',
            'annual', 'checkup', 'physical', 'wellness', 'lifestyle', 'diet', 'exercise',
            'nutrition', 'weight management', 'stress management', 'sleep hygiene',
            'meditation', 'relaxation', 'alternative medicine', 'complementary medicine',
            'holistic', 'natural', 'herbal', 'supplement', 'vitamin', 'mineral',
            'homeopathic', 'acupuncture', 'chiropractic', 'massage', 'yoga', 'tai chi',
            'meditation', 'mindfulness', 'biofeedback', 'hypnosis', 'counseling',
            'psychotherapy', 'cognitive behavioral therapy', 'group therapy',
            'family therapy', 'marriage counseling', 'grief counseling', 'support group'])

        # Charger les données de la base de données
        db_path = os.path.join(os.path.dirname(__file__), '../../phase1_data_collection/data/raw/social_media/reddit/sqlite/reddit.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Vérifier si la table 'posts' existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
        if not cursor.fetchone():
            logging.error("La table 'posts' n'existe pas dans la base de données")
            return []

        # Récupérer le texte de tous les posts
        cursor.execute("SELECT title, body FROM posts WHERE title IS NOT NULL OR body IS NOT NULL")
        posts = cursor.fetchall()

        # Fermer la connexion
        conn.close()

        # Traiter le texte et compter les mots
        word_freq = {}
        for title, body in posts:
            text = f"{title or ''} {body or ''}"
            # Nettoyer le texte
            text = re.sub(r'[^\w\s]', ' ', text.lower())
            words = text.split()
            
            # Compter les mots qui ne sont pas dans stop_words
            for word in words:
                if word not in stop_words and (len(word) > 2 or word in medical_keywords):
                    word_freq[word] = word_freq.get(word, 0) + 1

        # Ajouter les mots-clés médicaux avec une fréquence minimale
        for keyword in medical_keywords:
            if keyword not in word_freq:
                word_freq[keyword] = 1

        # Trier les mots par fréquence
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        # Filtrer les mots-clés pertinents
        keywords = []
        for word, freq in sorted_words:
            if freq >= 3 or word in medical_keywords:  # Ajuster le seuil de fréquence si nécessaire
                keywords.append(word)
                logging.info(f"Mot-clé médical extrait: {word} (fréquence: {freq})")

        logging.info(f"Nombre total de mots-clés médicaux extraits: {len(keywords)}")
        return keywords

    except Exception as e:
        logging.error(f"Erreur lors de l'extraction des mots-clés : {str(e)}")
        return []

def extract_keywords(text, medical_keywords):
    """Extrait les mots-clés importants du texte en utilisant la liste de mots-clés médicaux."""
    if not text:
        return []
        
    text = text.lower()
    keywords = []
    
    # Vérification des termes de recherche par catégorie et langue
    for category, languages in SEARCH_TERMS.items():
        for lang, terms in languages.items():
            for term in terms:
                if term.lower() in text:
                    keywords.append(term)
    
    # Extraction des mots-clés médicaux
    for word in medical_keywords:
        if word.lower() in text:
            keywords.append(word)
    
    # Suppression des doublons
    keywords = list(set(keywords))
    
    return keywords

def generate_personalized_response(question, keywords, language):
    """Génère une réponse personnalisée en fonction des mots-clés et de la langue"""
    if not keywords:
        logging.warning("Aucun mot-clé trouvé pour générer une réponse personnalisée")
        if language == 'fr':
            return "Je comprends votre inquiétude. Pour mieux vous aider, pourriez-vous me donner plus de détails sur vos symptômes ?"
        else:
            return "I understand your concern. Could you please provide more details about your symptoms so I can better assist you?"
    
    # Analyse des mots-clés pour déterminer le contexte
    context = {
        'symptoms': False,
        'diagnosis': False,
        'treatment': False,
        'emergency': False,
        'chronic': False
    }
    
    # Détermination du contexte en fonction des mots-clés
    for keyword in keywords:
        keyword = keyword.lower()
        if any(symptom in keyword for symptom in ['douleur', 'souffrance', 'fièvre', 'fatigue', 'nausée', 'vomissement']):
            context['symptoms'] = True
        elif any(diag in keyword for diag in ['diagnostic', 'examen', 'test', 'résultat']):
            context['diagnosis'] = True
        elif any(treat in keyword for treat in ['médicament', 'traitement', 'thérapie', 'opération']):
            context['treatment'] = True
        elif any(emerg in keyword for emerg in ['urgence', 'grave', 'sérieux', 'critique']):
            context['emergency'] = True
        elif any(chronic in keyword for chronic in ['chronique', 'persistant', 'récurent']):
            context['chronic'] = True
    
    # Génération de la réponse en fonction du contexte
    if language == 'fr':
        if context['emergency']:
            return "Votre situation semble nécessiter une attention médicale immédiate. Je vous recommande de vous rendre aux urgences ou de contacter immédiatement un médecin."
        elif context['symptoms'] and context['chronic']:
            return "Je comprends que vous souffrez de symptômes persistants. Il serait important de consulter un spécialiste pour une évaluation approfondie et un suivi régulier."
        elif context['diagnosis']:
            return "Pour établir un diagnostic précis, je vous conseille de consulter un médecin qui pourra vous prescrire les examens appropriés et interpréter les résultats."
        elif context['treatment']:
            return "Concernant votre traitement, il est essentiel d'en discuter avec votre médecin traitant qui pourra l'ajuster en fonction de votre situation spécifique."
        elif context['symptoms']:
            return "Je comprends que vous présentez des symptômes inquiétants. Je vous conseille de prendre rendez-vous avec votre médecin pour une évaluation complète."
        else:
            return "Je comprends votre inquiétude. Pour mieux vous aider, pourriez-vous me donner plus de détails sur votre situation médicale ?"
    else:
        if context['emergency']:
            return "Your situation seems to require immediate medical attention. I recommend going to the emergency room or contacting a doctor right away."
        elif context['symptoms'] and context['chronic']:
            return "I understand you're experiencing persistent symptoms. It would be important to consult a specialist for a thorough evaluation and regular follow-up."
        elif context['diagnosis']:
            return "To establish an accurate diagnosis, I advise you to consult a doctor who can prescribe appropriate tests and interpret the results."
        elif context['treatment']:
            return "Regarding your treatment, it's essential to discuss it with your primary care physician who can adjust it based on your specific situation."
        elif context['symptoms']:
            return "I understand you're experiencing concerning symptoms. I recommend making an appointment with your doctor for a complete evaluation."
        else:
            return "I understand your concern. Could you please provide more details about your medical situation so I can better assist you?"

def load_existing_data(file_path: Path) -> list:
    """Charge les données existantes d'un fichier JSON."""
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data_with_version(data: list, base_path: Path, timestamp: str):
    """Sauvegarde les données avec un horodatage."""
    # Création du chemin avec horodatage
    versioned_path = base_path.parent / f"{base_path.stem}_{timestamp}{base_path.suffix}"
    
    # Sauvegarde des données
    with open(versioned_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Données sauvegardées dans {versioned_path}")
    return versioned_path

def prepare_training_pairs(data: list) -> list:
    """Prépare les paires d'entraînement à partir des données brutes."""
    training_pairs = []
    for item in data:
        # Les données contiennent déjà une question formatée
        question = item.get('question', '').strip()
        logger.info(f"Question : {question[:100]}...")
        
        # Ne pas traiter les questions vides
        if not question:
            logger.warning("Question vide détectée, ignorée")
            continue
        
        # Utiliser la langue de l'item
        detected_lang = item.get('language', 'en')
        if detected_lang not in ['fr', 'en']:
            detected_lang = 'en'
        
        logger.info(f"Langue détectée : {detected_lang}")
        
        # Génération de la réponse personnalisée
        response = generate_personalized_response(question, item.get('keywords', []), detected_lang)
        logger.info(f"Réponse générée : {response[:100]}...")
        
        training_pairs.append({
            'question': question,
            'response': response,
            'medical_relevance_score': item.get('medical_relevance_score', 0.0),
            'keywords': item.get('keywords', [])
        })
    
    logger.info(f"Nombre total de paires d'entraînement générées : {len(training_pairs)}")
    return training_pairs

def main():
    """Fonction principale."""
    try:
        # Initialisation du logger
        logger = logging.getLogger(__name__)
        
        # Chargement de la configuration
        config_path = Path(__file__).parent / "data_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        logger.info("Configuration chargée depuis %s", config_path)
            
        # Chargement des données depuis la base SQLite...
        db_path = os.path.join(project_root, "phase1_data_collection/data/raw/social_media/reddit/sqlite/reddit.db")
        logger.info("Chargement des données depuis %s", db_path)
        data = load_data_from_sqlite(db_path)
        logger.info(f"{len(data)} conversations chargées avec succès")
        
        # Préparation des paires d'entraînement
        logger.info("Préparation des paires d'entraînement...")
        training_pairs = prepare_training_pairs(data)
        
        # Division des données (70% train, 15% validation, 15% test)
        random.shuffle(training_pairs)
        total = len(training_pairs)
        train_size = int(0.7 * total)
        val_size = int(0.15 * total)
        
        train_data = training_pairs[:train_size]
        val_data = training_pairs[train_size:train_size + val_size]
        test_data = training_pairs[train_size + val_size:]
        
        logger.info(f"Division des données : {len(train_data)} train, {len(val_data)} validation, {len(test_data)} test")
        
        # Création du dossier de sortie s'il n'existe pas
        output_dir = Path("data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Génération de l'horodatage
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarde des données avec versionnement
        logger.info("Données sauvegardées avec succès. Versions créées :")
        
        # Sauvegarde des paires d'entraînement
        pairs_path = output_dir / "training_pairs.json"
        pairs_versioned_path = save_data_with_version(training_pairs, pairs_path, timestamp)
        logger.info(f"- {pairs_versioned_path}")
        
        # Sauvegarde des données d'entraînement
        train_path = output_dir / "train_data.json"
        train_versioned_path = save_data_with_version(train_data, train_path, timestamp)
        logger.info(f"- {train_versioned_path}")
        
        # Sauvegarde des données de validation
        val_path = output_dir / "val_data.json"
        val_versioned_path = save_data_with_version(val_data, val_path, timestamp)
        logger.info(f"- {val_versioned_path}")
        
        # Sauvegarde des données de test
        test_path = output_dir / "test_data.json"
        test_versioned_path = save_data_with_version(test_data, test_path, timestamp)
        logger.info(f"- {test_versioned_path}")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du script : {str(e)}")
        raise

if __name__ == "__main__":
    main() 