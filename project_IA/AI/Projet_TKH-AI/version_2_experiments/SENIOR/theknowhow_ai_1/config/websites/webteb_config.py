"""
Configuration pour le scraper de WebTeb.
"""

CONFIG = {
    'SITE_NAME': 'WebTeb',
    'BASE_URL': 'https://www.webteb.com',
    'DB_PATH_ENV': 'WEBTEB_DB_PATH',
    'DEFAULT_LANGUAGE': 'ar',
    'MAX_PAGES_PER_CATEGORY': 50,
    'REQUEST_DELAY': 2,
    'RANDOM_DELAY': True,
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 5,
    'SELECTORS': {
        'title': 'h1.article-title',
        'content': 'div.article-content',
        'author': 'span.author-name',
        'date': 'span.publish-date',
        'category': 'div.article-category',
        'tags': 'div.article-tags a',
        'article_links': 'div.article-list a.article-link',
        'next_page': 'a.next-page',
        'comments': 'div.comment-content',
        'comment_author': 'span.comment-author',
        'comment_date': 'span.comment-date'
    },
    'CATEGORIES': {
        'health': '/health',
        'diseases': '/diseases',
        'prevention': '/prevention',
        'medical_research': '/medical-research'
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