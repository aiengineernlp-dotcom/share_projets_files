"""
Configuration pour le site Qatar Living
"""

CONFIG = {
    'SITE_NAME': 'Qatar Living',
    'BASE_URL': 'https://www.qatarliving.com',
    'DB_PATH_ENV': 'QATAR_LIVING_DB_PATH',
    'DEFAULT_LANGUAGE': 'en',
    'MAX_PAGES_PER_CATEGORY': 50,
    'REQUEST_DELAY': 2,
    'RANDOM_DELAY': True,
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 5,
    
    'SELECTORS': {
        'title': 'h1.thread-title',
        'content': 'div.thread-content',
        'author': 'span.thread-author',
        'date': 'span.thread-date',
        'category': 'span.thread-category',
        'tags': 'div.thread-tags a',
        'thread_links': 'div.threads-list a.thread-link',
        'replies': 'div.reply-content',
        'reply_author': 'span.reply-author',
        'reply_date': 'span.reply-date'
    },
    
    'CATEGORIES': {
        'health': {
            'name': 'Health',
            'url': '/forum/health'
        },
        'doctors': {
            'name': 'Doctors',
            'url': '/forum/doctors'
        },
        'hospitals': {
            'name': 'Hospitals',
            'url': '/forum/hospitals'
        },
        'pharmacies': {
            'name': 'Pharmacies',
            'url': '/forum/pharmacies'
        },
        'medical_insurance': {
            'name': 'Medical Insurance',
            'url': '/forum/medical-insurance'
        }
    },
    
    'HTTP_HEADERS': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    
    'KEYWORDS': [
        'health', 'doctor', 'hospital', 'treatment', 'medicine', 'disease', 'prevention',
        'symptoms', 'diagnosis', 'complications', 'advice', 'consultation',
        'صحة', 'طبيب', 'مستشفى', 'علاج', 'دواء', 'مرض', 'وقاية'
    ]
} 