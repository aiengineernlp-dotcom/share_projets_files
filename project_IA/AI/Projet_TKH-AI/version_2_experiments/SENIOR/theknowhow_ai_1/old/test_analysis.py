"""
Tests d'intégration pour l'analyse des données médicales.
"""

import pytest
from pathlib import Path
import logging
from datetime import datetime

from src.core.data_collection.analysis.medical_analyzer import MedicalAnalyzer
from src.core.data_collection.preprocessing.text_processor import TextProcessor

@pytest.fixture
def analysis_components():
    """Initialise les composants d'analyse pour les tests."""
    return {
        'analyzer': MedicalAnalyzer(),
        'processor': TextProcessor()
    }

@pytest.fixture
def sample_processed_posts():
    """Génère un ensemble de posts prétraités pour les tests."""
    current_time = datetime.now().timestamp()
    return [
        {
            'id': 'emergency_1',
            'title': 'Severe Chest Pain',
            'content': 'Experiencing intense chest pain radiating to left arm, shortness of breath',
            'processed_text': 'severe chest pain radiating left arm shortness breath',
            'medical_entities': ['chest pain', 'radiating pain', 'dyspnea'],
            'created_at': current_time,
            'processed_at': current_time
        },
        {
            'id': 'chronic_1',
            'title': 'Ongoing Joint Pain',
            'content': 'Having joint pain in knees and ankles for 6 months, worse in mornings',
            'processed_text': 'joint pain knees ankles six months worse mornings',
            'medical_entities': ['joint pain', 'morning stiffness', 'chronic pain'],
            'created_at': current_time,
            'processed_at': current_time
        },
        {
            'id': 'mild_1',
            'title': 'Common Cold Symptoms',
            'content': 'Runny nose and mild cough for 2 days, no fever',
            'processed_text': 'runny nose mild cough two days no fever',
            'medical_entities': ['rhinorrhea', 'cough', 'cold symptoms'],
            'created_at': current_time,
            'processed_at': current_time
        }
    ]

@pytest.mark.integration
def test_sentiment_analysis_pipeline(analysis_components, sample_processed_posts):
    """
    Teste l'intégration de l'analyse des sentiments dans le pipeline.
    """
    analyzer = analysis_components['analyzer']
    
    for post in sample_processed_posts:
        # Analyse des sentiments
        sentiment_data = analyzer.analyze_sentiment(post['processed_text'])
        
        # Vérifications de base
        assert 'sentiment_score' in sentiment_data
        assert -1 <= sentiment_data['sentiment_score'] <= 1
        
        # Vérifications spécifiques selon le contenu
        if 'severe' in post['processed_text'] or 'pain' in post['processed_text']:
            assert sentiment_data['sentiment_score'] < 0
        
        if 'mild' in post['processed_text'] and 'no fever' in post['processed_text']:
            assert sentiment_data['sentiment_score'] > -0.5

@pytest.mark.integration
def test_urgency_analysis_pipeline(analysis_components, sample_processed_posts):
    """
    Teste l'intégration de l'analyse d'urgence dans le pipeline.
    """
    analyzer = analysis_components['analyzer']
    
    for post in sample_processed_posts:
        # Analyse d'urgence
        urgency_data = analyzer.calculate_urgency_score(
            post['processed_text'],
            post['medical_entities']
        )
        
        # Vérifications de base
        assert 0 <= urgency_data['urgency_score'] <= 1
        
        # Vérifications spécifiques
        if 'chest pain' in post['medical_entities']:
            assert urgency_data['urgency_score'] >= 0.8
        
        if 'cold symptoms' in post['medical_entities']:
            assert urgency_data['urgency_score'] <= 0.3

@pytest.mark.integration
def test_symptom_extraction_pipeline(analysis_components, sample_processed_posts):
    """
    Teste l'intégration de l'extraction des symptômes dans le pipeline.
    """
    analyzer = analysis_components['analyzer']
    
    for post in sample_processed_posts:
        # Extraction des symptômes
        symptoms_data = analyzer.extract_symptoms(
            post['processed_text'],
            post['medical_entities']
        )
        
        # Vérifications de base
        assert len(symptoms_data['symptoms']) > 0
        
        # Vérifications spécifiques
        if 'chest pain' in post['medical_entities']:
            assert any('chest pain' in symptom.lower() for symptom in symptoms_data['symptoms'])
            assert any('breath' in symptom.lower() for symptom in symptoms_data['symptoms'])
        
        if 'joint pain' in post['medical_entities']:
            assert any('joint' in symptom.lower() for symptom in symptoms_data['symptoms'])
            assert any('pain' in symptom.lower() for symptom in symptoms_data['symptoms'])

@pytest.mark.integration
def test_complete_analysis_pipeline(analysis_components, sample_processed_posts):
    """
    Teste l'intégration complète du pipeline d'analyse.
    """
    analyzer = analysis_components['analyzer']
    
    for post in sample_processed_posts:
        # Analyse complète
        analyzed_data = analyzer.analyze_post(post)
        
        # Vérifications des champs requis
        required_fields = [
            'id', 'urgency_score', 'relevance_score',
            'sentiment_score', 'medical_category',
            'symptoms', 'analysis_timestamp'
        ]
        for field in required_fields:
            assert field in analyzed_data
        
        # Vérification des scores
        assert 0 <= analyzed_data['urgency_score'] <= 1
        assert 0 <= analyzed_data['relevance_score'] <= 1
        assert -1 <= analyzed_data['sentiment_score'] <= 1
        
        # Vérification de la catégorisation
        assert analyzed_data['medical_category'] != ""
        
        # Vérification des symptômes
        assert len(analyzed_data['symptoms']) > 0
        
        # Vérification de la cohérence temporelle
        assert analyzed_data['analysis_timestamp'] >= post['processed_at']

@pytest.mark.integration
def test_categorization_pipeline(analysis_components, sample_processed_posts):
    """
    Teste l'intégration de la catégorisation médicale dans le pipeline.
    """
    analyzer = analysis_components['analyzer']
    
    for post in sample_processed_posts:
        # Catégorisation
        category_data = analyzer.categorize_post(
            post['processed_text'],
            post['medical_entities']
        )
        
        # Vérifications de base
        assert 'medical_category' in category_data
        assert category_data['medical_category'] != ""
        
        # Vérifications spécifiques
        if 'chest pain' in post['medical_entities']:
            assert category_data['medical_category'].lower() in ['cardiology', 'emergency']
        
        if 'joint pain' in post['medical_entities']:
            assert category_data['medical_category'].lower() in ['rheumatology', 'orthopedics']
        
        if 'cold symptoms' in post['medical_entities']:
            assert category_data['medical_category'].lower() in ['general practice', 'ent']

@pytest.mark.integration
def test_analysis_consistency(analysis_components, sample_processed_posts):
    """
    Teste la cohérence des analyses à travers plusieurs exécutions.
    """
    analyzer = analysis_components['analyzer']
    
    for post in sample_processed_posts:
        # Première analyse
        first_analysis = analyzer.analyze_post(post)
        
        # Deuxième analyse
        second_analysis = analyzer.analyze_post(post)
        
        # Vérification de la cohérence
        assert first_analysis['urgency_score'] == second_analysis['urgency_score']
        assert first_analysis['medical_category'] == second_analysis['medical_category']
        assert set(first_analysis['symptoms']) == set(second_analysis['symptoms'])
        assert first_analysis['sentiment_score'] == second_analysis['sentiment_score']

@pytest.mark.integration
def test_error_handling_in_analysis(analysis_components):
    """
    Teste la gestion des erreurs dans le pipeline d'analyse.
    """
    analyzer = analysis_components['analyzer']
    
    # Test avec des données invalides
    invalid_posts = [
        {
            'id': 'invalid_1',
            'processed_text': '',
            'medical_entities': []
        },
        {
            'id': 'invalid_2',
            'processed_text': 'Valid text',
            'medical_entities': None
        },
        {
            'id': 'invalid_3',
            'processed_text': None,
            'medical_entities': ['some entity']
        }
    ]
    
    for post in invalid_posts:
        try:
            analyzed_data = analyzer.analyze_post(post)
            
            # Si l'analyse réussit, vérifier les valeurs par défaut
            assert analyzed_data['urgency_score'] == 0
            assert analyzed_data['relevance_score'] == 0
            assert analyzed_data['sentiment_score'] == 0
            assert analyzed_data['medical_category'] == 'undefined'
            assert len(analyzed_data['symptoms']) == 0
            
        except Exception as e:
            # Si une exception est levée, vérifier qu'elle est explicite
            assert str(e) != "" 