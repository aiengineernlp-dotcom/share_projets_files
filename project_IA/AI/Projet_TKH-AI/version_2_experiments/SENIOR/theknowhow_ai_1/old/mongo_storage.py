"""
Implémentation du stockage avec MongoDB.
"""

from datetime import datetime
from typing import List, Dict, Any
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from .base_storage import BaseStorage

class MongoStorage(BaseStorage):
    """Stockage des données dans MongoDB."""
    
    def __init__(self, uri: str, db_name: str, collection_name: str):
        """
        Initialise le stockage MongoDB.
        
        Args:
            uri: URI de connexion MongoDB
            db_name: Nom de la base de données
            collection_name: Nom de la collection
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection: Collection = self.db[collection_name]
        self._init_database()
    
    def _init_database(self) -> None:
        """Crée les index nécessaires."""
        # Index sur l'ID pour les recherches rapides
        self.collection.create_index([("id", ASCENDING)], unique=True)
        
        # Index sur le score pour le tri
        self.collection.create_index([("score", ASCENDING)])
        
        # Index TTL sur created_at (suppression après 30 jours)
        self.collection.create_index(
            [("created_at", ASCENDING)],
            expireAfterSeconds=30*24*60*60
        )
    
    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """Sauvegarde les données dans MongoDB."""
        for item in data:
            # Ajout de l'horodatage
            item["created_at"] = datetime.utcnow()
            
            # Upsert : insert si n'existe pas, update si existe
            self.collection.update_one(
                {"id": item["id"]},
                {"$set": item},
                upsert=True
            )
    
    def get_data(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Récupère les données avec les filtres spécifiés."""
        # Conversion des filtres pour MongoDB
        mongo_filters = filters if filters else {}
        
        # Récupération des documents
        cursor = self.collection.find(mongo_filters)
        
        # Conversion en liste de dictionnaires
        # On retire l'ID MongoDB (_id) qui n'est pas sérialisable
        return [{k: v for k, v in doc.items() if k != "_id"} for doc in cursor]
    
    def update_data(self, id: str, data: Dict[str, Any]) -> None:
        """Met à jour les données existantes."""
        # Mise à jour de l'horodatage
        data["updated_at"] = datetime.utcnow()
        
        self.collection.update_one(
            {"id": id},
            {"$set": data}
        )
    
    def delete_data(self, id: str) -> None:
        """Supprime une entrée."""
        self.collection.delete_one({"id": id})
    
    def close(self) -> None:
        """Ferme la connexion au client MongoDB."""
        self.client.close()
    
    # Méthodes spécifiques à MongoDB
    
    def aggregate(self, pipeline: List[Dict]) -> List[Dict]:
        """
        Exécute une agrégation MongoDB.
        
        Args:
            pipeline: Pipeline d'agrégation MongoDB
            
        Returns:
            Résultats de l'agrégation
        """
        return list(self.collection.aggregate(pipeline))
    
    def create_index(self, keys: List[tuple], **kwargs) -> None:
        """
        Crée un index personnalisé.
        
        Args:
            keys: Liste de tuples (champ, direction)
            **kwargs: Options d'index supplémentaires
        """
        self.collection.create_index(keys, **kwargs)
    
    def bulk_write(self, operations: List[Dict]) -> None:
        """
        Exécute des opérations en bulk.
        
        Args:
            operations: Liste d'opérations MongoDB
        """
        self.collection.bulk_write(operations) 