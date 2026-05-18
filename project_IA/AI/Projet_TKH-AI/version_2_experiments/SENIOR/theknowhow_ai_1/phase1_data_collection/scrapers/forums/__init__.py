"""
Package des scrapers de forums médicaux.

RÔLE PRINCIPAL :
---------------
Ce module initialise le package des scrapers de forums médicaux.
Il expose les classes de scrapers et les fonctionnalités communes
pour le scraping de forums médicaux.

RELATIONS AVEC LES AUTRES FICHIERS :
----------------------------------
- Est importé par :
  * run_phase1.py (exécution des scrapers)
  * phase1.py (intégration dans la phase 1)

- Dépend de :
  * base_scraper.py (classe de base)
  * healthunlocked_scraper.py (scraper HealthUnlocked)
  * webmd_scraper.py (scraper WebMD)
  * healthboards_scraper.py (scraper HealthBoards)
  * medhelp_scraper.py (scraper MedHelp)
  * patient_info_scraper.py (scraper Patient.info)

STRUCTURE DU CONTENU :
--------------------
1. Imports :
   - Classes de scrapers
   - Fonctionnalités communes
   - Utilitaires

2. Exports :
   - Classes de scrapers
   - Fonctions utilitaires
   - Constantes

3. Configuration :
   - Paramètres communs
   - Constantes
   - Types

4. Documentation :
   - Description du package
   - Guide d'utilisation
   - Exemples

FONCTIONS PRINCIPALES :
---------------------
- get_scraper() : Obtient un scraper
- get_all_scrapers() : Liste tous les scrapers
- get_scraper_config() : Configuration d'un scraper
- get_common_config() : Configuration commune

IMPORTANCE ET SUPPRESSION :
-------------------------
Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
- Il initialise le package des scrapers
- Il expose les fonctionnalités
- Il centralise la configuration
- Il est essentiel pour la phase 1
"""

"""
Sous-package contenant les scrapers de forums médicaux
""" 