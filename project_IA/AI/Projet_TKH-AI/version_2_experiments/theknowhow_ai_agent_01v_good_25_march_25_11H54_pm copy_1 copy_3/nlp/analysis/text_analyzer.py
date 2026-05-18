"""
Analyseur de texte générique
"""

class TextAnalyzer:
    def __init__(self, nlp):
        self.nlp = nlp

    def analyze_text(self, text: str) -> dict:
        """
        Analyse un texte et retourne les informations pertinentes
        """
        if not text:
            return {
                "sentiment": 0,
                "entities": [],
                "keywords": []
            }

        doc = self.nlp(text)
        
        # Extraction des entités nommées
        entities = [
            {
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            }
            for ent in doc.ents
        ]
        
        # Extraction des mots-clés (noms et adjectifs)
        keywords = [
            token.text
            for token in doc
            if token.pos_ in ["NOUN", "ADJ"] and not token.is_stop
        ]
        
        # Analyse basique du sentiment (à améliorer)
        sentiment = 0
        for token in doc:
            if token.pos_ == "ADJ":
                # Logique simple : les adjectifs positifs = +1, négatifs = -1
                if token.text.lower() in ["good", "great", "excellent", "amazing"]:
                    sentiment += 1
                elif token.text.lower() in ["bad", "terrible", "awful", "poor"]:
                    sentiment -= 1
        
        return {
            "sentiment": sentiment,
            "entities": entities,
            "keywords": keywords
        } 