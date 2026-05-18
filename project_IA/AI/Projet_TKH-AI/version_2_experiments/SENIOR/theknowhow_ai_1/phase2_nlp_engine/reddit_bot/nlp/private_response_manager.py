import random
import logging
import time
from typing import List, Dict
from .response_generator import ResponseGenerator

logger = logging.getLogger(__name__)

class PrivateResponseManager:
    def __init__(self, reddit_client):
        self.reddit = reddit_client
        self.conversation_stages = {}  # Pour suivre l'état des conversations
        self.logger = logging.getLogger(__name__)
        self.last_action_time = 0
        self.min_delay = 120  # 2 minutes minimum entre les actions
        self.max_delay = 300  # 5 minutes maximum entre les actions
        self.response_generator = ResponseGenerator()  # Initialiser le générateur de réponses
        
        # Templates pour les réponses en anglais
        self.public_templates = {
            'knee_pain': [
                "I understand your concern about your cousin's knee pain. I've had a similar experience with a meniscus injury, and I know how confusing and worrying it can be when you're not sure about the next steps.",
                "I can relate to your cousin's situation with the knee pain. I've been through a similar journey with a meniscus tear, and I understand how important it is to get clear information about the condition.",
                "Your cousin's knee pain situation resonates with me. I've also dealt with a meniscus injury and know how crucial it is to understand the MRI results and treatment options."
            ],
            'heart': [
                "I understand your concern about the heart fluttering. I've experienced similar cardiac symptoms, and I know how worrying it can be when you're not sure what's causing it.",
                "Your experience with heart palpitations is something I can relate to. I've been through similar concerns about my heart health.",
                "I understand how concerning heart fluttering can be. I've had similar experiences and know how important it is to get proper medical attention."
            ],
            'pregnancy': [
                "I understand your concern about your HCG levels during pregnancy. I've been through similar worries about pregnancy-related tests and results.",
                "Your questions about pregnancy and HCG levels are completely valid. I've had similar concerns during my own pregnancy journey.",
                "I can relate to your concerns about pregnancy test results. I've been through similar situations where test results needed careful interpretation."
            ],
            'skin': [
                "I understand your concern about the skin condition. I've dealt with similar dermatological issues, and I know how important it is to get the right diagnosis.",
                "Your questions about skin conditions are something I can relate to. I've had similar experiences with skin issues that needed proper medical attention.",
                "I understand your concern about the skin growth. I've been through similar situations where getting the right diagnosis was crucial."
            ],
            'default': [
                "I understand your concern about your medical situation. I've been through similar health challenges, and I know how important it is to get the right information.",
                "Your medical questions are completely valid. I've faced similar situations where getting proper medical advice made a big difference.",
                "I can relate to your health concerns. I've been through similar experiences where getting the right medical guidance was crucial."
            ]
        }
        
        self.public_follow_ups = {
            'knee_pain': [
                "What helped me most was consulting with both an orthopedic specialist and a sports medicine doctor. Each had a different perspective on my meniscus injury, and their combined insights helped me make an informed decision about treatment.",
                "In my experience, getting opinions from both a general orthopedic surgeon and a specialist in sports injuries provided valuable insights that helped me understand my options better.",
                "I found that discussing my case with different specialists helped me understand the full range of treatment options available for meniscus injuries."
            ],
            'heart': [
                "Consulting with both a cardiologist and an electrophysiologist helped me understand my heart symptoms better. Each specialist brought different expertise to my case.",
                "What made a difference for me was getting opinions from different cardiac specialists. Their combined insights helped identify the root cause of my symptoms.",
                "I found that getting perspectives from both a general cardiologist and a specialist in heart rhythm disorders provided the most comprehensive understanding of my condition."
            ],
            'pregnancy': [
                "Getting opinions from both my OB-GYN and a maternal-fetal medicine specialist helped me better understand my pregnancy-related concerns.",
                "What helped me most was consulting with specialists who had different areas of expertise in pregnancy care. Their combined knowledge was invaluable.",
                "I found that getting perspectives from both a general obstetrician and a specialist in high-risk pregnancies provided the most comprehensive care."
            ],
            'skin': [
                "Consulting with both a dermatologist and a specialist in skin conditions helped me get a more accurate diagnosis and better treatment options.",
                "What made a difference for me was getting opinions from different skin specialists. Their combined expertise helped identify the best approach for my condition.",
                "I found that getting perspectives from both a general dermatologist and a specialist in skin growths provided the most comprehensive understanding of my situation."
            ],
            'default': [
                "What helped me most was being able to discuss with different specialists. Each had a unique perspective, and it was by combining their approaches that I found relief.",
                "In my case, getting different opinions from healthcare providers made a big difference. Each doctor brought a unique perspective that helped me see the bigger picture.",
                "I found that consulting with multiple specialists gave me a more complete understanding of my condition. Each professional had valuable insights to share."
            ]
        }
        
        self.public_conclusions = [
            "If you'd like, I can share more about my experience and the different approaches that were suggested to me. This could give you some ideas to discuss with your doctor. Feel free to send me a private message if you want to talk more about it.",
            "I'd be happy to share more details about my journey and the different perspectives I received. It might help you in your discussions with your healthcare provider. Don't hesitate to message me privately if you'd like to know more.",
            "I can tell you more about how I navigated through similar challenges and what worked for me. This might give you some ideas to discuss with your doctor. Feel free to reach out in private if you'd like to know more."
        ]

    def _extract_main_topic(self, post):
        """Extrait le sujet principal du post"""
        title = post.title.lower()
        content = post.selftext.lower() if post.selftext else ""
        
        # Liste de sujets médicaux courants
        medical_topics = [
            'douleur', 'symptôme', 'diagnostic', 'traitement', 'médicament',
            'test', 'examen', 'résultat', 'consultation', 'opération'
        ]
        
        for topic in medical_topics:
            if topic in title or topic in content:
                return topic
        return "votre situation médicale"

    def _needs_second_opinion(self, post):
        """Détermine si le post nécessite un second avis"""
        second_opinion_keywords = [
            'second opinion', 'not sure', 'confused', 'wondering',
            'question', 'check', 'skeptical', 'need advice'
        ]
        
        text = f"{post.title} {post.selftext}".lower()
        return any(keyword in text for keyword in second_opinion_keywords)

    def _generate_stage_response(self, post, stage: int, needs_second_opinion: bool) -> str:
        """Génère une réponse appropriée selon le stade de la conversation"""
        topic = self._extract_main_topic(post)
        language = self._detect_language(f"{post.title} {post.selftext}")
        
        if stage == 1:
            # Premier contact
            if needs_second_opinion:
                return self._generate_multilingual_response(topic, post.selftext, language)
            else:
                return self._generate_multilingual_response(topic, post.selftext, language)
        
        elif stage == 2:
            # Suivi
            if needs_second_opinion:
                return self._generate_multilingual_response(topic, post.selftext, language)
            else:
                return self._generate_multilingual_response(topic, post.selftext, language)
        
        else:  # stage 3
            # Conclusion
            if needs_second_opinion:
                return self._generate_multilingual_response(topic, post.selftext, language)
            else:
                return self._generate_multilingual_response(topic, post.selftext, language)

    def can_receive_messages(self, username: str) -> bool:
        """Vérifie si l'utilisateur accepte les messages privés"""
        try:
            user = self.reddit.redditor(username)
            # Essayer d'accéder à un attribut qui nécessite des permissions
            # Si cela échoue, l'utilisateur n'accepte pas les messages
            _ = user.created_utc
            return True
        except Exception as e:
            if "RESTRICTED_TO_PM" in str(e):
                self.logger.warning(f"L'utilisateur {username} n'accepte pas les messages privés")
                return False
            return True

    def send_private_message(self, username: str, subject: str, message: str) -> bool:
        """Envoie un message privé à un utilisateur."""
        try:
            # Essayer d'abord le message direct
            self.reddit.redditor(username).message(subject, message)
            self.logger.info(f"Message privé envoyé à {username}")
            return True
        except Exception as e:
            if "RESTRICTED_TO_PM" in str(e):
                # Si l'utilisateur n'accepte pas les messages, on passe simplement au suivant
                self.logger.info(f"L'utilisateur {username} n'accepte pas les messages - passage au suivant")
                return False
            else:
                self.logger.error(f"Erreur lors de l'envoi du message privé : {str(e)}")
                return False

    def _wait_for_rate_limit(self):
        """Attend le temps nécessaire pour respecter les limites de taux"""
        current_time = time.time()
        time_since_last_action = current_time - self.last_action_time
        
        if time_since_last_action < self.min_delay:
            # Calculer un délai aléatoire entre min_delay et max_delay
            delay = random.uniform(self.min_delay - time_since_last_action, self.max_delay - time_since_last_action)
            self.logger.info(f"Attente de {delay:.2f} secondes pour respecter les limites de taux")
            time.sleep(delay)
        
        self.last_action_time = time.time()

    def _smart_sleep(self, min_delay: int = 120, max_delay: int = 300):
        """Gère une pause intelligente entre les réponses"""
        # Calculer un délai aléatoire
        delay = random.uniform(min_delay, max_delay)
        
        # Ajouter une variation aléatoire pour paraître plus naturel
        variation = random.uniform(-30, 30)
        final_delay = max(min_delay, delay + variation)
        
        self.logger.info(f"Pause intelligente de {final_delay:.2f} secondes")
        time.sleep(final_delay)

    def _detect_language(self, text: str) -> str:
        """Détecte la langue du texte de manière plus sophistiquée"""
        text = text.lower()
        
        # Mots-clés pour chaque langue
        french_keywords = ["je", "vous", "merci", "bonjour", "salut", "merci", "s'il vous plaît", "docteur"]
        spanish_keywords = ["yo", "gracias", "hola", "por favor", "doctor", "médico", "salud"]
        english_keywords = ["i", "you", "thank", "hello", "hi", "doctor", "medical"]
        
        # Compter les occurrences
        french_count = sum(1 for word in french_keywords if word in text)
        spanish_count = sum(1 for word in spanish_keywords if word in text)
        english_count = sum(1 for word in english_keywords if word in text)
        
        # Retourner la langue avec le plus d'occurrences
        counts = {
            "fr": french_count,
            "es": spanish_count,
            "en": english_count
        }
        
        return max(counts.items(), key=lambda x: x[1])[0]

    def _generate_multilingual_response(self, topic: str, post_text: str, language: str = "en") -> str:
        """Génère une réponse dans la langue appropriée"""
        responses = {
            "en": {
                "hair_loss": (
                    "I completely understand your concern about hair loss. "
                    "I went through a similar period after a stressful time, "
                    "and I know how worrying it can be. "
                    "\n\n"
                    "What really helped me was being able to discuss with several specialists who gave me different perspectives. "
                    "Each had a slightly different approach, and it was by combining their advice that I found a solution that worked for me. "
                    "\n\n"
                    "If you'd like, I can share my experience and the solutions that worked for me in detail. "
                    "This could give you some avenues to explore with your doctor. "
                    "Feel free to send me a private message if you want to discuss it further."
                ),
                "pain": (
                    "I understand your concern about the pain. "
                    "I've had to deal with chronic pain that required several medical opinions. "
                    "It's really frustrating when you don't find an immediate solution. "
                    "\n\n"
                    "What helped me the most was being able to discuss with different specialists. "
                    "Each had a unique perspective, and it was by combining their approaches that I finally found relief. "
                    "\n\n"
                    "If you'd like, I can share my experience and the different approaches that were suggested to me. "
                    "This could give you some ideas to explore with your doctor. "
                    "Feel free to send me a private message if you want to discuss it."
                ),
                "default": (
                    "I understand your concern about {topic}. "
                    "I was in a similar situation last year, "
                    "and I know how stressful it can be not to have clear answers. "
                    "\n\n"
                    "What really helped me was being able to discuss with several healthcare professionals. "
                    "Each had a different approach, and it was by combining their perspectives that I was able to better understand my situation. "
                    "\n\n"
                    "If you'd like, I can share my experience and the different approaches that were suggested to me. "
                    "This could give you some avenues to explore with your doctor. "
                    "Feel free to send me a private message if you want to discuss it in more detail."
                )
            },
            "fr": {
                "hair_loss": (
                    "Je comprends parfaitement votre inquiétude concernant la perte de cheveux. "
                    "J'ai moi-même traversé une période similaire après une période de stress intense, "
                    "et je sais à quel point cela peut être inquiétant. "
                    "\n\n"
                    "Ce qui m'a vraiment aidé, c'est d'avoir pu discuter avec plusieurs spécialistes qui m'ont donné des perspectives différentes. "
                    "Chacun avait une approche légèrement différente, et c'est en combinant leurs conseils que j'ai trouvé une solution qui fonctionnait pour moi. "
                    "\n\n"
                    "Si vous le souhaitez, je peux vous partager en détail mon expérience et les solutions qui ont fonctionné pour moi. "
                    "Cela pourrait vous donner des pistes à explorer avec votre médecin. "
                    "N'hésitez pas à m'envoyer un message privé si vous voulez en discuter plus en détail."
                ),
                "pain": (
                    "Je comprends votre inquiétude concernant la douleur. "
                    "J'ai moi-même dû faire face à des douleurs chroniques qui ont nécessité plusieurs avis médicaux. "
                    "C'est vraiment frustrant quand on ne trouve pas de solution immédiate. "
                    "\n\n"
                    "Ce qui m'a le plus aidé, c'est d'avoir pu discuter avec différents spécialistes. "
                    "Chacun avait une perspective unique, et c'est en combinant leurs approches que j'ai finalement trouvé un soulagement. "
                    "\n\n"
                    "Si vous le souhaitez, je peux vous partager mon expérience et les différentes approches qui m'ont été proposées. "
                    "Cela pourrait vous donner des idées à explorer avec votre médecin. "
                    "N'hésitez pas à m'envoyer un message privé si vous voulez en discuter."
                ),
                "default": (
                    "Je comprends votre inquiétude concernant {topic}. "
                    "J'ai moi-même été dans une situation similaire l'année dernière, "
                    "et je sais à quel point cela peut être stressant de ne pas avoir de réponses claires. "
                    "\n\n"
                    "Ce qui m'a vraiment aidé, c'est d'avoir pu discuter avec plusieurs professionnels de santé. "
                    "Chacun avait une approche différente, et c'est en combinant leurs perspectives que j'ai pu mieux comprendre ma situation. "
                    "\n\n"
                    "Si vous le souhaitez, je peux vous partager mon expérience et les différentes approches qui m'ont été proposées. "
                    "Cela pourrait vous donner des pistes à explorer avec votre médecin. "
                    "N'hésitez pas à m'envoyer un message privé si vous voulez en discuter plus en détail."
                )
            },
            "es": {
                "hair_loss": (
                    "Entiendo perfectamente tu preocupación por la pérdida de cabello. "
                    "Yo misma pasé por un período similar después de un momento estresante, "
                    "y sé lo preocupante que puede ser. "
                    "\n\n"
                    "Lo que realmente me ayudó fue poder discutir con varios especialistas que me dieron diferentes perspectivas. "
                    "Cada uno tenía un enfoque ligeramente diferente, y fue combinando sus consejos que encontré una solución que funcionó para mí. "
                    "\n\n"
                    "Si lo deseas, puedo compartir mi experiencia y las soluciones que funcionaron para mí en detalle. "
                    "Esto podría darte algunas vías para explorar con tu médico. "
                    "No dudes en enviarme un mensaje privado si quieres discutirlo más a fondo."
                ),
                "pain": (
                    "Entiendo tu preocupación por el dolor. "
                    "He tenido que lidiar con dolor crónico que requirió varias opiniones médicas. "
                    "Es realmente frustrante cuando no encuentras una solución inmediata. "
                    "\n\n"
                    "Lo que más me ayudó fue poder discutir con diferentes especialistas. "
                    "Cada uno tenía una perspectiva única, y fue combinando sus enfoques que finalmente encontré alivio. "
                    "\n\n"
                    "Si lo deseas, puedo compartir mi experiencia y los diferentes enfoques que me sugirieron. "
                    "Esto podría darte algunas ideas para explorar con tu médico. "
                    "No dudes en enviarme un mensaje privado si quieres discutirlo."
                ),
                "default": (
                    "Entiendo tu preocupación por {topic}. "
                    "Estuve en una situación similar el año pasado, "
                    "y sé lo estresante que puede ser no tener respuestas claras. "
                    "\n\n"
                    "Lo que realmente me ayudó fue poder discutir con varios profesionales de la salud. "
                    "Cada uno tenía un enfoque diferente, y fue combinando sus perspectivas que pude entender mejor mi situación. "
                    "\n\n"
                    "Si lo deseas, puedo compartir mi experiencia y los diferentes enfoques que me sugirieron. "
                    "Esto podría darte algunas vías para explorar con tu médico. "
                    "No dudes en enviarme un mensaje privé si quieres discutirlo más a fondo."
                )
            }
        }

        # Détecter la langue du post
        if "hair loss" in post_text.lower() or "hair" in topic.lower():
            return responses[language]["hair_loss"]
        elif "pain" in post_text.lower() or "pain" in topic.lower():
            return responses[language]["pain"]
        else:
            return responses[language]["default"].format(topic=topic)

    def _get_topic_category(self, post):
        """Détermine la catégorie du post pour utiliser le bon template"""
        text = f"{post.title} {post.selftext}".lower()
        
        if any(word in text for word in ['knee', 'meniscus', 'cartilage', 'joint']):
            return 'knee_pain'
        elif any(word in text for word in ['heart', 'cardiac', 'palpitation', 'flutter']):
            return 'heart'
        elif any(word in text for word in ['pregnant', 'pregnancy', 'hcg', 'baby']):
            return 'pregnancy'
        elif any(word in text for word in ['skin', 'dermat', 'rash', 'wart', 'tag']):
            return 'skin'
        else:
            return 'default'

    def reply_to_automod(self, post, response=None):
        """Respond to AutoModerator's comment"""
        try:
            # Wait to respect rate limits
            self._wait_for_rate_limit()
            
            # Wait for AutoModerator's comment
            automod_comment = None
            for comment in post.comments:
                if comment.author.name == "AutoModerator":
                    automod_comment = comment
                    break
            
            if automod_comment:
                # Check if it's a top-level message
                is_top_level = automod_comment.parent_id.startswith('t3_')
                
                if is_top_level:
                    # Generate response using Ollama
                    response = self._generate_ollama_response(post)
                else:
                    # For replies to other comments, be more direct
                    response = self._generate_ollama_response(post, is_reply=True)
                
                # Reply to AutoModerator's comment
                automod_comment.reply(response)
                self.logger.info(f"Response posted to AutoModerator's comment for post {post.id}")
                
                # Smart pause after response
                self._smart_sleep()
                
                return True
            else:
                self.logger.warning(f"No AutoModerator comment found for post {post.id}")
                return False
            
        except Exception as e:
            if "RATELIMIT" in str(e):
                # Extract suggested wait time
                wait_time = int(str(e).split("Take a break for ")[1].split(" ")[0])
                self.logger.warning(f"Rate limit reached. Waiting for {wait_time} minutes")
                time.sleep(wait_time * 60)  # Convert to seconds
                return self.reply_to_automod(post, response)  # Retry after waiting
            else:
                self.logger.error(f"Error when responding to AutoModerator: {str(e)}")
                return False

    def _generate_ollama_response(self, post, is_reply=False):
        """Generate a response using Ollama"""
        try:
            # Prepare the prompt based on whether it's a reply or top-level comment
            if is_reply:
                prompt = f"""You are a Reddit user sharing a personal medical experience in English.
                The following post is about a medical issue. Generate a SHORT response (2-3 sentences) that:
                1. Shows empathy
                2. Shares a brief relevant experience
                3. Ends with a subtle invitation to discuss privately
                
                Guidelines:
                - Write in English only
                - Keep it VERY concise (max 3 sentences)
                - Be specific about the medical condition
                - Use appropriate medical terminology
                - Keep it natural and conversational
                
                Post: {post.title}\n{post.selftext}
                
                Response:"""
            else:
                prompt = f"""You are a Reddit user sharing a personal medical experience in English.
                The following post is about a medical issue. Generate a CONCISE response (3-4 sentences) that:
                1. Shows empathy and understanding
                2. Shares a brief relevant experience
                3. Provides one key medical insight
                4. Ends with a subtle invitation to discuss privately
                
                Guidelines:
                - Write in English only
                - Keep it concise (max 4 sentences)
                - Be specific about the medical condition
                - Use appropriate medical terminology
                - Keep it natural and conversational
                - Avoid long explanations
                
                Post: {post.title}\n{post.selftext}
                
                Response:"""

            # Generate response using Ollama
            response = self.response_generator.generate_response(prompt)
            
            # Verify the response is in English
            if not self.response_generator._is_english(response):
                self.logger.warning("Generated response is not in English, retrying...")
                response = self.response_generator.generate_response(prompt)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating Ollama response: {str(e)}")
            return "I understand your concern. I've had a similar experience and would be happy to discuss it with you privately if you'd like."

    def handle_conversation(self, post, response=None):
        """Gère la conversation en trois étapes"""
        try:
            # Essayer d'abord de répondre au commentaire d'AutoModerator
            if self.reply_to_automod(post, response):
                return True
                
            # Si cela échoue, essayer le message privé
            author = post.author.name
            needs_second_opinion = self._needs_second_opinion(post)
            
            # Initialiser ou mettre à jour le stade de la conversation
            if author not in self.conversation_stages:
                self.conversation_stages[author] = 1
            else:
                self.conversation_stages[author] = min(self.conversation_stages[author] + 1, 3)
            
            # Générer la réponse appropriée
            response = self._generate_stage_response(
                post,
                self.conversation_stages[author],
                needs_second_opinion
            )
            
            # Envoyer le message
            return self.send_private_message(author, f"À propos de votre post : {post.title[:50]}...", response)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la gestion de la conversation : {str(e)}")
            return False 