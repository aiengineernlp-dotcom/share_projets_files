"""
Configuration pour le scraper de Dubai Forum.
"""

CONFIG = {
    'SITE_NAME': 'Dubai Forum',
    'BASE_URL': 'https://www.dubaiforum.com',
    'DB_PATH_ENV': 'DUBAI_FORUM_DB_PATH',
    'DEFAULT_LANGUAGE': 'ar',
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
        'category': 'div.thread-category',
        'tags': 'div.thread-tags a',
        'thread_links': 'div.thread-list a.thread-link',
        'next_page': 'a.next-page',
        'replies': 'div.reply-content',
        'reply_author': 'span.reply-author',
        'reply_date': 'span.reply-date'
    },
    'CATEGORIES': {
        'health': '/health',
        'doctors': '/doctors',
        'hospitals': '/hospitals',
        'pharmacies': '/pharmacies',
        'medical_insurance': '/medical-insurance'
    },
    'HTTP_HEADERS': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    'KEYWORDS': [
        'صحة', 'مرض', 'علاج', 'وقاية', 'أعراض', 'تشخيص', 'طبيب', 'مستشفى',
        'health', 'disease', 'treatment', 'prevention', 'symptoms', 'diagnosis', 'doctor', 'hospital'
    ]
} 