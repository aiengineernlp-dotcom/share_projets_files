# 🤖 Machine Learning & AI

## Environnement Virtuel (Venv)
Créer et activer un environnement propre :
```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
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
