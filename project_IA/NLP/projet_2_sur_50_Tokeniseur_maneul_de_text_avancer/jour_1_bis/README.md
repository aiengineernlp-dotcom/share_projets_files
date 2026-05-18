project_root/
├── data/
│   ├── raw/                     # Données brutes
│   ├── processed/               # Données prétraitées
│   └── external/                # Embeddings, lexiques, etc.
├── src/
│   ├── __init__.py
│   ├── preprocessing/           # Modules de prétraitement
│   │   ├── __init__.py
│   │   ├── cleaner.py           # Nettoyage de texte
│   │   ├── tokenizer.py         # Tokenisation
│   │   └── normalizer.py        # Normalisation (lemmes, etc.)
│   ├── features/                # Extraction de caractéristiques
│   │   ├── __init__.py
│   │   ├── vectorizer.py        # TF-IDF, BoW, etc.
│   │   └── embeddings.py        # Word2vec, GloVe, etc.
│   ├── models/                  # Modèles ML/DL
│   │   ├── __init__.py
│   │   ├── classifier.py        # Modèles de classification
│   │   └── sequence.py          # Modèles séquentiels (RNN, etc.)
│   ├── evaluation/              # Évaluation des modèles
│   │   ├── __init__.py
│   │   └── metrics.py           # Métriques et évaluation
│   └── utils/                   # Utilitaires
│       ├── __init__.py
│       ├── logger.py            # Logging
│       └── visualization.py     # Visualisations
├── notebooks/                   # Notebooks Jupyter pour exploration
├── config/                      # Configuration
│   └── config.yaml              # Paramètres de configuration
├── requirements.txt             # Dépendances
└── README.md                    # Documentation
Projets de base (Projets simples 1-10)
Ajoutez à la structure principale :

project_root/
├── main.py                      # Point d'entrée principal
├── streamlit_app.py             # Pour visualisation simple (si besoin)
