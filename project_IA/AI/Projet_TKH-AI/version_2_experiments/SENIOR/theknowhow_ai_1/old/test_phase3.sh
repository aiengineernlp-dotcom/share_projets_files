#!/bin/bash

# Arrêter les processus existants sur les ports utilisés
./stop_ports.sh

# Installer les dépendances si nécessaire
pip install -r requirements.txt

# Lancer les tests
echo "Lancement des tests de la phase 3..."
python -m pytest test_phase3.py -v

# Lancer le serveur en arrière-plan
echo "Démarrage du serveur..."
python phase3_conversationnel.py &
SERVER_PID=$!

# Attendre que le serveur démarre
sleep 5

# Vérifier si le serveur est en cours d'exécution
if ps -p $SERVER_PID > /dev/null; then
    echo "Serveur démarré avec succès sur http://localhost:8000"
else
    echo "Erreur lors du démarrage du serveur"
    exit 1
fi

# Attendre que l'utilisateur appuie sur Ctrl+C
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
wait $SERVER_PID 