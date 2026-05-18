#!/bin/bash

# Arrêter le processus sur le port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Arrêter le processus sur le port 8001
lsof -ti:8001 | xargs kill -9 2>/dev/null

echo "Ports 8000 et 8001 libérés" 