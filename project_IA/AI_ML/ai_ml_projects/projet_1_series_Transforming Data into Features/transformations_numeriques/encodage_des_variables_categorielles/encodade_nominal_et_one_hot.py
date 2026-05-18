import pandas as pd

# Chargement du fichier
Reviews = pd.read_csv('../data/Reviews.csv')

# Afficher les types 
print("Les types de variables: \n", Reviews.dtypes)

# Afficher les étiquettes fréquentes dans 'Summary'
print("\nAffichage des étiquettes de la variable 'Summary':\n", Reviews['Summary'].value_counts().head(15))

# Garder les 10 résumés les plus fréquents
top_summaries = Reviews['Summary'].value_counts().nlargest(10).index

# Créer une nouvelle colonne 'Summary_top10' qui contient seulement les top résumés, sinon 'Autre'
Reviews['Summary_top10'] = Reviews['Summary'].apply(lambda x: x if x in top_summaries else 'Autre')

# One-Hot Encoding
ohe = pd.get_dummies(Reviews['Summary_top10'], prefix='Summary')

# Ajouter les colonnes encodées
Reviews = Reviews.join(ohe)

# Afficher les premières colonnes pour vérifier
print("\n✅ Encodage One-Hot terminé. Aperçu des premières lignes :")
print(Reviews.iloc[:, -15:].head())  # Dernières colonnes = colonnes One-Hot
