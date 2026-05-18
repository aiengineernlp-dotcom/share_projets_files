"""
Configuration pour le site Altibbi (الطبي)
"""

CONFIG = {
    'SITE_NAME': 'Altibbi',
    'BASE_URL': 'https://www.altibbi.com',
    'DB_PATH_ENV': 'ALTIBBI_DB_PATH',
    'DEFAULT_LANGUAGE': 'ar',
    'MAX_PAGES_PER_CATEGORY': 50,
    'REQUEST_DELAY': 2,
    'RANDOM_DELAY': True,
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 5,
    
    'SELECTORS': {
        'title': 'h1.question-title',
        'content': 'div.question-content',
        'author': 'span.question-author',
        'date': 'span.question-date',
        'category': 'span.question-category',
        'tags': 'div.question-tags a',
        'article_links': 'div.questions-list a.question-link',
        'answers': 'div.answer-content',
        'answer_author': 'span.answer-author',
        'answer_date': 'span.answer-date'
    },
    
    'CATEGORIES': {
        'general_health': {
            'name': 'الصحة العامة',
            'url': '/questions/category/الصحة-العامة'
        },
        'diseases': {
            'name': 'الأمراض',
            'url': '/questions/category/الأمراض'
        },
        'nutrition': {
            'name': 'التغذية',
            'url': '/questions/category/التغذية'
        },
        'mental_health': {
            'name': 'الصحة النفسية',
            'url': '/questions/category/الصحة-النفسية'
        },
        'pregnancy': {
            'name': 'الحمل والولادة',
            'url': '/questions/category/الحمل-والولادة'
        }
    },
    
    'HTTP_HEADERS': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    
    'KEYWORDS': [
        'صحة', 'طبيب', 'مستشفى', 'علاج', 'دواء', 'مرض', 'وقاية',
        'أعراض', 'تشخيص', 'علاج', 'مضاعفات', 'نصائح', 'استشارة',
        'health', 'doctor', 'hospital', 'treatment', 'medicine', 'disease', 'prevention',
        'symptoms', 'diagnosis', 'complications', 'advice', 'consultation'
    ]
} 