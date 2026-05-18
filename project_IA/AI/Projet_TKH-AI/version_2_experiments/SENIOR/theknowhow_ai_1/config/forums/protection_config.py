"""
Configuration commune pour la gestion des protections et des limites d'accès aux forums.
"""

import random
from datetime import timedelta, datetime
from urllib.parse import urlparse

# Configuration des User-Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Configuration des proxies
PROXY_CONFIG = {
    "enabled": False,  # À activer si nécessaire
    "proxy_list": [
        # Liste à remplir avec des proxies valides
        # Format: "protocol://ip:port"
    ],
    "rotation_interval": timedelta(minutes=30),
    "max_consecutive_failures": 3,
    "verify_ssl": True
}

# Configuration anti-CAPTCHA
CAPTCHA_CONFIG = {
    "detection_patterns": [
        "captcha",
        "robot verification",
        "human verification",
        "prove you're human",
        "security check"
    ],
    "max_retries": 3,
    "cooldown_period": timedelta(minutes=15),
    "session_reset_on_captcha": True
}

# Configuration des limites de taux
RATE_LIMITS = {
    "requests_per_minute": {
        "default": 20,
        "healthunlocked": 30,
        "medhelp": 20,
        "patient_info": 25,
        "healthboards": 20,
        "webmd": 15
    },
    "max_requests_per_hour": {
        "default": 1000,
        "healthunlocked": 1500,
        "medhelp": 1000,
        "patient_info": 1200,
        "healthboards": 1000,
        "webmd": 800
    },
    "cooldown_period": timedelta(minutes=5)
}

# Configuration du respect des robots.txt
ROBOTS_TXT_CONFIG = {
    "respect_robots_txt": True,
    "cache_duration": timedelta(hours=24),
    "custom_rules": {
        "healthunlocked": {
            "allowed_paths": ["/communities", "/posts"],
            "disallowed_paths": ["/admin", "/internal"]
        },
        "medhelp": {
            "allowed_paths": ["/forums", "/topics"],
            "disallowed_paths": ["/admin", "/private"]
        },
        "patient_info": {
            "allowed_paths": ["/forums", "/discussions"],
            "disallowed_paths": ["/admin", "/management"]
        },
        "healthboards": {
            "allowed_paths": [
                "/allergies/food-allergies",
                "/allergies/seasonal-allergies",
                "/cancer/breast-cancer",
                "/cancer/lung-cancer",
                "/cancer/skin-cancer",
                "/diabetes/type-1",
                "/diabetes/type-2",
                "/diabetes/gestational",
                "/heart-cardiovascular/heart-disease",
                "/heart-cardiovascular/blood-pressure",
                "/heart-cardiovascular/cholesterol",
                "/mental-health/anxiety",
                "/mental-health/depression",
                "/mental-health/bipolar",
                "/pain-management/chronic-pain",
                "/pain-management/back-pain",
                "/pain-management/fibromyalgia",
                "/skin-hair/acne",
                "/skin-hair/eczema",
                "/skin-hair/psoriasis",
                "/weight-loss/diet",
                "/weight-loss/exercise",
                "/weight-loss/obesity"
            ],
            "disallowed_paths": ["/admin", "/moderator"]
        },
        "webmd": {
            "allowed_paths": ["/messageboards", "/forums"],
            "disallowed_paths": ["/admin", "/internal"]
        }
    }
}

# Configuration de la session HTTP
SESSION_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "backoff_factor": 2,
    "retry_on_status": [500, 502, 503, 504],
    "headers": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }
}

# Configuration des erreurs et récupération
ERROR_HANDLING = {
    "max_consecutive_errors": 5,
    "error_cooldown": timedelta(minutes=10),
    "recoverable_errors": [
        "timeout",
        "connection_error",
        "proxy_error",
        "rate_limit",
        "captcha"
    ],
    "critical_errors": [
        "authentication_failed",
        "ip_banned",
        "permanent_redirect"
    ]
}

# Configuration de la rotation des identités
IDENTITY_ROTATION = {
    "enabled": True,
    "rotation_interval": timedelta(hours=1),
    "components": [
        "user_agent",
        "proxy",
        "cookies",
        "headers"
    ],
    "preserve_session": False
}

# Méthodes utilitaires pour la gestion des protections
def should_rotate_identity(last_rotation_time):
    """Détermine si une rotation d'identité est nécessaire."""
    if not IDENTITY_ROTATION["enabled"]:
        return False
    return (datetime.now() - last_rotation_time) > IDENTITY_ROTATION["rotation_interval"]

def is_rate_limited(forum_name, request_count, timeframe):
    """Vérifie si les limites de taux sont atteintes."""
    limits = RATE_LIMITS["requests_per_minute"].get(forum_name, RATE_LIMITS["requests_per_minute"]["default"])
    return request_count >= limits

def handle_captcha_detection(page_content):
    """Détecte et gère la présence de CAPTCHA."""
    for pattern in CAPTCHA_CONFIG["detection_patterns"]:
        if pattern.lower() in page_content.lower():
            return True
    return False

def get_proxy_settings():
    """Obtient les paramètres de proxy actuels."""
    if not PROXY_CONFIG["enabled"] or not PROXY_CONFIG["proxy_list"]:
        return None
    return random.choice(PROXY_CONFIG["proxy_list"])

def is_path_allowed(forum_name, url):
    """Vérifie si le chemin est autorisé selon les règles robots.txt."""
    if not ROBOTS_TXT_CONFIG["respect_robots_txt"]:
        return True
    
    # Extrait le chemin de l'URL
    path = urlparse(url).path
    
    rules = ROBOTS_TXT_CONFIG["custom_rules"].get(forum_name, {})
    
    # Vérifie d'abord les chemins interdits
    for disallowed in rules.get("disallowed_paths", []):
        if path.startswith(disallowed):
            return False
    
    # Vérifie ensuite les chemins autorisés
    for allowed in rules.get("allowed_paths", []):
        if path.startswith(allowed):
            return True
    
    return False  # Par défaut, refuse l'accès si le chemin n'est pas explicitement autorisé 