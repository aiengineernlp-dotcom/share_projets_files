#!/usr/bin/env python3
"""
Script pour lancer la phase 1 de collecte de données.
"""

import os
import sys
import asyncio

# Ajouter le répertoire racine au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))  # Remonter de src/scripts à la racine
sys.path.insert(0, root_dir)

# Importer le script principal de la phase 1
from src.core.phase_1_data_collection.data_collection import main

if __name__ == "__main__":
    print("Démarrage de la phase 1 de collecte de données...")
    
    # Exécuter la phase 1
    asyncio.run(main())
    
    print("Phase 1 terminée. Vérifiez les logs pour plus de détails.") 