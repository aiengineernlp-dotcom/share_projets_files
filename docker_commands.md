# 🐳 Commandes Docker Utiles

## Nettoyage (Prune)
Supprimer TOUT ce qui n'est pas utilisé (containers, images, networks) :
```bash
docker system prune -a --volumes
```

## Gestion des Conteneurs
Arrêter tous les conteneurs en cours :
```bash
docker stop $(docker ps -q)
```

Supprimer tous les conteneurs (même arrêtés) :
```bash
docker rm $(docker ps -a -q)
```

## Docker Compose
Lancer en arrière-plan et forcer la reconstruction :
```bash
docker-compose up -d --build
```
