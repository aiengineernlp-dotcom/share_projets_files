# Scrapers de Sites Web Médicaux

Ce dossier contient les scrapers pour collecter des données médicales à partir de différents sites web médicaux français.

## Sites Supportés

- Ameli (https://www.ameli.fr)
- Doctissimo (https://www.doctissimo.fr)
- Vidal (https://www.vidal.fr)
- E-santé (https://www.e-sante.fr)
- Santé Magazine (https://www.sante-magazine.fr)

## Structure des Fichiers

```
websites/
├── base_web_scraper.py      # Classe de base pour tous les scrapers
├── ameli_scraper.py         # Scraper pour Ameli
├── doctissimo_scraper.py    # Scraper pour Doctissimo
├── vidal_scraper.py         # Scraper pour Vidal
├── esante_scraper.py        # Scraper pour E-santé
├── sante_magazine_scraper.py # Scraper pour Santé Magazine
└── run_all_web_scrapers.py  # Script pour lancer tous les scrapers
```

## Configuration

Chaque scraper a sa propre configuration dans le dossier `config/websites/`. Les fichiers de configuration contiennent :

- URL de base
- Chemins de base de données
- Sélecteurs CSS
- Catégories d'articles
- Headers HTTP
- Mots-clés médicaux
- Configuration du logging

## Prérequis

- Python 3.8+
- aiohttp
- beautifulsoup4
- sqlite3

## Installation

1. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer un Scraper Individuel

Pour lancer un scraper spécifique, exécutez le script correspondant :

```bash
python ameli_scraper.py
python doctissimo_scraper.py
python vidal_scraper.py
python esante_scraper.py
python sante_magazine_scraper.py
```

### Lancer Tous les Scrapers

Pour lancer tous les scrapers en parallèle :

```bash
python run_all_web_scrapers.py
```

## Structure des Données

Les données collectées sont stockées dans des bases de données SQLite avec la structure suivante :

### Table Articles

- article_id (INTEGER PRIMARY KEY)
- title (TEXT)
- content (TEXT)
- url (TEXT)
- author (TEXT)
- published_date (TEXT)
- category (TEXT)
- tags (TEXT)
- medical_relevance_score (FLOAT)
- language (TEXT)
- scraped_at (TEXT)
- source (TEXT)
- is_official (BOOLEAN)

### Champs Spécifiques par Site

#### Ameli
- is_official (BOOLEAN)

#### Doctissimo
- has_comments (BOOLEAN)

#### Vidal
- is_medication (BOOLEAN)
- active_ingredients (TEXT)
- prescription_type (TEXT)
- pharmacy_availability (TEXT)

#### E-santé
- medical_references (TEXT)
- sources (TEXT)

#### Santé Magazine
- images (TEXT)
- videos (TEXT)
- external_links (TEXT)

## Logs

Les logs sont stockés dans le dossier `logs/` avec un fichier par scraper :

- ameli_scraper.log
- doctissimo_scraper.log
- vidal_scraper.log
- esante_scraper.log
- sante_magazine_scraper.log
- all_web_scrapers.log

## Gestion des Erreurs

Les scrapers incluent :
- Gestion des timeouts
- Retry automatique en cas d'erreur
- Logging détaillé des erreurs
- Gestion des exceptions

## Limitations

- Respect des robots.txt
- Délais entre les requêtes
- Limite du nombre de pages par catégorie
- Gestion de la mémoire

## Contribution

Pour contribuer :
1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Créez une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails. 