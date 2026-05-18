"""
Classe de base pour toutes les implémentations de stockage.
"""

from typing import List, Dict, Optional

class BaseStorage:
    def save_data(self, data: List[Dict]) -> bool:
        """Sauvegarde les données dans le stockage."""
        raise NotImplementedError("Cette méthode doit être implémentée par les classes filles")
    
    def get_data(self, id: str) -> Optional[Dict]:
        """Récupère une entrée par son ID."""
        raise NotImplementedError("Cette méthode doit être implémentée par les classes filles")
    
    def update_data(self, id: str, data: Dict) -> bool:
        """Met à jour une entrée existante."""
        raise NotImplementedError("Cette méthode doit être implémentée par les classes filles")
    
    def delete_data(self, id: str) -> bool:
        """Supprime une entrée par son ID."""
        raise NotImplementedError("Cette méthode doit être implémentée par les classes filles")
    
    def close(self):
        """Ferme la connexion au stockage."""
        pass 