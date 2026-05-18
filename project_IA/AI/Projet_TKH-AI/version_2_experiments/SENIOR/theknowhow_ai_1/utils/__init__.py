"""
Module utils.
Code source extrait de phase__traitement_du_langage_naturel.py (lignes 201-350 : utilitaires)
"""

from .logger import (
    setup_logger,
    get_logger,
    set_log_level,
    add_file_handler,
    add_console_handler,
    remove_handlers,
    create_rotating_file_handler,
    create_timed_rotating_file_handler,
    log_exception,
    log_performance,
    log_memory_usage,
    log_api_call,
    log_data_validation,
    log_model_prediction
)

from .helpers import (
    # Text Utils
    clean_text,
    normalize_text,
    tokenize_text,
    remove_stopwords,
    extract_ngrams,
    count_word_frequencies,
    extract_phrases,
    calculate_text_metrics,
    extract_hashtags,
    extract_mentions,
    extract_urls,
    remove_urls,
    extract_emojis,
    remove_emojis,
    extract_numbers,
    remove_numbers,
    extract_punctuation,
    remove_punctuation,
    extract_whitespace,
    normalize_whitespace,
    
    # Validation Utils
    validate_text,
    validate_text_length,
    validate_text_content,
    validate_text_pattern,
    validate_text_language,
    validate_text_encoding,
    validate_text_sentiment,
    validate_text_urgency,
    validate_text_location,
    validate_text_entities,
    validate_text_keywords,
    validate_text_metrics,
    validate_text_timestamp,
    validate_text_confidence,
    validate_text_severity,
    validate_text_zone
)

__all__ = [
    # Logger
    'setup_logger',
    'get_logger',
    'set_log_level',
    'add_file_handler',
    'add_console_handler',
    'remove_handlers',
    'create_rotating_file_handler',
    'create_timed_rotating_file_handler',
    'log_exception',
    'log_performance',
    'log_memory_usage',
    'log_api_call',
    'log_data_validation',
    'log_model_prediction',
    
    # Text Utils
    'clean_text',
    'normalize_text',
    'tokenize_text',
    'remove_stopwords',
    'extract_ngrams',
    'count_word_frequencies',
    'extract_phrases',
    'calculate_text_metrics',
    'extract_hashtags',
    'extract_mentions',
    'extract_urls',
    'remove_urls',
    'extract_emojis',
    'remove_emojis',
    'extract_numbers',
    'remove_numbers',
    'extract_punctuation',
    'remove_punctuation',
    'extract_whitespace',
    'normalize_whitespace',
    
    # Validation Utils
    'validate_text',
    'validate_text_length',
    'validate_text_content',
    'validate_text_pattern',
    'validate_text_language',
    'validate_text_encoding',
    'validate_text_sentiment',
    'validate_text_urgency',
    'validate_text_location',
    'validate_text_entities',
    'validate_text_keywords',
    'validate_text_metrics',
    'validate_text_timestamp',
    'validate_text_confidence',
    'validate_text_severity',
    'validate_text_zone'
] 