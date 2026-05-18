"""
Template pour le scraping d'URLs de sites médicaux.
Ce template fournit une structure de base pour collecter des informations depuis des sites web médicaux.
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import urljoin

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MedicalWebScraper:
    """Classe template pour le scraping de sites web médicaux."""
    
    def __init__(self, base_url: str, headers: Optional[Dict] = None):
        """
        Initialise le scraper.
        
        Args:
            base_url (str): URL de base du site médical
            headers (Dict, optional): Headers HTTP personnalisés
        """
        self.base_url = base_url
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (compatible; MedicalBot/1.0; +http://theknowHow.ae)'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Récupère et parse le contenu d'une page.
        
        Args:
            url (str): URL à scraper
            
        Returns:
            BeautifulSoup: Contenu parsé de la page
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de {url}: {str(e)}")
            return None
            
    def extract_medical_questions(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extrait les questions médicales d'une page.
        
        Args:
            soup (BeautifulSoup): Contenu parsé de la page
            
        Returns:
            List[Dict]: Liste des questions médicales trouvées
        """
        questions = []
        # Exemple de sélecteurs à adapter selon le site
        question_elements = soup.select('.medical-question')
        
        for element in question_elements:
            question = {
                'title': element.select_one('.question-title').text.strip(),
                'content': element.select_one('.question-content').text.strip(),
                'author': element.select_one('.author').text.strip(),
                'date': element.select_one('.date').text.strip(),
                'category': element.select_one('.category').text.strip(),
                'url': element.select_one('a')['href'],
                'collected_at': datetime.now().isoformat()
            }
            questions.append(question)
            
        return questions
        
    def classify_urgency(self, content: str) -> str:
        """
        Classifie l'urgence d'une question médicale.
        
        Args:
            content (str): Contenu de la question
            
        Returns:
            str: Niveau d'urgence ('Très Urgent', 'Urgent', 'Normal')
        """
        urgent_keywords = ["urgent", "emergency", "immediate", "severe pain"]
        medical_keywords = ["pain", "symptoms", "bleeding", "fever"]
        
        content_lower = content.lower()
        urgency_score = sum(2 for kw in urgent_keywords if kw in content_lower)
        medical_score = sum(1 for kw in medical_keywords if kw in content_lower)
        
        total_score = urgency_score + medical_score
        if total_score >= 4:
            return "Très Urgent"
        elif total_score >= 2:
            return "Urgent"
        return "Normal"
        
    def scrape_medical_forum(self, max_pages: int = 5) -> List[Dict]:
        """
        Scrape un forum médical complet.
        
        Args:
            max_pages (int): Nombre maximum de pages à scraper
            
        Returns:
            List[Dict]: Liste de toutes les questions médicales trouvées
        """
        all_questions = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/forum/page/{page}"
            soup = self.get_page_content(url)
            
            if not soup:
                break
                
            questions = self.extract_medical_questions(soup)
            for question in questions:
                question['urgency'] = self.classify_urgency(question['content'])
                
            all_questions.extend(questions)
            logger.info(f"Page {page}: {len(questions)} questions collectées")
            
        return all_questions

# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple avec un site médical fictif
    scraper = MedicalWebScraper("https://example-medical-forum.com")
    questions = scraper.scrape_medical_forum(max_pages=3)
    
    print(f"Total des questions collectées: {len(questions)}")
    for urgency in ['Très Urgent', 'Urgent', 'Normal']:
        count = sum(1 for q in questions if q['urgency'] == urgency)
        print(f"{urgency}: {count} questions")
