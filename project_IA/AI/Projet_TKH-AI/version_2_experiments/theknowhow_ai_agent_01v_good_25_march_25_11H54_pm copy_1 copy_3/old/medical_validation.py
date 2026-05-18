"""
Fonctions utilitaires pour la validation du contenu médical.
"""

def validate_medical_content(text: str) -> bool:
    """Vérifie si le contenu est de nature médicale."""
    medical_terms = {
        "diagnosis", "treatment", "symptoms", "patient",
        "clinical", "medical", "medicine", "doctor",
        "hospital", "health", "disease", "condition",
        "therapy", "prescription", "surgery", "physician",
        "nurse", "healthcare", "clinic", "emergency"
    }
    
    text_lower = text.lower()
    words = set(text_lower.split())
    
    # Vérifie si au moins 2 termes médicaux sont présents
    medical_words = words.intersection(medical_terms)
    return len(medical_words) >= 2 