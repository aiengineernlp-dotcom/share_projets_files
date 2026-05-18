#!/bin/bash

# Configuration
export PYTHONPATH=$PYTHONPATH:.

# Couleurs pour le terminal
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Fonction pour exécuter les tests d'une phase
run_phase_tests() {
    echo -e "\n${GREEN}Exécution des tests de la phase $1...${NC}"
    pytest tests/test_phase$1/ -v
}

# Nettoyage des fichiers .pyc
echo "Nettoyage des fichiers .pyc..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete

# Installation des dépendances de test si nécessaire
if ! pip show pytest > /dev/null; then
    echo "Installation de pytest..."
    pip install pytest pytest-cov
fi

# Exécution des tests par phase
for phase in {1..4}; do
    run_phase_tests $phase
done

# Génération du rapport de couverture
echo -e "\n${GREEN}Génération du rapport de couverture...${NC}"
pytest --cov=src tests/ --cov-report=html

echo -e "\n${GREEN}Tests terminés. Consultez le rapport de couverture dans htmlcov/index.html${NC}" 