"""Detection automaitque des intentions dans une requets de l'utilisateur"""
"""Objectif: creer un un petit syteme qui devine ce que veut faire l'utilisateur a partir de phrases simple

“Je veux acheter une maison à Yaoundé.” → Intention : achat_immobilier

“Je cherche un cardiologue.” → Intention : recherche_medecin

“Peux-tu me trouver une voiture d’occasion ?” → Intention : achat_voiture
"""


"""🧩 Étapes du projet :
Étape	Description
1️⃣	Préparer un jeu de données avec des phrases d’exemple
2️⃣	Nettoyer le texte (tokenisation, lemmatisation si nécessaire)
3️⃣	Vectoriser les phrases (TF-IDF ou embeddings simples)
4️⃣	Entraîner un classifieur (comme LogisticRegression ou SVC)
5️⃣	Prédire l’intention d’une nouvelle phrase
6️⃣	Évaluer / améliorer le modèle"""


"""📁 Exemple de jeu de données :"""
"""phrases = [
    ("Je veux acheter une maison à Douala", "achat_immobilier"),
    ("Je cherche un appartement à louer", "location_immobilier"),
    ("Trouve-moi un dentiste à Yaoundé", "recherche_medecin"),
    ("Peux-tu me trouver une voiture ?", "achat_voiture"),
    ("Je veux vendre mon terrain", "vente_immobilier"),
    ("Je cherche un cardiologue", "recherche_medecin")
]
"""

import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# donnees d'entrainnement

# data est un tuple
data = [
    ("Je veux acheter une maison à Douala", "achat_immobilier"),
    ("Je cherche un appartement à louer", "location_immobilier"),
    ("Trouve-moi un dentiste à Yaoundé", "recherche_medecin"),
    ("Peux-tu me trouver une voiture ?", "achat_voiture"),
    ("Je veux vendre mon terrain", "vente_immobilier"),
    ("Je cherche un cardiologue", "recherche_medecin")
]

X,y = zip(*data) # ici je decompose Le tuple qui est une liste en deux liste X et y

"""donc je peu faire ceci : """
# print(X)
# print(y)

# Modèle de classification
model = Pipeline([    # c'est genre je dis fais d'abors TfidfVectorizer puis LogisticRegression donc c'est une Chaine le traitement du texte
    ('tfidf', TfidfVectorizer()),
    ('clf',LogisticRegression())
])

# Entrainement
model.fit(X,y)  # ici c'est l'entrainement des modeles afin que X puis reconnaitre son y d'ou la fonction fit()





# Prédiction
phrase_test = ["Peux-tu me trouver une voiture ?","Je veux vendre mon terrain","Je cherche un cardiologue"]

pred = model.predict(phrase_test)


print(f"Phrase : , {phrase_test}")
print(f"Intention detectee: {pred[0]} ",)
print(f"Intention detectee: {pred} ",)



