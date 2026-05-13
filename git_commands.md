# 🚀 Commandes Git Utiles

## Rafraîchir .gitignore (Force update)
À utiliser quand un fichier ignoré continue d'apparaître :
```bash
git rm -r --cached .
git add .
git commit -m "Fix: réinitialisation du cache .gitignore"
git push origin main
```

## Annuler le dernier commit (en gardant les modifs)
```bash
git reset --soft HEAD~1
```
