"""
Tests d'intégration pour le prétraitement des données médicales.
"""

import pytest
from pathlib import Path
import logging
from datetime import datetime

from src.core.data_collection.preprocessing.text_processor import TextProcessor
from src.core.data_collection.preprocessing.medical_entities import MedicalEntityExtractor
from src.core.data_collection.preprocessing.text_cleaner import TextCleaner

@pytest.fixture
def preprocessing_components():
    """Initialise les composants de prétraitement pour les tests."""
    return {
        'processor': TextProcessor(),
        'entity_extractor': MedicalEntityExtractor(),
        'text_cleaner': TextCleaner()
    }

@pytest.fixture
def sample_medical_posts():
    """Génère un ensemble de posts médicaux pour les tests."""
    return [
        {
            'id': 'test_1',
            'title': 'Severe Migraine and Nausea',
            'content': 'I've been experiencing intense migraines with nausea for 3 days. Taking Tylenol but no relief. temp=38.5°C',
            'created_at': datetime.now().timestamp()
        },
        {
            'id': 'test_2',
            'title': 'Blood Pressure Concerns',
            'content': 'My BP readings: 150/95 mmHg, feeling dizzy and having headaches. http://example.com/bp-chart',
            'created_at': datetime.now().timestamp()
        },
        {
            'id': 'test_3',
            'title': 'COVID-19 Symptoms?',
            'content': 'Lost sense of smell&taste, mild fever (37.8°C), and dry cough since yesterday. #covid19 #health',
            'created_at': datetime.now().timestamp()
        }
    ]

@pytest.mark.integration
def test_text_cleaning_pipeline(preprocessing_components, sample_medical_posts):
    """
    Teste l'intégration du pipeline de nettoyage de texte.
    """
    text_cleaner = preprocessing_components['text_cleaner']
    
    for post in sample_medical_posts:
        # Nettoyage du titre
        cleaned_title = text_cleaner.clean_text(post['title'])
        assert cleaned_title != ""
        assert "http" not in cleaned_title.lower()
        assert "#" not in cleaned_title
        
        # Nettoyage du contenu
        cleaned_content = text_cleaner.clean_text(post['content'])
        assert cleaned_content != ""
        assert "http" not in cleaned_content.lower()
        assert "#" not in cleaned_content
        
        # Vérification de la conservation des informations médicales importantes
        if "38.5°C" in post['content']:
            assert "38.5" in cleaned_content
        if "150/95" in post['content']:
            assert "150/95" in cleaned_content

@pytest.mark.integration
def test_entity_extraction_pipeline(preprocessing_components, sample_medical_posts):
    """
    Teste l'intégration du pipeline d'extraction d'entités médicales.
    """
    entity_extractor = preprocessing_components['entity_extractor']
    text_cleaner = preprocessing_components['text_cleaner']
    
    for post in sample_medical_posts:
        # Préparation du texte
        cleaned_text = text_cleaner.clean_text(f"{post['title']} {post['content']}")
        
        # Extraction des entités
        entities = entity_extractor.extract_entities(cleaned_text)
        
        # Vérifications spécifiques selon le contenu
        if "migraine" in post['content'].lower():
            assert any("migraine" in entity.lower() for entity in entities)
            assert any("nausea" in entity.lower() for entity in entities)
        
        if "blood pressure" in post['content'].lower():
            assert any("blood pressure" in entity.lower() for entity in entities)
            assert any("dizzy" in entity.lower() for entity in entities)
        
        if "covid" in post['content'].lower():
            assert any(entity.lower() in ["fever", "cough", "anosmia"] for entity in entities)

@pytest.mark.integration
def test_complete_preprocessing_pipeline(preprocessing_components, sample_medical_posts):
    """
    Teste l'intégration complète du pipeline de prétraitement.
    """
    processor = preprocessing_components['processor']
    
    for post in sample_medical_posts:
        # Traitement complet
        processed_data = processor.process_medical_post(post)
        
        # Vérifications de base
        assert 'processed_text' in processed_data
        assert 'medical_entities' in processed_data
        assert processed_data['id'] == post['id']
        
        # Vérification du texte traité
        assert len(processed_data['processed_text']) > 0
        assert "http" not in processed_data['processed_text'].lower()
        assert "#" not in processed_data['processed_text']
        
        # Vérification des entités médicales
        assert len(processed_data['medical_entities']) > 0
        
        # Vérifications spécifiques selon le contenu
        if "migraine" in post['content'].lower():
            assert any("headache" in entity.lower() or "migraine" in entity.lower() 
                      for entity in processed_data['medical_entities'])
        
        if "blood pressure" in post['content'].lower():
            assert any("blood pressure" in entity.lower() or "hypertension" in entity.lower() 
                      for entity in processed_data['medical_entities'])

@pytest.mark.integration
def test_error_handling(preprocessing_components, sample_medical_posts):
    """
    Teste la gestion des erreurs dans le pipeline de prétraitement.
    """
    processor = preprocessing_components['processor']
    
    # Test avec un post invalide
    invalid_post = {
        'id': 'invalid_1',
        'title': None,
        'content': ''
    }
    
    # Vérification de la gestion des erreurs
    try:
        processed_data = processor.process_medical_post(invalid_post)
        assert processed_data['processed_text'] == ""
        assert len(processed_data['medical_entities']) == 0
    except Exception as e:
        assert str(e) != ""  # L'erreur doit être explicite
    
    # Test avec du contenu malformé
    malformed_post = {
        'id': 'malformed_1',
        'title': 'Test <script>alert("xss")</script>',
        'content': 'Content with HTML <b>tags</b> and http://malicious.com links'
    }
    
    processed_data = processor.process_medical_post(malformed_post)
    assert "<script>" not in processed_data['processed_text']
    assert "http://" not in processed_data['processed_text']
    assert "<b>" not in processed_data['processed_text']

@pytest.mark.integration
def test_data_consistency(preprocessing_components, sample_medical_posts):
    """
    Teste la cohérence des données à travers le pipeline de prétraitement.
    """
    processor = preprocessing_components['processor']
    
    for post in sample_medical_posts:
        # Premier traitement
        first_process = processor.process_medical_post(post)
        
        # Deuxième traitement du même post
        second_process = processor.process_medical_post(post)
        
        # Vérification de la cohérence
        assert first_process['processed_text'] == second_process['processed_text']
        assert set(first_process['medical_entities']) == set(second_process['medical_entities'])
        
        # Vérification de la préservation des informations importantes
        assert post['id'] in first_process['processed_text']
        
        # Vérification que les valeurs numériques médicales sont préservées
        if any(temp in post['content'] for temp in ['37.8°C', '38.5°C']):
            assert any(temp.replace('°C', '') in first_process['processed_text'] 
                      for temp in ['37.8', '38.5'])
        
        if '150/95' in post['content']:
            assert '150/95' in first_process['processed_text']

@pytest.mark.integration
def test_special_cases(preprocessing_components):
    """
    Teste le traitement de cas spéciaux dans le pipeline de prétraitement.
    """
    processor = preprocessing_components['processor']
    
    # Test avec des unités médicales
    special_cases = [
        {
            'id': 'special_1',
            'title': 'Lab Results',
            'content': 'WBC: 11.5 x10^9/L, RBC: 4.2 x10^12/L, Hb: 14.2 g/dL',
            'created_at': datetime.now().timestamp()
        },
        {
            'id': 'special_2',
            'title': 'Medication Dosage',
            'content': 'Taking 500mg Amoxicillin 3x/day and 50μg Levothyroxine',
            'created_at': datetime.now().timestamp()
        }
    ]
    
    for case in special_cases:
        processed_data = processor.process_medical_post(case)
        
        # Vérification de la préservation des valeurs numériques et unités
        if 'WBC' in case['content']:
            assert '11.5' in processed_data['processed_text']
            assert any('wbc' in entity.lower() for entity in processed_data['medical_entities'])
        
        if 'Amoxicillin' in case['content']:
            assert '500' in processed_data['processed_text']
            assert any('amoxicillin' in entity.lower() for entity in processed_data['medical_entities']) 