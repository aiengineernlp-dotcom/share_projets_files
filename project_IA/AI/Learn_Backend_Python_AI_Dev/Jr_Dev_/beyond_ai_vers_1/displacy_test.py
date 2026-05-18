#pour spacy lui meme
import spacy
#pour displacy
from spacy import displacy
#pour le chemin de l'image
from pathlib import Path
#charger le modele
nlp = spacy.load("en_core_web_md")
# mon text
text = "Barack Obama was born in Hawaii in 1961 and became president of the United States."

#traitement du texte
doc = nlp(text)
# Afficher les entités détectées dans le terminal
for ent in doc.ents:
    print(ent.text, ent.label_)

svg = displacy.render(doc,style='dep',jupyter=False)

# Definir le chemin de sortie dans un dossier locale 'images'
output_dir = Path('images')
output_dir.mkdir(exist_ok=True)  # creation du dossier si il n'existe pas

#Enregisterer le fichier SVG
output_path  = output_dir/ 'butterfly.svg'
output_path.write_text(svg,encoding='utf-8')

print(f"✅ SVG généré ici : {output_path.resolve()}")

#Visualisation avec displacy dans le navigateur (par defaut en localhost:5000)
displacy.serve(doc,style='ent',port=3004)
# displacy.serve(doc,style='dep',port=3003)