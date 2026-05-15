# 🤖 Machine Learning & AI

## Environnement Virtuel (Venv)
Créer et activer un environnement propre :
```bash
#Créer
python -m venv .env
#activer
source .env/bin/activate  # Mac/Linux
#Créer et activer
python -m venv .env && source .env/bin/activate

pip install pandas numpy scikit-learn torch tensorflow
```

## Nettoyer les Notebooks Jupyter
Indispensable avant de faire un "git push" (supprime les outputs lourds) :
```bash
jupyter nbconvert --clear-output --inplace *.ipynb
```

## Gestion des dépendances
Exporter tes bibliothèques pour ton projet :
```bash
pip freeze > requirements.txt
```

## Vérifier le GPU (Nvidia)
```bash
nvidia-smi
```
