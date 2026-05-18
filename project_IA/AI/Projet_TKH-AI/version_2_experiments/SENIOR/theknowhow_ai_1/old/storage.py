"""
Gestionnaire de stockage des données scrapées
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import motor.motor_asyncio
from elasticsearch import AsyncElasticsearch

from app.config import DATA_FOLDERS
from app.utils.logger import setup_logger

logger = setup_logger("storage")

class StorageManager:
    """Gestionnaire de stockage des données"""
    
    def __init__(self):
        # MongoDB
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        )
        self.db = self.mongo_client[os.getenv("MONGODB_DB", "medical_ai")]
        
        # Elasticsearch
        self.es = AsyncElasticsearch(
            [os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")]
        )
        
        # Chemins locaux
        self.raw_data_dir = DATA_FOLDERS["raw"]
        self.processed_data_dir = DATA_FOLDERS["processed"]
        
    async def save_raw_data(self, source_type: str, source_name: str,
                           data: List[Dict[str, Any]]) -> str:
        """
        Sauvegarde les données brutes
        
        Args:
            source_type: Type de source (social_media, medical_forums, etc.)
            source_name: Nom de la source
            data: Données à sauvegarder
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        try:
            # Sauvegarde locale
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = self.raw_data_dir / source_type / source_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{source_name}_raw_{timestamp}.json"
            output_file = output_dir / filename
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            # Sauvegarde MongoDB
            collection = self.db[f"raw_{source_type}_{source_name}"]
            for item in data:
                item["collected_at"] = datetime.now()
                await collection.insert_one(item)
                
            logger.info(f"Données brutes sauvegardées: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données brutes: {e}")
            raise
            
    async def save_processed_data(self, source_type: str, source_name: str,
                                data: List[Dict[str, Any]]) -> str:
        """
        Sauvegarde les données traitées
        
        Args:
            source_type: Type de source
            source_name: Nom de la source
            data: Données à sauvegarder
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        try:
            # Sauvegarde locale
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = self.processed_data_dir / source_type / source_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{source_name}_processed_{timestamp}.json"
            output_file = output_dir / filename
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            # Sauvegarde MongoDB
            collection = self.db[f"processed_{source_type}_{source_name}"]
            for item in data:
                item["processed_at"] = datetime.now()
                await collection.insert_one(item)
                
            # Indexation Elasticsearch
            index_name = f"medical_data_{source_type}_{source_name}"
            for item in data:
                await self.es.index(index=index_name, document=item)
                
            logger.info(f"Données traitées sauvegardées: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des données traitées: {e}")
            raise
            
    async def get_raw_data(self, source_type: str, source_name: str,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Récupère les données brutes
        
        Args:
            source_type: Type de source
            source_name: Nom de la source
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            List[Dict[str, Any]]: Données brutes
        """
        try:
            collection = self.db[f"raw_{source_type}_{source_name}"]
            query = {}
            
            if start_date or end_date:
                query["collected_at"] = {}
                if start_date:
                    query["collected_at"]["$gte"] = start_date
                if end_date:
                    query["collected_at"]["$lte"] = end_date
                    
            cursor = collection.find(query)
            return await cursor.to_list(length=None)
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données brutes: {e}")
            return []
            
    async def search_processed_data(self, query: str,
                                  source_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Recherche dans les données traitées
        
        Args:
            query: Requête de recherche
            source_types: Types de sources à inclure
            
        Returns:
            List[Dict[str, Any]]: Résultats de recherche
        """
        try:
            if source_types:
                indices = [f"medical_data_{st}" for st in source_types]
            else:
                indices = ["medical_data_*"]
                
            response = await self.es.search(
                index=indices,
                body={
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["content", "title", "keywords"]
                        }
                    }
                }
            )
            
            return [hit["_source"] for hit in response["hits"]["hits"]]
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche dans les données: {e}")
            return []
            
    async def cleanup_old_data(self, days: int = 30):
        """
        Nettoie les anciennes données
        
        Args:
            days: Nombre de jours à conserver
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Nettoyage MongoDB
            for collection in await self.db.list_collection_names():
                if collection.startswith(("raw_", "processed_")):
                    await self.db[collection].delete_many({
                        "$or": [
                            {"collected_at": {"$lt": cutoff_date}},
                            {"processed_at": {"$lt": cutoff_date}}
                        ]
                    })
                    
            # Nettoyage Elasticsearch
            for index in await self.es.indices.get("medical_data_*"):
                await self.es.delete_by_query(
                    index=index,
                    body={
                        "query": {
                            "range": {
                                "processed_at": {"lt": cutoff_date.isoformat()}
                            }
                        }
                    }
                )
                
            logger.info(f"Nettoyage des données antérieures à {cutoff_date} terminé")
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des données: {e}")
            raise 