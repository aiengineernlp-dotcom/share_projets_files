#!/bin/bash

# Script de sauvegarde de la base de données
# Usage: ./backup_database.sh [chemin_destination]

# Configuration
DB_PATH="data/phase1_data.db"
BACKUP_DIR="data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Création du dossier de sauvegarde si nécessaire
mkdir -p "$BACKUP_DIR"

# Chemin de destination de la sauvegarde
if [ -z "$1" ]; then
    BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP.db"
else
    BACKUP_PATH="$1/backup_$TIMESTAMP.db"
fi

# Vérification de l'existence de la base de données
if [ ! -f "$DB_PATH" ]; then
    echo "Erreur: La base de données n'existe pas à $DB_PATH"
    exit 1
fi

# Sauvegarde de la base de données
echo "Sauvegarde de la base de données..."
cp "$DB_PATH" "$BACKUP_PATH"

if [ $? -eq 0 ]; then
    echo "Sauvegarde réussie: $BACKUP_PATH"
else
    echo "Erreur lors de la sauvegarde"
    exit 1
fi 