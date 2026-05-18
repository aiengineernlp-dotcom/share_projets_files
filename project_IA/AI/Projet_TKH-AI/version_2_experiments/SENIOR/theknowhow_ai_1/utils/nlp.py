"""
Module pour le traitement du langage naturel.
"""

from typing import Tuple, Dict, Any, List, Union
import re
import spacy
from langdetect import detect
import logging
from phase1_data_collection.nlp.keywords.medical_terms import (
    SPECIALIZED_CASES,
    SURGICAL_SPECIALTIES,
    MEDICAL_SPECIALTIES,
    SECOND_OPINION_INDICATORS
)

# Configuration du logging
logger = logging.getLogger(__name__)

# Chargement des modèles spaCy
try:
    nlp_fr = spacy.load("fr_core_news_lg")
    logger.info("Modèle français chargé avec succès")
except Exception as e:
    logger.warning(f"Erreur lors du chargement du modèle français large : {e}")
    try:
        nlp_fr = spacy.load("fr_core_news_md")
        logger.info("Modèle français medium chargé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle français : {e}")
        raise

try:
    nlp_en = spacy.load("en_core_web_lg")
    logger.info("Modèle anglais chargé avec succès")
except Exception as e:
    logger.warning(f"Erreur lors du chargement du modèle anglais large : {e}")
    try:
        nlp_en = spacy.load("en_core_web_md")
        logger.info("Modèle anglais medium chargé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle anglais : {e}")
        raise

def is_valid_location(text: str) -> bool:
    """Vérifie si le texte est une localisation valide.
    
    Args:
        text (str): Texte à vérifier
        
    Returns:
        bool: True si c'est une localisation valide, False sinon
    """
    # Liste de mots à exclure (médicaments, termes médicaux, etc.)
    invalid_words = {
        'er', 'mri', 'ct', 'usa', 'us', 'uk', 'pa', 'va', 'md', 'nc',
        'brca', 'xarelto', 'plavix', 'klonopin', 'clonazepam',
        'nuero', 'anhedonia', 'ptsd', 'mdma', 'inr', 'ef', 'tldr',
        'https', 'http', 'www', 'com', 'org', 'net',
        'images', 'image', 'img', 'jpg', 'jpeg', 'png', 'gif'
    }
    
    # Vérifie si le texte est dans la liste des mots invalides
    if text.lower() in invalid_words:
        logger.debug(f"Texte exclu car dans la liste des mots invalides : {text}")
        return False
    
    # Vérifie si le texte contient des chiffres ou des caractères spéciaux
    if re.search(r'[0-9/]', text):
        logger.debug(f"Texte exclu car contient des chiffres ou caractères spéciaux : {text}")
        return False
    
    # Vérifie si le texte est trop court (moins de 2 caractères)
    if len(text) < 2:
        logger.debug(f"Texte exclu car trop court : {text}")
        return False
    
    return True

def detect_location(text: str) -> Dict[str, List[str]]:
    """Détecte les pays et les villes dans le texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        Dict[str, List[str]]: Dictionnaire contenant les pays et villes détectés
    """
    # Détection de la langue
    lang = detect_language(text)
    
    # Sélection du modèle approprié
    nlp = nlp_fr if lang == 'fr' else nlp_en
    logger.info(f"Utilisation du modèle {'français' if lang == 'fr' else 'anglais'}")
    
    doc = nlp(text)
    locations = {
        "countries": [],
        "cities": []
    }
    
    # Liste des pays du GCC (en français et en anglais) avec leurs variantes
    gcc_countries = {
        "fr": {
            "Arabie Saoudite": ["arabie", "saoudite", "arabie saoudite"],
            "Émirats Arabes Unis": ["emirats", "eau", "émirats arabes unis"],
            "Koweït": ["koweit", "koweït"],
            "Bahreïn": ["bahrein", "bahreïn"],
            "Oman": ["oman"],
            "Qatar": ["qatar"]
        },
        "en": {
            "Saudi Arabia": ["saudi", "arabia", "saudi arabia", "ksa"],
            "United Arab Emirates": ["uae", "emirates", "united arab emirates"],
            "Kuwait": ["kuwait"],
            "Bahrain": ["bahrain"],
            "Oman": ["oman"],
            "Qatar": ["qatar"]
        }
    }
    
    # Sélection de la liste appropriée
    current_gcc_countries = gcc_countries['fr'] if lang == 'fr' else gcc_countries['en']
    logger.info(f"Liste des pays GCC utilisée : {list(current_gcc_countries.keys())}")
    
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:  # GPE = Geo-Political Entity, LOC = Location
            # Nettoyage du texte
            location_text = ent.text.strip()
            logger.debug(f"Entité géographique détectée : {location_text} (type: {ent.label_})")
            
            # Vérifie si c'est une localisation valide
            if not is_valid_location(location_text):
                continue
            
            # Vérifie si c'est un pays du GCC
            for country, variants in current_gcc_countries.items():
                if any(variant in location_text.lower() for variant in variants):
                    if country not in locations["countries"]:
                        locations["countries"].append(country)
                        logger.info(f"Pays du GCC détecté : {country} (variante trouvée : {location_text})")
                    break
            else:  # Si ce n'est pas un pays du GCC
                # Vérifie si c'est une ville (en général, les villes sont plus courtes)
                if len(location_text.split()) <= 2 and location_text not in locations["cities"]:
                    locations["cities"].append(location_text)
                    logger.debug(f"Ville détectée : {location_text}")
    
    logger.info(f"Résultats de la détection : {locations}")
    return locations

def categorize_post(text_or_dict: Union[str, Dict[str, Any]]) -> Tuple[str, float]:
    """
    Catégorise un post en fonction de son contenu médical et émotionnel.
    
    Args:
        text_or_dict: Texte du post ou dictionnaire contenant 'title' et 'selftext'
        
    Returns:
        Tuple[str, float]: (catégorie, score)
    """
    # Extraire le texte si c'est un dictionnaire
    if isinstance(text_or_dict, dict):
        text = f"{text_or_dict.get('title', '')} {text_or_dict.get('selftext', '')}"
    else:
        text = text_or_dict
        
    # Détecter la langue
    lang = detect_language(text)
    
    # Sélectionner le modèle spaCy approprié
    nlp = nlp_fr if lang == 'fr' else nlp_en
    doc = nlp(text)
    
    # Initialiser les scores
    scores = {
        'critical_second_opinion': 0.0,
        'high_priority_second_opinion': 0.0,
        'medium_priority_second_opinion': 0.0,
        'low_priority_second_opinion': 0.0,
        'general_medical_question': 0.0,
        'non_medical': 0.0
    }
    
    # Analyse des entités nommées
    medical_entities = [ent.text for ent in doc.ents if ent.label_ in ['DISEASE', 'BODY_PART', 'MEDICAL_TERM']]
    
    # Analyse des dépendances syntaxiques
    for token in doc:
        # Détection des relations de cause à effet
        if token.dep_ == 'mark' and token.head.dep_ == 'advcl':
            if any(word in token.head.text.lower() for word in ['because', 'since', 'as']):
                scores['critical_second_opinion'] += 0.2
                scores['high_priority_second_opinion'] += 0.1
        
        # Détection des expressions d'urgence
        if token.dep_ == 'advmod' and token.head.pos_ == 'VERB':
            if token.text.lower() in ['urgently', 'immediately', 'asap']:
                scores['critical_second_opinion'] += 0.3
                scores['high_priority_second_opinion'] += 0.2
        
        # Détection des expressions de doute
        if token.dep_ == 'neg' or (token.dep_ == 'advmod' and token.text.lower() in ['maybe', 'perhaps', 'possibly']):
            scores['high_priority_second_opinion'] += 0.1
            scores['medium_priority_second_opinion'] += 0.1
    
    # Analyse des phrases complètes
    for sent in doc.sents:
        # Détection des questions
        if sent.root.dep_ == 'ROOT' and sent.root.pos_ == 'VERB':
            if sent.root.text.lower() in ['should', 'could', 'would', 'must']:
                scores['high_priority_second_opinion'] += 0.2
                scores['medium_priority_second_opinion'] += 0.1
        
        # Détection des expressions d'émotion
        for token in sent:
            if token.pos_ == 'ADJ' and token.dep_ == 'acomp':
                if token.text.lower() in ['worried', 'concerned', 'anxious', 'scared']:
                    scores['critical_second_opinion'] += 0.2
                    scores['high_priority_second_opinion'] += 0.1
    
    # Analyse des mots-clés médicaux avec contexte
    for category, keywords in SPECIALIZED_CASES.items():
        for word in keywords.get(lang, keywords['en']):
            if word.lower() in text.lower():
                # Vérifier le contexte du mot-clé
                for sent in doc.sents:
                    if word.lower() in sent.text.lower():
                        # Analyse du contexte de la phrase
                        if any(emotion in sent.text.lower() for emotion in ['urgent', 'emergency', 'critical']):
                            scores['critical_second_opinion'] += 0.4
                        elif any(emotion in sent.text.lower() for emotion in ['worried', 'concerned', 'anxious']):
                            scores['high_priority_second_opinion'] += 0.3
                        else:
                            scores['medium_priority_second_opinion'] += 0.2
    
    # Analyse des indicateurs de seconde opinion avec contexte
    for word in SECOND_OPINION_INDICATORS.get(lang, SECOND_OPINION_INDICATORS['en']):
        if word.lower() in text.lower():
            for sent in doc.sents:
                if word.lower() in sent.text.lower():
                    # Analyse du contexte de la phrase
                    if any(emotion in sent.text.lower() for emotion in ['urgent', 'emergency', 'critical']):
                        scores['critical_second_opinion'] += 0.3
                    elif any(emotion in sent.text.lower() for emotion in ['worried', 'concerned', 'anxious']):
                        scores['high_priority_second_opinion'] += 0.3
                    else:
                        scores['medium_priority_second_opinion'] += 0.2
    
    # Normaliser les scores
    total = sum(scores.values())
    if total > 0:
        for key in scores:
            scores[key] /= total
    
    # Déterminer la catégorie finale avec plus de nuance
    if scores['critical_second_opinion'] >= 0.7:
        return "Critical Priority - Second Opinion", scores['critical_second_opinion']
    elif scores['high_priority_second_opinion'] >= 0.5:
        return "High Priority - Second Opinion", scores['high_priority_second_opinion']
    elif scores['medium_priority_second_opinion'] >= 0.3:
        return "Medium Priority - Second Opinion", scores['medium_priority_second_opinion']
    elif scores['low_priority_second_opinion'] > 0:
        return "Low Priority - Second Opinion", scores['low_priority_second_opinion']
    elif scores['general_medical_question'] > 0:
        return "General Medical Question", scores['general_medical_question']
    else:
        return "Non-Medical Content", 0.0

def detect_language(text: str) -> str:
    """
    Détecte la langue du texte.
    
    Args:
        text (str): Texte à analyser
        
    Returns:
        str: Code de la langue détectée ('fr' ou 'en')
    """
    try:
        if not text or len(text.strip()) == 0:
            logger.warning("Texte vide ou nul fourni à detect_language")
            return 'en'
            
        lang = detect(text)
        logger.info(f"Langue détectée : {lang}")
        return lang
    except Exception as e:
        logger.error(f"Erreur lors de la détection de la langue : {str(e)}")
        logger.error(f"Texte qui a causé l'erreur : {text[:100]}...")  # Log les 100 premiers caractères
        return 'en'  # Par défaut en anglais

def detect_entities(text: str, language: str) -> Dict[str, List[str]]:
    """Détecte les entités nommées dans le texte"""
    nlp = nlp_fr if language == "fr" else nlp_en
    doc = nlp(text)
    
    entities = {
        "countries": [],
        "cities": []
    }
    
    for ent in doc.ents:
        if ent.label_ == "GPE":
            if is_valid_location(ent.text):
                entities["cities"].append(ent.text)
            
    return entities

def evaluate_urgency(text: str, language: str) -> float:
    """Évalue l'urgence d'un texte"""
    nlp = nlp_fr if language == "fr" else nlp_en
    doc = nlp(text)
    
    # Mots-clés d'urgence avec leurs poids
    urgency_keywords = {
        'emergency': 1.0, 'urgent': 0.9, 'critical': 0.9,
        'severe': 0.8, 'serious': 0.8, 'immediately': 0.8,
        'pain': 0.7, 'worried': 0.6, 'concerned': 0.6,
        'help': 0.5, 'advice': 0.4, 'question': 0.3
    }
    
    score = 0.0
    word_count = 0
    
    for token in doc:
        if token.text.lower() in urgency_keywords:
            score += urgency_keywords[token.text.lower()]
            word_count += 1
    
    if word_count > 0:
        return min(1.0, score / word_count)
    return 0.3  # Score par défaut

def validate_medical_content(text: str) -> bool:
    """Vérifie si le contenu est médical.
    
    Args:
        text (str): Texte à vérifier
        
    Returns:
        bool: True si le contenu est médical, False sinon
    """
    if not text:
        return False
        
    # Mots-clés médicaux
    medical_keywords = {
        'doctor', 'hospital', 'clinic', 'medical', 'health', 'treatment',
        'diagnosis', 'symptoms', 'disease', 'patient', 'medicine', 'prescription',
        'therapy', 'surgery', 'examination', 'test', 'scan', 'mri', 'ct',
        'xray', 'blood', 'pain', 'chronic', 'acute', 'emergency', 'specialist',
        'consultation', 'referral', 'follow-up', 'medication', 'condition',
        'illness', 'injury', 'recovery', 'care', 'physician', 'nurse',
        'healthcare', 'medical center', 'urgent care', 'emergency room',
        'ambulance', 'paramedic', 'emt', 'first aid', 'intensive care',
        'icu', 'operating room', 'or', 'surgery', 'surgical', 'procedure',
        'treatment plan', 'medical history', 'family history', 'genetic',
        'hereditary', 'congenital', 'chronic condition', 'acute condition',
        'terminal', 'palliative', 'hospice', 'rehabilitation', 'therapy',
        'physical therapy', 'occupational therapy', 'speech therapy',
        'respiratory therapy', 'cardiac', 'heart', 'lung', 'brain',
        'neurological', 'orthopedic', 'bone', 'joint', 'muscle',
        'gastrointestinal', 'digestive', 'stomach', 'intestine',
        'liver', 'kidney', 'renal', 'urinary', 'reproductive',
        'endocrine', 'hormonal', 'thyroid', 'diabetes', 'cancer',
        'oncology', 'tumor', 'mass', 'growth', 'biopsy',
        'chemotherapy', 'radiation', 'immunotherapy', 'vaccine',
        'vaccination', 'immunization', 'allergy', 'allergic',
        'asthma', 'respiratory', 'breathing', 'pulmonary',
        'cardiovascular', 'heart disease', 'stroke', 'hypertension',
        'high blood pressure', 'cholesterol', 'arthritis',
        'osteoporosis', 'fracture', 'sprain', 'strain',
        'infection', 'bacterial', 'viral', 'fungal',
        'antibiotic', 'antiviral', 'medication', 'drug',
        'dose', 'dosage', 'prescription', 'over-the-counter',
        'otc', 'side effect', 'adverse reaction', 'contraindication',
        'preventive', 'preventative', 'screening', 'check-up',
        'annual exam', 'physical exam', 'lab test', 'blood test',
        'urine test', 'stool test', 'imaging', 'ultrasound',
        'sonogram', 'x-ray', 'radiograph', 'ct scan',
        'mri', 'pet scan', 'nuclear medicine', 'contrast',
        'dye', 'intravenous', 'iv', 'injection', 'oral',
        'topical', 'ointment', 'cream', 'gel', 'drops',
        'spray', 'inhaler', 'nebulizer', 'suppository',
        'patch', 'implant', 'device', 'prosthetic',
        'artificial', 'transplant', 'donor', 'recipient',
        'blood type', 'tissue type', 'compatibility',
        'rejection', 'immune system', 'autoimmune',
        'inflammation', 'swelling', 'redness', 'pain',
        'acute pain', 'chronic pain', 'breakthrough pain',
        'management', 'control', 'relief', 'palliative',
        'hospice', 'end-of-life', 'terminal', 'prognosis',
        'outcome', 'survival', 'mortality', 'morbidity',
        'quality of life', 'activities of daily living',
        'adl', 'independent', 'dependent', 'assistance',
        'caregiver', 'support', 'counseling', 'therapy',
        'psychological', 'psychiatric', 'mental health',
        'behavioral health', 'addiction', 'substance abuse',
        'recovery', 'rehabilitation', 'physical therapy',
        'occupational therapy', 'speech therapy', 'cognitive therapy',
        'behavioral therapy', 'group therapy', 'individual therapy',
        'family therapy', 'marriage counseling', 'grief counseling',
        'support group', 'self-help', 'lifestyle', 'diet',
        'nutrition', 'exercise', 'physical activity', 'weight',
        'obesity', 'underweight', 'eating disorder', 'anorexia',
        'bulimia', 'binge eating', 'purging', 'fasting',
        'metabolism', 'digestion', 'absorption', 'elimination',
        'bowel movement', 'urination', 'frequency', 'urgency',
        'incontinence', 'retention', 'catheter', 'stoma',
        'ostomy', 'colostomy', 'ileostomy', 'urostomy',
        'wound', 'injury', 'trauma', 'burn', 'cut',
        'laceration', 'abrasion', 'contusion', 'bruise',
        'fracture', 'break', 'sprain', 'strain', 'dislocation',
        'head injury', 'concussion', 'traumatic brain injury',
        'tbi', 'spinal cord injury', 'paralysis', 'quadriplegia',
        'paraplegia', 'amputation', 'prosthetic', 'artificial limb',
        'wheelchair', 'walker', 'cane', 'crutches', 'mobility aid',
        'assistive device', 'hearing aid', 'glasses', 'contacts',
        'vision correction', 'dental', 'oral health', 'teeth',
        'gums', 'periodontal', 'cavity', 'filling', 'crown',
        'bridge', 'implant', 'denture', 'partial', 'full',
        'extraction', 'root canal', 'orthodontic', 'braces',
        'invisalign', 'retainer', 'bite', 'jaw', 'tmj',
        'sleep', 'insomnia', 'apnea', 'snoring', 'fatigue',
        'tired', 'exhaustion', 'energy', 'weakness', 'strength',
        'balance', 'coordination', 'dizziness', 'vertigo',
        'nausea', 'vomiting', 'diarrhea', 'constipation',
        'bloating', 'gas', 'heartburn', 'reflux', 'gerd',
        'ulcer', 'bleeding', 'hemorrhage', 'clot', 'dvt',
        'embolism', 'stroke', 'heart attack', 'mi',
        'cardiac arrest', 'arrhythmia', 'palpitations',
        'murmur', 'valve', 'bypass', 'stent', 'pacemaker',
        'defibrillator', 'blood pressure', 'pulse', 'heart rate',
        'respiratory rate', 'breathing rate', 'temperature',
        'fever', 'chills', 'sweats', 'hot flashes',
        'menopause', 'perimenopause', 'postmenopause',
        'menstrual', 'period', 'cycle', 'irregular',
        'heavy', 'light', 'spotting', 'bleeding',
        'pregnancy', 'pregnant', 'conception', 'fertility',
        'infertility', 'miscarriage', 'abortion',
        'birth control', 'contraception', 'std',
        'sti', 'sexually transmitted', 'hiv', 'aids',
        'hepatitis', 'herpes', 'hpv', 'warts',
        'infection', 'bacterial', 'viral', 'fungal',
        'parasitic', 'antibiotic', 'antiviral',
        'antifungal', 'antiparasitic', 'resistance',
        'immune', 'immunity', 'vaccine', 'vaccination',
        'immunization', 'booster', 'allergy', 'allergic',
        'reaction', 'anaphylaxis', 'shock', 'emergency'
    }
    
    # Conversion en minuscules pour la comparaison
    text = text.lower()
    
    # Compte le nombre de mots-clés médicaux trouvés
    found_keywords = sum(1 for keyword in medical_keywords if keyword in text)
    
    # Retourne True si au moins 2 mots-clés médicaux sont trouvés
    return found_keywords >= 2