import spacy
from spacy import displacy

#chargement du modele
nlp = spacy.load("en_core_web_md")

#chargement d'un model texte

doc = nlp('I have a ginger cat.')

#Affichage des tokens

for token in doc:
    print(token.text, token.pos_, token.dep_)