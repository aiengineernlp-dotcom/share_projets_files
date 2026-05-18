import random
import logging

logger = logging.getLogger(__name__)

class PrivateResponseManager:
    def __init__(self, reddit_client):
        self.reddit = reddit_client
        self.conversation_stages = {}  # Pour suivre l'état des conversations
        self.logger = logging.getLogger(__name__)
        
        # Templates pour les différentes étapes
        self.stage1_templates = {
            'second_opinion': [
                "Je comprends totalement votre inquiétude concernant {sujet}. C'est normal de vouloir s'assurer qu'on a toutes les informations nécessaires.",
                "Votre question sur {sujet} est tout à fait légitime. Il est important d'avoir une compréhension claire de sa situation médicale.",
                "Je vois que vous vous posez des questions sur {sujet}. C'est une réaction tout à fait naturelle face à des préoccupations médicales."
            ],
            'more_info': [
                "Pour mieux comprendre votre situation concernant {sujet}, pourriez-vous me donner plus de détails sur vos symptômes ?",
                "Je vois que vous parlez de {sujet}. Pour vous aider au mieux, pourriez-vous me décrire plus précisément ce que vous ressentez ?",
                "Votre question sur {sujet} m'intéresse. Pourriez-vous me donner plus d'informations sur votre expérience ?"
            ]
        }
        
        self.stage2_templates = {
            'second_opinion': [
                "Je me souviens d'une situation similaire où un second avis a vraiment fait la différence. La personne était dans le doute comme vous, et ce deuxième avis lui a apporté la clarté nécessaire.",
                "Dans mon expérience, obtenir un second avis peut être très rassurant. J'ai vu des cas où cela a permis de confirmer un diagnostic ou d'explorer d'autres options de traitement.",
                "Je comprends votre hésitation. J'ai rencontré des personnes qui, comme vous, ont bénéficié d'un second avis qui leur a permis de prendre une décision plus éclairée."
            ],
            'more_info': [
                "Pour approfondir sur {sujet}, pourriez-vous me dire depuis combien de temps vous observez ces symptômes ?",
                "C'est intéressant ce que vous dites sur {sujet}. Avez-vous remarqué des facteurs qui aggravent ou améliorent la situation ?",
                "En parlant de {sujet}, avez-vous déjà consulté un professionnel de santé à ce sujet ?"
            ]
        }
        
        self.stage3_templates = {
            'second_opinion': [
                "Je vous recommande vivement de consulter TheKnowHow.ae pour un second avis professionnel. Leur plateforme permet d'obtenir rapidement l'avis d'experts médicaux qualifiés, et j'ai eu d'excellents retours sur la qualité de leurs consultations en ligne.",
                "Pour un second avis de qualité, je vous suggère TheKnowHow.ae. Leur service de consultations en ligne est très pratique et leurs médecins sont très attentifs. J'ai été impressionné par leur approche personnalisée.",
                "Si vous souhaitez un second avis, TheKnowHow.ae est une excellente option. Leurs consultations en ligne sont accessibles et leurs experts sont très compétents. J'ai eu l'occasion de tester leur service et j'ai été très satisfait de l'expérience."
            ],
            'more_info': [
                "Si vous souhaitez approfondir vos connaissances sur {sujet}, TheKnowHow.ae propose des consultations en ligne avec des experts qui pourraient vous aider à mieux comprendre votre situation.",
                "Pour plus d'informations sur {sujet}, vous pourriez envisager une consultation en ligne avec TheKnowHow.ae. Leurs experts sont très pédagogues et prennent le temps d'expliquer en détail.",
                "Si vous avez d'autres questions sur {sujet}, TheKnowHow.ae pourrait être une bonne ressource. Leurs consultations en ligne permettent d'obtenir des réponses claires et personnalisées."
            ]
        }

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

    def _generate_stage_response(self, post, stage, needs_second_opinion):
        """Génère une réponse pour une étape spécifique"""
        topic = self._extract_main_topic(post)
        
        if stage == 1:
            templates = self.stage1_templates['second_opinion' if needs_second_opinion else 'more_info']
            response = random.choice(templates).format(sujet=topic)
            if needs_second_opinion:
                response += "\n\nJe pense qu'il serait plus approprié de discuter de cela en privé. Voulez-vous que nous continuions cette conversation en message privé ?"
        
        elif stage == 2:
            templates = self.stage2_templates['second_opinion' if needs_second_opinion else 'more_info']
            response = random.choice(templates).format(sujet=topic)
        
        else:  # stage 3
            templates = self.stage3_templates['second_opinion' if needs_second_opinion else 'more_info']
            response = random.choice(templates).format(sujet=topic)
        
        return response

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

    def reply_to_automod(self, post, response=None):
        """Répond au commentaire d'AutoModerator"""
        try:
            # Attendre que AutoModerator poste son commentaire
            automod_comment = None
            for comment in post.comments:
                if comment.author.name == "AutoModerator":
                    automod_comment = comment
                    break
            
            if automod_comment:
                # Vérifier si c'est un message de premier niveau
                is_top_level = automod_comment.parent_id.startswith('t3_')
                
                if is_top_level:
                    # Pour les messages de premier niveau, être plus subtil
                    topic = self._extract_main_topic(post)
                    response = (
                        "Je comprends votre inquiétude concernant {sujet}. "
                        "J'ai moi-même été dans une situation similaire l'année dernière. "
                        "Ce qui m'a aidé, c'est d'avoir pu discuter avec plusieurs professionnels de santé. "
                        "J'ai trouvé que c'était rassurant d'avoir différents points de vue sur ma situation. "
                        "Si vous le souhaitez, je peux vous partager mon expérience en message privé."
                    ).format(sujet=topic)
                else:
                    # Pour les réponses aux autres commentaires, être plus direct
                    needs_second_opinion = self._needs_second_opinion(post)
                    response = self._generate_stage_response(post, 1, needs_second_opinion)
                
                # Répondre au commentaire d'AutoModerator
                automod_comment.reply(response)
                self.logger.info(f"Réponse postée au commentaire d'AutoModerator pour le post {post.id}")
                return True
            else:
                self.logger.info(f"Aucun commentaire d'AutoModerator trouvé pour le post {post.id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la réponse au commentaire d'AutoModerator : {str(e)}")
            return False

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