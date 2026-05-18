import spacy
#charger le model francais
nlp = spacy.load("fr_core_news_sm")

#texte a analyser
texte = "Le client veut acheter une maison à Yaoundé. Il a contacté l'agence ImmoPlus hier."

#traiter le texte
doc = nlp(texte)

#extraire les mots(les noms, les verbes les lieux, les entites etc.....)
noms = [token.text for token in doc if token.pos_=='NOUN']
verbs = [token.text for token in doc if token.pos_=='VERB']
lieux = [ent.text for ent in doc.ents if ent.label_ =='LOC' or ent.label_=='GPE']
entites = [(ent.text, ent.label_) for ent in doc.ents]


# print("les verbs: ",verbs)
# print("les lieux: ",lieux)
# print("les entites: ",entites)