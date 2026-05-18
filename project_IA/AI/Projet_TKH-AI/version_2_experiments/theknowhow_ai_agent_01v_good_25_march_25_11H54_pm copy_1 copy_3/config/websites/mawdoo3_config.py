"""
Configuration pour le site Mawdoo3 (موضوع)
"""

CONFIG = {
    'SITE_NAME': 'Mawdoo3',
    'BASE_URL': 'https://mawdoo3.com',
    'DB_PATH_ENV': 'MAWDOO3_DB_PATH',
    'DEFAULT_LANGUAGE': 'ar',
    'MAX_PAGES_PER_CATEGORY': 50,
    'REQUEST_DELAY': 2,
    'RANDOM_DELAY': True,
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 5,
    
    'SELECTORS': {
        'title': 'h1.article-title',
        'content': 'div.article-content',
        'author': 'span.article-author',
        'date': 'span.article-date',
        'category': 'span.article-category',
        'tags': 'div.article-tags a',
        'article_links': 'div.articles-list a.article-link',
        'comments': 'div.comment-content',
        'comment_author': 'span.comment-author',
        'comment_date': 'span.comment-date'
    },
    
    'CATEGORIES': {
        'health': {
            'name': 'الصحة',
            'url': '/category/الصحة'
        },
        'diseases': {
            'name': 'الأمراض',
            'url': '/category/الأمراض'
        },
        'nutrition': {
            'name': 'التغذية',
            'url': '/category/التغذية'
        },
        'mental_health': {
            'name': 'الصحة النفسية',
            'url': '/category/الصحة-النفسية'
        },
        'pregnancy': {
            'name': 'الحمل والولادة',
            'url': '/category/الحمل-والولادة'
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