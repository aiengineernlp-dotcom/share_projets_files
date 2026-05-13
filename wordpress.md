# 📝 WordPress (WP-CLI & Maintenance)

## Mises à jour rapides
Tout mettre à jour (cœur, plugins et thèmes) en une ligne :
```bash
wp core update && wp plugin update --all && wp theme update --all
```

## Sécurité des fichiers (Permissions)
Rétablir les bonnes permissions via le terminal :
```bash
# Dossiers en 755
find . -type d -exec chmod 755 {} \;
# Fichiers en 644
find . -type f -exec chmod 644 {} \;
# wp-config.php en lecture seule pour le propriétaire
chmod 600 wp-config.php
```

## Base de données
Exporter pour une sauvegarde :
```bash
wp db export backup_$(date +%Y-%m-%d).sql
```
