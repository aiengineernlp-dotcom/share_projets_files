# Guide d'ajout d'un nouveau scraper

Ce guide explique comment ajouter un nouveau scraper au système de collecte de données.

## Structure du projet

```
phase1_data_collection/
├── scrapers/
│   ├── social_media/     # Scrapers pour les réseaux sociaux
│   ├── forums/          # Scrapers pour les forums médicaux
│   └── websites/        # Scrapers pour les sites web médicaux
├── data/
│   └── raw/
│       ├── social_media/
│       ├── forums/
│       └── websites/
└── run_phase1.py        # Script principal
```

## Étapes pour ajouter un nouveau scraper

### 1. Création du fichier du scraper

1. **Choisir la catégorie appropriée** :
   - `social_media/` : Pour les réseaux sociaux (Reddit, Twitter, etc.)
   - `forums/` : Pour les forums médicaux
   - `websites/` : Pour les sites web médicaux

2. **Créer le fichier du scraper** :
   - Nommer le fichier : `nom_du_scraper.py`
   - Exemple : `scrapers/websites/mon_nouveau_scraper.py`

3. **Structure de base du scraper** :
```python
import os
import logging
from typing import Dict, List
import sqlite3
from datetime import datetime

class MonNouveauScraper:
    def __init__(self):
        self.db_path = os.environ.get('MON_NOUVEAU_SCRAPER_DB_PATH')
        self.logger = logging.getLogger(__name__)
        self.setup_database()
    
    def setup_database(self):
        """Initialise la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Création des tables nécessaires
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                date TEXT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def run(self):
        """Méthode principale du scraper"""
        try:
            self.logger.info("Démarrage du scraper")
            # Implémentation du scraping
            self.logger.info("Scraper terminé avec succès")
        except Exception as e:
            self.logger.error(f"Erreur lors du scraping : {str(e)}")
            raise

if __name__ == "__main__":
    scraper = MonNouveauScraper()
    scraper.run()
```

### 2. Modification de run_phase1.py

1. **Ajouter le répertoire de données** :
   Dans la fonction `create_directories()`, ajouter le nom du scraper :
```python
directories = {
    'raw': {
        'websites': [
            # ... autres scrapers ...
            'mon_nouveau_scraper'  # Nouveau scraper
        ]
    }
}
```

2. **Configurer le chemin de la base de données** :
   Dans la fonction `setup_database_paths()`, ajouter :
```python
db_paths = {
    # ... autres chemins ...
    'MON_NOUVEAU_SCRAPER_DB_PATH': 'data/raw/websites/mon_nouveau_scraper/sqlite/mon_nouveau_scraper.db'
}
```

3. **Ajouter le scraper à la liste d'exécution** :
   Dans la fonction `main()`, ajouter le chemin du scraper :
```python
scrapers = [
    # ... autres scrapers ...
    'scrapers/websites/mon_nouveau_scraper.py'
]
```

### 3. Bonnes pratiques

1. **Gestion des erreurs** :
   - Toujours utiliser try/except
   - Logger les erreurs de manière détaillée
   - Gérer les timeouts et les erreurs réseau

2. **Configuration** :
   - Utiliser les variables d'environnement pour les configurations sensibles
   - Stocker les URLs et autres constantes en haut du fichier

3. **Base de données** :
   - Utiliser les chemins définis dans les variables d'environnement
   - Créer des index pour les requêtes fréquentes
   - Fermer proprement les connexions

4. **Logging** :
   - Utiliser le logger configuré
   - Loguer les étapes importantes
   - Inclure des statistiques (nombre d'éléments scrapés, temps d'exécution)

### 4. Exemple complet

Voici un exemple complet d'ajout d'un nouveau scraper pour un site web médical :

1. **Créer le fichier** `scrapers/websites/mon_nouveau_scraper.py`
2. **Modifier** `run_phase1.py` comme indiqué ci-dessus
3. **Tester** le scraper :
```bash
python run_phase1.py
```

### 5. Vérifications

Après l'ajout, vérifier que :
- Le répertoire de données est créé
- La base de données est accessible
- Les logs sont correctement générés
- Le scraper s'exécute sans erreur

### 6. Dépannage

Si le scraper ne fonctionne pas :
1. Vérifier les logs pour les erreurs
2. S'assurer que tous les chemins sont corrects
3. Vérifier les permissions des répertoires
4. Confirmer que toutes les dépendances sont installées

## Notes importantes

- Toujours tester le scraper avant de l'ajouter à la liste principale
- Documenter les spécificités du scraper (API keys, limitations, etc.)
- Mettre à jour ce guide si de nouvelles bonnes pratiques sont identifiées 