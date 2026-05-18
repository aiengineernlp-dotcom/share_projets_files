"""
Gestionnaire de résolution de CAPTCHA
"""
import os
from typing import Optional
import requests
from abc import ABC, abstractmethod

from app.utils.logger import setup_logger

logger = setup_logger("captcha_solver")

class CaptchaSolver(ABC):
    """Classe abstraite pour les solveurs de CAPTCHA"""
    
    @abstractmethod
    async def solve(self, captcha_data: str) -> Optional[str]:
        """
        Résout un CAPTCHA
        
        Args:
            captcha_data: Données du CAPTCHA (URL ou base64)
            
        Returns:
            Optional[str]: Solution ou None en cas d'échec
        """
        pass

class TwoCaptchaSolver(CaptchaSolver):
    """Solveur utilisant le service 2captcha.com"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://2captcha.com/in.php"
        self.result_url = "http://2captcha.com/res.php"
        
    async def solve(self, captcha_data: str) -> Optional[str]:
        """
        Résout un CAPTCHA via 2captcha
        
        Args:
            captcha_data: URL ou données base64 du CAPTCHA
            
        Returns:
            Optional[str]: Solution ou None en cas d'échec
        """
        try:
            # Envoi du CAPTCHA
            data = {
                "key": self.api_key,
                "method": "base64" if "," in captcha_data else "userrecaptcha",
                "json": 1
            }
            
            if "," in captcha_data:
                data["body"] = captcha_data.split(",")[1]
            else:
                data["googlekey"] = captcha_data
                
            response = requests.post(self.base_url, data=data)
            response.raise_for_status()
            result = response.json()
            
            if result["status"] == 0:
                logger.error(f"Erreur 2captcha: {result['request']}")
                return None
                
            # Attente et récupération du résultat
            import asyncio
            await asyncio.sleep(20)  # Attente initiale
            
            for _ in range(30):  # Maximum 30 tentatives
                check_response = requests.get(
                    self.result_url,
                    params={
                        "key": self.api_key,
                        "action": "get",
                        "id": result["request"],
                        "json": 1
                    }
                )
                
                check_result = check_response.json()
                if check_result["status"] == 1:
                    return check_result["request"]
                    
                await asyncio.sleep(5)  # Attente entre les tentatives
                
            logger.error("Timeout lors de la résolution du CAPTCHA")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la résolution du CAPTCHA: {e}")
            return None

class AntiCaptchaSolver(CaptchaSolver):
    """Solveur utilisant le service anti-captcha.com"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anti-captcha.com"
        
    async def solve(self, captcha_data: str) -> Optional[str]:
        """
        Résout un CAPTCHA via anti-captcha
        
        Args:
            captcha_data: URL ou données base64 du CAPTCHA
            
        Returns:
            Optional[str]: Solution ou None en cas d'échec
        """
        # TODO: Implémenter la résolution via anti-captcha.com
        pass

class CaptchaSolverFactory:
    """Factory pour créer des instances de solveurs"""
    
    @staticmethod
    def get_solver(solver_type: str = "2captcha") -> Optional[CaptchaSolver]:
        """
        Retourne une instance de solveur
        
        Args:
            solver_type: Type de solveur ("2captcha" ou "anticaptcha")
            
        Returns:
            Optional[CaptchaSolver]: Instance du solveur ou None
        """
        if solver_type == "2captcha":
            api_key = os.getenv("TWOCAPTCHA_API_KEY")
            if not api_key:
                logger.error("Clé API 2captcha non trouvée")
                return None
            return TwoCaptchaSolver(api_key)
            
        elif solver_type == "anticaptcha":
            api_key = os.getenv("ANTICAPTCHA_API_KEY")
            if not api_key:
                logger.error("Clé API Anti-Captcha non trouvée")
                return None
            return AntiCaptchaSolver(api_key)
            
        logger.error(f"Type de solveur non supporté: {solver_type}")
        return None 