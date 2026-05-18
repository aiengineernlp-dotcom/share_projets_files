"""
Configuration pour le scraping Reddit
"""

# Liste des subreddits à scraper
MEDICAL_SUBREDDITS = [
    'AskDocs',           # Forum général de questions médicales
    'medical_advice',    # Conseils médicaux généraux
    'DiagnoseMe',        # Aide au diagnostic
    'AskDoctorSmeeee',   # Questions pour les médecins
    'AskHealthcare',     # Questions sur les soins de santé
    'AskPediatrics',     # Questions pédiatriques
    'AskNeurology',      # Questions neurologiques
    'AskCardiology',     # Questions cardiologiques
    'AskDermatology',    # Questions dermatologiques
    'AskPsychiatry',     # Questions psychiatriques
    'AskPsychologists',  # Questions pour les psychologues
    'AskOptometry',      # Questions pour les optométristes
    'AskDentists',       # Questions dentaires
    'AskVet',           # Questions vétérinaires
    'AskVeterinarians',  # Questions vétérinaires (alternative)
    'AskMedical',       # Questions médicales générales
    'AskHealth',        # Questions de santé générales
    'AskDoctor',        # Questions pour les médecins
    'AskNurses',        # Questions pour les infirmiers
    'AskPharmacist',    # Questions pour les pharmaciens
    'SecondOpinion',    # Spécialisé dans les second avis
    'MedicalSecondOpinion',  # Second avis médicaux
    'DoctorAdvice',     # Conseils médicaux
    'MedicalAdvice',    # Avis médicaux
    'HealthAdvice',     # Conseils de santé
    'PatientAdvice',    # Conseils pour les patients
    'MedicalQuestions', # Questions médicales
    'HealthQuestions',  # Questions de santé
    'PatientQuestions'  # Questions des patients
]

# Nombre de posts à collecter par terme de recherche
POSTS_PER_SEARCH = 1

# Termes de recherche par catégorie et par langue
SEARCH_TERMS = {
    'second_opinion': {
        'fr': [
            "besoin d'un autre avis", "avis médical différent", "autre médecin",
            "confirmation diagnostic", "doute sur diagnostic", "pas sûr du diagnostic",
            "opinions contradictoires", "médecin dit mais", "avis contradictoires",
            "deuxième consultation", "changement de médecin", "nouveau spécialiste",
            "avis divergent", "diagnostic différent", "traitement différent",
            "médecin ne prend pas au sérieux", "doute sur le traitement",
            "avis médical contradictoire", "besoin d'une confirmation",
            "médecin ne m'écoute pas", "avis médical alternatif",
            "diagnostics contradictoires", "avis divergent", "conflict diagnostic",
            "mon médecin dit X mais je pense Y", "doute sur le diagnostic proposé",
            "avis médical conflictuel", "besoin d'un avis supplémentaire",
            "médecin ne me convainc pas", "avis médical insuffisant",
            "médecin ne comprend pas", "plusieurs diagnostics différents",
            "besoin expertise supplémentaire", "pas convaincu par diagnostic",
            "résultats contradictoires", "symptômes inexpliqués",
            "traitement inefficace", "besoin autre expertise",
            "médecin minimise symptômes", "diagnostic incertain"
        ],
        'en': [
            "second opinion", "another doctor", "different doctor",
            "need confirmation", "verify diagnosis", "doubt diagnosis",
            "not sure about diagnosis", "conflicting opinions",
            "doctor said but", "want another opinion", "change doctor",
            "new specialist", "divergent opinion", "different diagnosis",
            "different treatment", "doctor not taking seriously",
            "doubt about treatment", "contradictory medical advice",
            "need verification", "doctor not listening",
            "alternative medical opinion", "conflicting diagnoses",
            "diagnostic conflict", "my doctor says X but I think Y",
            "doubt about proposed diagnosis", "conflicting medical advice",
            "need additional opinion", "doctor not convincing",
            "insufficient medical advice",
            "doctors disagree", "conflicting test results",
            "multiple diagnoses", "need expert opinion",
            "not convinced by diagnosis", "unexplained symptoms",
            "treatment not working", "doctors can't figure out",
            "doctor dismisses symptoms", "uncertain diagnosis",
            "different specialists say", "need clarity on diagnosis",
            "doctors are stumped", "medical opinions differ"
        ],
        'ar': [
            "رأي طبي ثان", "طبيب آخر", "رأي آخر",
            "تأكيد التشخيص", "شك في التشخيص", "غير متأكد من التشخيص",
            "آراء متضاربة", "الطبيب قال لكن", "تشخيص مختلف",
            "استشارة ثانية", "تغيير الطبيب", "أخصائي جديد",
            "رأي مختلف", "تشخيص مختلف", "علاج مختلف",
            "الطبيب لا يأخذ على محمل الجد", "شك في العلاج",
            "نصائح طبية متضاربة", "بحاجة للتأكيد",
            "الطبيب لا يستمع", "رأي طبي بديل",
            "تشخيصات متضاربة", "تعارض في التشخيص",
            "الطبيب يقول X لكنني أعتقد Y", "شك في التشخيص المقترح",
            "نصائح طبية متعارضة", "بحاجة لرأي إضافي",
            "الطبيب غير مقنع", "نصائح طبية غير كافية",
            "اختلاف الأطباء", "نتائج متضاربة",
            "تشخيصات متعددة", "بحاجة لرأي خبير",
            "غير مقتنع بالتشخيص", "أعراض غير مفسرة",
            "العلاج غير فعال", "الأطباء لا يفهمون",
            "الطبيب يتجاهل الأعراض", "تشخيص غير مؤكد"
        ]
    },
    'urgent_help': {
        'fr': [
            "urgence médicale", "aide urgente", "besoin aide immédiate", "critique",
            "danger de mort", "douleur sévère", "aggravation",
            "ne peut pas attendre", "attention immédiate", "condition grave"
        ],
        'en': [
            "emergency", "urgent help", "need help now", "critical",
            "life threatening", "severe pain", "getting worse",
            "cant wait", "immediate attention", "serious condition"
        ],
        'ar': [
            "حالة طارئة", "مساعدة عاجلة", "بحاجة للمساعدة الآن", "حالة حرجة",
            "خطر على الحياة", "ألم شديد", "تدهور الحالة",
            "لا يمكن الانتظار", "عناية فورية", "حالة خطيرة"
        ]
    },
    'medical_advice': {
        'fr': [
            "besoin conseil", "question médicale", "problème santé",
            "dois-je consulter", "aide médicale", "souci santé",
            "condition médicale", "problème médical", "inquiétude santé"
        ],
        'en': [
            "need advice", "medical question", "health concern",
            "should i see doctor", "medical help", "health problem",
            "medical condition", "health issue", "medical concern"
        ],
        'ar': [
            "نصيحة طبية", "سؤال طبي", "مشكلة صحية",
            "هل يجب أن أرى طبيب", "مساعدة طبية", "مشكلة صحية",
            "حالة طبية", "مشكلة صحية", "قلق صحي"
        ]
    },
    'diagnosis_help': {
        'fr': [
            "qu'est-ce que ça pourrait être", "diagnostic possible", "symptômes de",
            "mystère médical", "non diagnostiqué", "besoin diagnostic",
            "identifier problème", "qu'est-ce qui ne va pas", "condition médicale"
        ],
        'en': [
            "what could this be", "possible diagnosis", "symptoms of",
            "medical mystery", "undiagnosed", "need diagnosis",
            "help identify", "what is wrong", "medical condition"
        ],
        'ar': [
            "ما يمكن أن يكون هذا", "تشخيص محتمل", "أعراض",
            "لغز طبي", "غير مشخص", "بحاجة إلى تشخيص",
            "تحديد المشكلة", "ما الخطأ", "حالة طبية"
        ]
    }
}

# Seuils de catégorisation
CATEGORIZATION_THRESHOLDS = {
    'urgent_help': 0.6,      # Seuil pour les cas urgents (ex: arrêt cardiaque, hémorragie)
    'urgent_second_opinion': 0.50,  # Seuil pour les second avis urgents (ex: cancer suspecté)
    'priority_second_opinion': 0.40,  # Seuil pour les second avis prioritaires (ex: maladie chronique)
    'standard_second_opinion': 0.30,  # Seuil pour les second avis standards (ex: vérification de diagnostic)
    'quick_advice': 0.2      # Seuil pour les conseils rapides (ex: questions simples)
}

# Poids des différents scores
SCORE_WEIGHTS = {
    'medical_relevance': 0.35,    # Légèrement réduit (35%)
    'urgency': 0.25,              # Légèrement réduit (25%)
    'second_opinion': 0.40        # Augmenté (40%) pour donner plus de poids aux demandes de second avis
}

# Configuration des modèles NLP pour chaque langue
NLP_CONFIG = {
    'models': {
        'fr': 'fr_core_news_sm',
        'en': 'en_core_web_sm',
        'ar': 'xx_ent_wiki_sm'  # Modèle multilingue pour l'arabe
    },
    'default': 'en'  # Langue par défaut
}

# Catégories de posts
POST_CATEGORIES = {
    'urgent': 'Urgent Second Opinion',
    'priority': 'Priority Second Opinion',
    'standard': 'Standard Second Opinion',
    'quick': 'Quick Consultation Recommended',
    'emergency': 'Medical Emergency'
}

# Configuration des logs
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}