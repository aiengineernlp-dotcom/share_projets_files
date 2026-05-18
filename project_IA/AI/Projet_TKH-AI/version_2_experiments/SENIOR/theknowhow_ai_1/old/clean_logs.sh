#!/bin/bash

# Script de nettoyage des logs
# Usage: ./clean_logs.sh [jours]

# Configuration
LOG_DIR="logs"
DAYS_TO_KEEP=${1:-30}

# Vérification du dossier de logs
if [ ! -d "$LOG_DIR" ]; then
    echo "Erreur: Le dossier de logs n'existe pas"
    exit 1
fi

# Nettoyage des logs plus vieux que X jours
echo "Nettoyage des logs plus vieux que $DAYS_TO_KEEP jours..."
find "$LOG_DIR" -type f -name "*.log" -mtime +$DAYS_TO_KEEP -delete

echo "Nettoyage terminé" 