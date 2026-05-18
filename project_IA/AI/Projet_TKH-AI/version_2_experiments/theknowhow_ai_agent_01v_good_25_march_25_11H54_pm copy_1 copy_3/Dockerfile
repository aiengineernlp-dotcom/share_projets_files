# ==============================================
# FICHIER DE CONFIGURATION DOCKER
# ==============================================
#
# RÔLE PRINCIPAL :
# --------------
# Ce Dockerfile définit l'image Docker pour l'application de collecte de données médicales.
# Il configure :
# - L'environnement d'exécution Python
# - Les dépendances système
# - L'installation des packages Python
# - La configuration de l'application
#
# RELATIONS AVEC LES AUTRES FICHIERS :
# ---------------------------------
# - docker-compose.yml : Orchestration des services
# - .dockerignore : Fichiers à exclure de l'image
# - .env : Variables d'environnement
# - poetry.lock : Verrouillage des dépendances
#
# STRUCTURE DU CONTENU :
# --------------------
# Le fichier est organisé en sections :
# 1. Image de base et variables d'environnement
# 2. Installation des dépendances système
# 3. Configuration de Poetry
# 4. Installation des dépendances Python
# 5. Copie du code source
# 6. Configuration des répertoires
# 7. Configuration de l'utilisateur
# 8. Configuration des ports et volumes
# 9. Labels et métadonnées
# 10. Healthcheck
#
# IMPORTANCE ET SUPPRESSION :
# -------------------------
# Ce fichier est CRITIQUE et ne doit PAS être supprimé car :
# - Il est nécessaire pour le déploiement en conteneur
# - Il garantit la reproductibilité de l'environnement
# - Il est utilisé par les pipelines CI/CD
# - Il définit la configuration de production
#
# NOTE DE MAINTENANCE :
# -------------------
# - Maintenir à jour les versions des images de base
# - Vérifier la sécurité des dépendances
# - Optimiser la taille de l'image
# - Documenter les changements dans CHANGELOG.md
#
# ==============================================

# Utiliser une image de base Python officielle
FROM python:3.9-slim-buster

# Définir les variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Ajouter poetry au PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Installer les dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        git \
    && rm -rf /var/lib/apt/lists/*

# Installer Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Créer le répertoire de travail
WORKDIR $PYSETUP_PATH

# Copier les fichiers de configuration
COPY poetry.lock pyproject.toml ./
COPY .env.example ./.env

# Installer les dépendances du projet
RUN poetry install --no-dev --no-root

# Copier le code source
COPY . .

# Installer le projet
RUN poetry install --no-dev

# Créer les répertoires nécessaires
RUN mkdir -p /data/logs /data/cache /data/models /data/backups

# Exposer les ports
EXPOSE 8000

# Définir les volumes
VOLUME ["/data"]

# Définir l'utilisateur non-root
RUN useradd -m -u 1000 app
USER app

# Commande par défaut
CMD ["poetry", "run", "python", "-m", "phase1_data_collection.run_scraper"]

# Labels
LABEL maintainer="TheKnowHow AI Team <contact@theknowhow.ai>" \
      version="1.0.0" \
      description="Collecte et analyse de données médicales - Phase 1" \
      org.label-schema.schema-version="1.0" \
      org.label-schema.name="medical_data_collection" \
      org.label-schema.description="Collecte et analyse de données médicales - Phase 1" \
      org.label-schema.url="https://github.com/theknowhow/medical_data_collection" \
      org.label-schema.vcs-url="https://github.com/theknowhow/medical_data_collection" \
      org.label-schema.vendor="TheKnowHow AI" \
      org.label-schema.version="1.0.0" \
      org.label-schema.docker.cmd="docker run -d -p 8000:8000 -v data:/data theknowhow/medical_data_collection"

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1 