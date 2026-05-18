"""
Tests unitaires pour le processeur de texte.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.core.data_collection.preprocessing.text_processor import TextProcessor

@pytest.fixture
def text_processor():
    """Instance du processeur de texte pour les tests."""
    return TextProcessor()

@pytest.fixture
def sample_medical_post():
    """Exemple de post médical pour les tests."""
    return {
        'id': 'test_1',
        'title': 'Urgent: High Fever and Cough',
        'content': 'I have been experiencing high fever (39.5°C) and persistent cough for 3 days.',
        'created_at': datetime.now().timestamp()
    }

class TestTextProcessor:
    """Tests pour la classe TextProcessor."""

    def test_init(self):
        """Teste l'initialisation du processeur."""
        processor = TextProcessor()
        assert processor is not None
        assert hasattr(processor, 'process_medical_post')

    def test_basic_processing(self, text_processor, sample_medical_post):
        """Teste le traitement basique d'un post."""
        result = text_processor.process_medical_post(sample_medical_post)
        
        assert 'medical_entities' in result
        assert 'processed_text' in result
        assert isinstance(result['medical_entities'], list)
        assert isinstance(result['processed_text'], str)
        assert len(result['medical_entities']) > 0

    def test_text_cleaning(self, text_processor):
        """Teste le nettoyage du texte."""
        dirty_text = {
            'title': 'Test Post with HTML <b>tags</b>',
            'content': 'Content with http://example.com links and @mentions',
            'created_at': datetime.now().timestamp()
        }
        
        result = text_processor.process_medical_post(dirty_text)
        
        assert '<b>' not in result['processed_text']
        assert 'http://' not in result['processed_text']
        assert '@mentions' not in result['processed_text']

    def test_medical_entity_extraction(self, text_processor):
        """Teste l'extraction d'entités médicales."""
        test_cases = [
            {
                'post': {
                    'title': 'Headache and Fever',
                    'content': 'Severe headache with 39°C fever',
                    'created_at': datetime.now().timestamp()
                },
                'expected_entities': ['headache', 'fever']
            },
            {
                'post': {
                    'title': 'Blood Pressure Issues',
                    'content': 'High blood pressure readings: 150/90',
                    'created_at': datetime.now().timestamp()
                },
                'expected_entities': ['blood pressure', 'high blood pressure']
            }
        ]
        
        for case in test_cases:
            result = text_processor.process_medical_post(case['post'])
            for entity in case['expected_entities']:
                assert any(entity in e.lower() for e in result['medical_entities'])

    def test_number_handling(self, text_processor):
        """Teste le traitement des valeurs numériques."""
        post = {
            'title': 'Temperature and Blood Pressure',
            'content': 'Temperature: 39.5°C, BP: 140/90',
            'created_at': datetime.now().timestamp()
        }
        
        result = text_processor.process_medical_post(post)
        
        # Vérifie que les nombres importants sont préservés
        assert '39.5' in result['processed_text']
        assert '140/90' in result['processed_text']

    def test_special_characters(self, text_processor):
        """Teste le traitement des caractères spéciaux."""
        post = {
            'title': 'Pain Level: ★★★☆☆',
            'content': 'Pain level: 3/5 (⭐⭐⭐)',
            'created_at': datetime.now().timestamp()
        }
        
        result = text_processor.process_medical_post(post)
        
        # Vérifie que le texte est nettoyé mais conserve l'information importante
        assert 'pain level' in result['processed_text'].lower()
        assert '3/5' in result['processed_text']

    def test_language_detection(self, text_processor):
        """Teste la détection de la langue."""
        non_english_post = {
            'title': 'Mal de tête',
            'content': 'J\'ai un très fort mal de tête depuis ce matin.',
            'created_at': datetime.now().timestamp()
        }
        
        with pytest.raises(ValueError):
            text_processor.process_medical_post(non_english_post)

    def test_empty_input(self, text_processor):
        """Teste le comportement avec des entrées vides."""
        empty_post = {
            'title': '',
            'content': '',
            'created_at': datetime.now().timestamp()
        }
        
        result = text_processor.process_medical_post(empty_post)
        
        assert len(result['medical_entities']) == 0
        assert result['processed_text'] == ''

    def test_abbreviation_handling(self, text_processor):
        """Teste le traitement des abréviations médicales."""
        post = {
            'title': 'BP and HR Issues',
            'content': 'BP: 140/90, HR: 100bpm, temp 38.5C',
            'created_at': datetime.now().timestamp()
        }
        
        result = text_processor.process_medical_post(post)
        
        # Vérifie que les abréviations sont correctement traitées
        assert 'blood pressure' in ' '.join(result['medical_entities']).lower()
        assert 'heart rate' in ' '.join(result['medical_entities']).lower()
        assert 'temperature' in ' '.join(result['medical_entities']).lower()

    def test_symptom_context(self, text_processor):
        """Teste la préservation du contexte des symptômes."""
        post = {
            'title': 'Symptoms getting worse',
            'content': 'Headache is severe but fever has improved',
            'created_at': datetime.now().timestamp()
        }
        
        result = text_processor.process_medical_post(post)
        
        # Vérifie que le contexte est préservé
        assert 'severe' in result['processed_text']
        assert 'improved' in result['processed_text']
        assert any('headache' in entity.lower() for entity in result['medical_entities']) 