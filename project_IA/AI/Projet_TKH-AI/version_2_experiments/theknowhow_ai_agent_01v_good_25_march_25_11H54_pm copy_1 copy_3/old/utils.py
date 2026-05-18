from typing import Dict, Any, List

def is_gcc_country(country: str) -> bool:
    """Vérifie si le pays fait partie du GCC."""
    gcc_countries = {
        # Arabie Saoudite
        'Saudi Arabia', 'Saudi', 'Arabie Saoudite', 'Arabie', 'KSA',
        # Émirats Arabes Unis
        'UAE', 'United Arab Emirates', 'Emirates', 'Dubai', 'Dubai UAE',
        'Abu Dhabi', 'Sharjah', 'Émirats Arabes Unis', 'EAU',
        # Qatar
        'Qatar', 'Doha', 'Qatar UAE',
        # Koweït
        'Kuwait', 'Koweït', 'Kuwait City',
        # Bahreïn
        'Bahrain', 'Bahreïn', 'Manama',
        # Oman
        'Oman', 'Muscat', 'Sultanate of Oman'
    }
    return country in gcc_countries if country else False

def is_african_country(country: str) -> bool:
    """Vérifie si le pays fait partie de l'Afrique."""
    african_countries = {
        # Afrique Centrale
        'Cameroun', 'Cameroon', 'République centrafricaine', 'Central African Republic',
        'Tchad', 'Chad', 'Congo', 'République démocratique du Congo', 'DR Congo', 'DRC',
        'Guinée équatoriale', 'Equatorial Guinea', 'Gabon', 'São Tomé et Príncipe',
        'Sao Tome and Principe',

        # Afrique de l'Est
        'Burundi', 'Comores', 'Comoros', 'Djibouti', 'Érythrée', 'Eritrea', 'Éthiopie',
        'Ethiopia', 'Kenya', 'Madagascar', 'Malawi', 'Maurice', 'Mauritius', 'Mozambique',
        'Rwanda', 'Seychelles', 'Somalie', 'Somalia', 'Soudan du Sud', 'South Sudan',
        'Tanzanie', 'Tanzania', 'Ouganda', 'Uganda',

        # Afrique de l'Ouest
        'Bénin', 'Benin', 'Burkina Faso', 'Cap-Vert', 'Cape Verde', 'Côte d\'Ivoire',
        'Ivory Coast', 'Gambie', 'Gambia', 'Ghana', 'Guinée', 'Guinea', 'Guinée-Bissau',
        'Guinea-Bissau', 'Libéria', 'Liberia', 'Mali', 'Mauritanie', 'Mauritania',
        'Niger', 'Nigeria', 'Sénégal', 'Senegal', 'Sierra Leone', 'Togo',

        # Afrique du Sud
        'Afrique du Sud', 'South Africa', 'Angola', 'Botswana', 'Lesotho', 'Namibie',
        'Namibia', 'Eswatini', 'Swaziland', 'Zambie', 'Zambia', 'Zimbabwe'
    }
    return country in african_countries if country else False

def get_african_region(country: str) -> str:
    """Détermine la région africaine d'un pays."""
    central_africa = {
        'Cameroun', 'Cameroon', 'République centrafricaine', 'Central African Republic',
        'Tchad', 'Chad', 'Congo', 'République démocratique du Congo', 'DR Congo', 'DRC',
        'Guinée équatoriale', 'Equatorial Guinea', 'Gabon', 'São Tomé et Príncipe',
        'Sao Tome and Principe'
    }
    
    east_africa = {
        'Burundi', 'Comores', 'Comoros', 'Djibouti', 'Érythrée', 'Eritrea', 'Éthiopie',
        'Ethiopia', 'Kenya', 'Madagascar', 'Malawi', 'Maurice', 'Mauritius', 'Mozambique',
        'Rwanda', 'Seychelles', 'Somalie', 'Somalia', 'Soudan du Sud', 'South Sudan',
        'Tanzanie', 'Tanzania', 'Ouganda', 'Uganda'
    }
    
    west_africa = {
        'Bénin', 'Benin', 'Burkina Faso', 'Cap-Vert', 'Cape Verde', 'Côte d\'Ivoire',
        'Ivory Coast', 'Gambie', 'Gambia', 'Ghana', 'Guinée', 'Guinea', 'Guinée-Bissau',
        'Guinea-Bissau', 'Libéria', 'Liberia', 'Mali', 'Mauritanie', 'Mauritania',
        'Niger', 'Nigeria', 'Sénégal', 'Senegal', 'Sierra Leone', 'Togo'
    }
    
    south_africa = {
        'Afrique du Sud', 'South Africa', 'Angola', 'Botswana', 'Lesotho', 'Namibie',
        'Namibia', 'Eswatini', 'Swaziland', 'Zambie', 'Zambia', 'Zimbabwe'
    }
    
    if country in central_africa:
        return "Afrique Centrale"
    elif country in east_africa:
        return "Afrique de l'Est"
    elif country in west_africa:
        return "Afrique de l'Ouest"
    elif country in south_africa:
        return "Afrique du Sud"
    else:
        return "Autre"

def extract_location(text: str) -> Dict[str, Any]:
    """Extrait les informations de localisation à partir du texte."""
    location_info = {
        'country': None,
        'city': None,
        'region': None,
        'latitude': None,
        'longitude': None
    }
    
    # À implémenter avec un service de géolocalisation
    # Pour l'instant, on retourne des valeurs par défaut
    return location_info 