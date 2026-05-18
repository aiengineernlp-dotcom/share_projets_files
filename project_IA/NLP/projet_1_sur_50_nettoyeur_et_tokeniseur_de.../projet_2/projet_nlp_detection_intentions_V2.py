from sklearn.feature_extraction.text import CountVectorizer  # pour la vectorisation du texte
from sklearn.naive_bayes import MultinomialNB  # pour le model

'''local_DATASET'''
#1. donnees de l'entrainement :
data = [
    ("Je veux acheter une maison à Douala", "achat_immobilier"),
    ("Je cherche un appartement à louer", "location_immobilier"),
    ("Je veux une clinique pour un check-up", "recherche_medecin"),
    ("Est-ce qu’il y a un bon pédiatre à Yaoundé ?", "recherche_medecin"),
    ("J’aimerais vendre ma maison", "vente_immobilier"),
    ("Trouve-moi une voiture électrique", "achat_voiture"),
    ("Je veux investir dans l'immobilier", "achat_immobilier"),
    ("Où puis-je louer un véhicule ?", "location_voiture"),
]

'''SEPARATION texte de l'intension '''
#2- Separation en X (texte) et y (intentions)
X,y= zip(*data)
print('TEXTES :',X)
print('INTENTIONS:', y)

'''PIPELINE'''
#3- VECTORISATION
vectorizer = CountVectorizer()
X_vectorizer = vectorizer.fit_transform(X)
#MODEL
model = MultinomialNB()
model.fit(X_vectorizer,y) # association du texte avec le model

#4- boucle iterrative

print("\n Bienvenue dans le systeme de detction des intentions ! ")
print("Tape une phrase (ou ecrit 'exit' pour quitter) : \n ")

while True:
    user_input = input("-> Votre Phrase : ")
    if user_input.lower() =='exit':
        print('Au revoir !')
        break
    else:
        vector_input = vectorizer.transform([user_input]) #  Tu prends la phrase entrée par l'utilisateur et tu la transformes en vecteur numérique, selon la même logique de vectorisation que pendant l'entraînement (fit_transform).👉 Cela garantit que les mots sont représentés dans le même "espace" que le modèle a appris.
        prediction = model.predict(vector_input) #  Tu demandes au modèle (ici Naive Bayes) de prédire une étiquette (intention) à partir du vecteur. 👉 En sortie : une prédiction parmi les classes "achat_immobilier", "recherche_medecin", etc.
        print("Intention  detectee: ", prediction,"\n")