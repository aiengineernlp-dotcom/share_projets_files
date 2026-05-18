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
lieux = [token.text for token in doc if token.pos_=='PLACE']
entites = [(ent.text, ent.label_) for ent in doc.ents]

print("",noms)
print("",verbs)
print("",lieux)
print("",entites)