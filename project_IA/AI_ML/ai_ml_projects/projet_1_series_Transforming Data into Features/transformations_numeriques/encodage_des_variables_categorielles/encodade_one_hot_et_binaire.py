import pandas as pd

from category_encoders import BinaryEncoder
# Chargement du fichier
Reviews = pd.read_csv('../data/Reviews.csv')

# Afficher les types
print("Les types de variables: \n", Reviews.dtypes)

# Afficher les étiquettes fréquentes dans 'Summary'
print("\nAffichage des étiquettes de la variable 'Summary':\n", Reviews['Summary'].value_counts().head(15))

Summary = BinaryEncoder(cols=['Summary'],drop_invariant=True).fit_transform(Reviews)

print("\nENCODAGE BINAIRE \n", Summary)