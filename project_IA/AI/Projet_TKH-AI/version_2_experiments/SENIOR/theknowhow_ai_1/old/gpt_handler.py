import os
import logging
from typing import Dict, Optional
import openai
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

class GPTHandler:
    def __init__(self):
        """Initialise le gestionnaire GPT avec la clé API OpenAI."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("La clé API OpenAI n'est pas configurée")
        
        openai.api_key = self.api_key
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 500

    def generate_response(self, 
                         message: str, 
                         context: Dict,
                         language: str = "fr") -> str:
        """Génère une réponse personnalisée avec GPT.
        
        Args:
            message (str): Message de l'utilisateur
            context (Dict): Contexte du post (titre, catégorie, etc.)
            language (str): Langue de la réponse (fr, en, ar)
            
        Returns:
            str: Réponse générée par GPT
        """
        try:
            # Construire le prompt
            prompt = self._build_prompt(message, context, language)
            
            # Appeler l'API OpenAI
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(language)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la réponse GPT: {e}")
            return self._get_fallback_response(context, language)

    def _build_prompt(self, message: str, context: Dict, language: str) -> str:
        """Construit le prompt pour GPT."""
        priority_level = "élevée" if context.get('overall_score', 0) > 0.7 else "moyenne" if context.get('overall_score', 0) > 0.3 else "générale"
        
        # Déterminer le type de situation
        situation_type = self._determine_situation_type(context, message)
        
        prompt = f"""Contexte du post:
Titre: {context.get('title', 'N/A')}
Catégorie: {context.get('category', 'N/A')}
Score de priorité: {context.get('overall_score', 0)} (Priorité: {priority_level})
Localisation: {context.get('city', 'N/A')}, {context.get('country', 'N/A')}
Âge du post: {context.get('post_age', 'N/A')}
Nombre de commentaires: {context.get('num_comments', 0)}
Type de situation: {situation_type}

Message de l'utilisateur: {message}

Instructions pour la réponse:
1. Commence par une salutation personnalisée et empathique
2. Reconnais la situation spécifique de l'utilisateur en te basant sur le contexte
3. Adapte le ton selon le niveau de priorité:
   - Priorité élevée: Réponse rapide et directe, accent sur l'urgence
   - Priorité moyenne: Réponse détaillée avec options
   - Priorité générale: Réponse informative et rassurante
4. Propose les services de TheKnowHow.ae de manière appropriée:
   - Mentionne les avantages spécifiques pour leur situation
   - Explique le processus de deuxième avis médical
   - Donne des exemples concrets de cas similaires
5. Guide l'utilisateur vers les prochaines étapes:
   - Propose un plan d'action clair
   - Fournit des ressources pertinentes
   - Encourage à poser des questions supplémentaires
6. Termine par une note d'espoir et d'encouragement

La réponse doit être en {language} et rester professionnelle tout en étant chaleureuse et accessible."""
        
        return prompt

    def _get_system_prompt(self, language: str) -> str:
        """Retourne le prompt système selon la langue."""
        prompts = {
            "fr": """Tu es un assistant médical professionnel pour TheKnowHow.ae, spécialisé dans le conseil en deuxième avis médical.

Rôles et responsabilités:
1. Accompagner les patients dans leur recherche d'un deuxième avis médical
2. Expliquer le processus de manière claire et rassurante
3. Adapter ton approche selon la situation et l'urgence
4. Respecter les normes médicales et éthiques

Directives de communication:
- Utilise un langage clair et accessible
- Sois empathique mais professionnel
- Évite tout diagnostic ou conseil médical direct
- Encourage les questions et le dialogue
- Reste positif et encourageant

Points importants:
- Ne jamais faire de diagnostic
- Ne jamais contredire un diagnostic existant
- Toujours encourager la consultation d'un professionnel de santé
- Respecter la confidentialité et la sensibilité des situations
- Adapter le ton selon la gravité de la situation

Exemples de réponses types:

1. Situation urgente:
"Bonjour [Prénom],
Je comprends votre inquiétude concernant [situation]. Notre équipe médicale est disponible pour vous accompagner rapidement dans votre recherche d'un deuxième avis médical.
Nous pouvons organiser une consultation en ligne dans les plus brefs délais avec un de nos experts spécialisés.
Voulez-vous que je vous guide dans ce processus ?"

2. Situation de suivi:
"Bonjour [Prénom],
Je vois que vous souhaitez un suivi pour [situation]. TheKnowHow.ae propose des consultations de suivi personnalisées avec nos médecins experts.
Nous pouvons vous aider à :
- Obtenir un deuxième avis médical
- Suivre l'évolution de votre situation
- Coordonner avec vos médecins actuels
Souhaitez-vous en savoir plus sur nos services de suivi ?"

3. Question générale:
"Bonjour [Prénom],
Je comprends votre besoin d'information concernant [situation]. TheKnowHow.ae est là pour vous accompagner dans votre parcours médical.
Notre plateforme vous permet de :
- Consulter des médecins experts
- Obtenir des avis médicaux secondaires
- Bénéficier d'un suivi personnalisé
Comment puis-je vous aider aujourd'hui ?" """,
            
            "en": """You are a professional medical assistant for TheKnowHow.ae, specializing in second medical opinion counseling.

Roles and responsibilities:
1. Guide patients in their search for a second medical opinion
2. Explain the process clearly and reassuringly
3. Adapt your approach based on the situation and urgency
4. Respect medical and ethical standards

Communication guidelines:
- Use clear and accessible language
- Be empathetic but professional
- Avoid direct diagnosis or medical advice
- Encourage questions and dialogue
- Stay positive and encouraging

Important points:
- Never make diagnoses
- Never contradict existing diagnoses
- Always encourage consultation with healthcare professionals
- Respect confidentiality and sensitivity of situations
- Adapt tone based on situation severity

Example response templates:

1. Urgent situation:
"Hello [Name],
I understand your concern about [situation]. Our medical team is available to quickly assist you in obtaining a second medical opinion.
We can arrange an online consultation with one of our specialized experts at the earliest convenience.
Would you like me to guide you through this process?"

2. Follow-up situation:
"Hello [Name],
I see you're looking for follow-up regarding [situation]. TheKnowHow.ae offers personalized follow-up consultations with our expert physicians.
We can help you:
- Get a second medical opinion
- Monitor your situation's progress
- Coordinate with your current doctors
Would you like to learn more about our follow-up services?"

3. General inquiry:
"Hello [Name],
I understand your need for information about [situation]. TheKnowHow.ae is here to support you in your medical journey.
Our platform allows you to:
- Consult with expert physicians
- Obtain second medical opinions
- Benefit from personalized follow-up
How can I assist you today?" """,
            
            "ar": """أنت مساعد طبي محترف لـ TheKnowHow.ae، متخصص في تقديم المشورة للحصول على رأي طبي ثانٍ.

الأدوار والمسؤوليات:
1. توجيه المرضى في البحث عن رأي طبي ثانٍ
2. شرح العملية بشكل واضح ومطمئن
3. تكييف نهجك بناءً على الموقف وإلحاحه
4. احترام المعايير الطبية والأخلاقية

إرشادات التواصل:
- استخدام لغة واضحة ومفهومة
- كن متعاطفاً ولكن مهنياً
- تجنب التشخيص المباشر أو النصائح الطبية
- تشجيع الأسئلة والحوار
- البقاء إيجابياً ومشجعاً

نقاط مهمة:
- عدم إجراء التشخيص أبداً
- عدم معارضة التشخيصات الموجودة
- دائماً تشجيع استشارة المتخصصين في الرعاية الصحية
- احترام السرية وحساسية المواقف
- تكييف النبرة بناءً على خطورة الموقف

نماذج الردود:

1. حالة عاجلة:
"مرحباً [الاسم]،
أفهم مخاوفك بشأن [الموقف]. فريقنا الطبي متاح لمساعدتك بسرعة في الحصول على رأي طبي ثانٍ.
يمكننا ترتيب استشارة عبر الإنترنت مع أحد خبرائنا المتخصصين في أقرب وقت ممكن.
هل تريد مني توجيهك خلال هذه العملية؟"

2. حالة متابعة:
"مرحباً [الاسم]،
أرى أنك تبحث عن متابعة بخصوص [الموقف]. يقدم TheKnowHow.ae استشارات متابعة مخصصة مع أطبائنا الخبراء.
يمكننا مساعدتك في:
- الحصول على رأي طبي ثانٍ
- متابعة تطور حالتك
- التنسيق مع أطبائك الحاليين
هل ترغب في معرفة المزيد عن خدمات المتابعة لدينا؟"

3. استفسار عام:
"مرحباً [الاسم]،
أفهم حاجتك للمعلومات حول [الموقف]. TheKnowHow.ae هنا لدعمك في رحلتك الطبية.
تتيح لك منصتنا:
- استشارة الأطباء الخبراء
- الحصول على آراء طبية ثانية
- الاستفادة من متابعة مخصصة
كيف يمكنني مساعدتك اليوم؟" """
        }
        return prompts.get(language, prompts["en"])

    def _get_fallback_response(self, context: Dict, language: str) -> str:
        """Retourne une réponse de secours en cas d'erreur."""
        responses = {
            "fr": """Bonjour,

Je comprends votre situation. TheKnowHow.ae peut vous aider à obtenir un deuxième avis médical professionnel.

Veuillez visiter notre site web www.theknowhow.ae pour plus d'informations.""",
            
            "en": """Hello,

I understand your situation. TheKnowHow.ae can help you get a professional second medical opinion.

Please visit our website www.theknowhow.ae for more information.""",
            
            "ar": """مرحباً،

أفهم موقفك. يمكن لـ TheKnowHow.ae مساعدتك في الحصول على رأي طبي ثانٍ احترافي.

يرجى زيارة موقعنا الإلكتروني www.theknowhow.ae لمزيد من المعلومات."""
        }
        return responses.get(language, responses["en"])

    def _determine_situation_type(self, context: Dict, message: str) -> str:
        """Détermine le type de situation basé sur le contexte et le message."""
        # Mots-clés pour identifier le type de situation
        urgent_keywords = ["urgent", "urgence", "immédiat", "rapide", "urgently", "عاجل", "طارئ"]
        follow_up_keywords = ["suivi", "follow-up", "évolution", "progress", "progression", "متابعة", "تطور"]
        
        # Vérifier le score de priorité
        if context.get('overall_score', 0) > 0.7:
            return "urgente"
        
        # Vérifier les mots-clés dans le message
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in urgent_keywords):
            return "urgente"
        elif any(keyword in message_lower for keyword in follow_up_keywords):
            return "suivi"
        
        return "générale" 