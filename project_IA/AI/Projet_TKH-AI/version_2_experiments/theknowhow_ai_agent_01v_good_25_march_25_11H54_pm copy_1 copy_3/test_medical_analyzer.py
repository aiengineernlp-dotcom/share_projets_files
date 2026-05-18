import spacy
from phase1_data_collection.processors.medical_analysis.medical_analyzer import MedicalAnalyzer
from config.reddit_config import NLP_CONFIG

def test_analyzer():
    # Chargement des modèles pour chaque langue
    nlp_fr = spacy.load(NLP_CONFIG['models']['fr'])
    nlp_en = spacy.load(NLP_CONFIG['models']['en'])
    nlp_ar = spacy.load(NLP_CONFIG['models']['ar'])

    # Création des analyseurs pour chaque langue
    analyzer_fr = MedicalAnalyzer(nlp_fr)
    analyzer_en = MedicalAnalyzer(nlp_en)
    analyzer_ar = MedicalAnalyzer(nlp_ar)

    # Textes de test en différentes langues
    texts = {
        'fr': "J'ai besoin d'un deuxième avis médical urgent. J'ai une douleur thoracique sévère qui empire.",
        'en': "I need an urgent second opinion. I have severe chest pain that's getting worse.",
        'ar': "أحتاج إلى رأي طبي ثان عاجل. لدي ألم شديد في الصدر يزداد سوءا."
    }

    # Test pour chaque langue
    results = {}
    
    # Analyse en français
    print("\n=== Test en Français ===")
    results['fr'] = analyzer_fr.analyze_medical_text(texts['fr'])
    print(f"Texte: {texts['fr']}")
    print(f"Score médical: {results['fr']['medical_score']:.2f}")
    print(f"Score d'urgence: {results['fr']['urgency_score']:.2f}")
    print(f"Score second avis: {results['fr']['second_opinion_score']:.2f}")
    print(f"Catégorie: {results['fr']['category']}")

    # Analyse en anglais
    print("\n=== Test en Anglais ===")
    results['en'] = analyzer_en.analyze_medical_text(texts['en'])
    print(f"Texte: {texts['en']}")
    print(f"Score médical: {results['en']['medical_score']:.2f}")
    print(f"Score d'urgence: {results['en']['urgency_score']:.2f}")
    print(f"Score second avis: {results['en']['second_opinion_score']:.2f}")
    print(f"Catégorie: {results['en']['category']}")

    # Analyse en arabe
    print("\n=== Test en Arabe ===")
    results['ar'] = analyzer_ar.analyze_medical_text(texts['ar'])
    print(f"Texte: {texts['ar']}")
    print(f"Score médical: {results['ar']['medical_score']:.2f}")
    print(f"Score d'urgence: {results['ar']['urgency_score']:.2f}")
    print(f"Score second avis: {results['ar']['second_opinion_score']:.2f}")
    print(f"Catégorie: {results['ar']['category']}")

if __name__ == "__main__":
    test_analyzer() 