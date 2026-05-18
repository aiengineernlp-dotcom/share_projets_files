"""
Tests unitaires pour le module d'analyse médicale.
"""

import pytest
from src.core.data_collection.analysis.medical_analyzer import MedicalAnalyzer
from unittest.mock import Mock, patch
from datetime import datetime

@pytest.fixture
def analyzer():
    """Fixture pour créer une instance de MedicalAnalyzer."""
    return MedicalAnalyzer()

@pytest.fixture
def sample_processed_data():
    """Fixture pour créer des données prétraitées de test."""
    return {
        'processed_title': "severe chest pain and difficulty breathing",
        'processed_content': "experiencing severe chest pain and difficulty breathing since 2 hours",
        'medical_entities': {
            'title': [
                {'text': 'chest pain', 'label': 'SYMPTOM', 'start': 7, 'end': 17},
                {'text': 'difficulty breathing', 'label': 'SYMPTOM', 'start': 22, 'end': 40}
            ],
            'content': [
                {'text': 'chest pain', 'label': 'SYMPTOM', 'start': 17, 'end': 27},
                {'text': 'difficulty breathing', 'label': 'SYMPTOM', 'start': 32, 'end': 50}
            ]
        },
        'preprocessing_metadata': {
            'num_entities': 4,
            'num_tokens': 12
        },
        'score': 15,
        'num_comments': 8
    }

@pytest.fixture
def medical_analyzer():
    """Instance de l'analyseur médical pour les tests."""
    return MedicalAnalyzer()

@pytest.fixture
def sample_processed_post():
    """Exemple de post traité pour les tests."""
    return {
        'id': 'test_1',
        'title': 'Severe chest pain and difficulty breathing',
        'content': 'Patient experiencing acute chest pain with shortness of breath for the last 2 hours.',
        'medical_entities': ['chest pain', 'shortness of breath', 'acute'],
        'processed_text': 'Patient experiencing acute chest pain with shortness of breath',
        'created_at': datetime.now().timestamp()
    }

def test_analyze_sentiment(analyzer, sample_processed_data):
    """Teste l'analyse de sentiment."""
    sentiment = analyzer._analyze_sentiment(
        sample_processed_data['processed_title'],
        sample_processed_data['processed_content']
    )
    
    # Vérifie la structure du résultat
    assert isinstance(sentiment, dict)
    assert all(k in sentiment for k in ['polarity', 'subjectivity', 'compound'])
    assert all(isinstance(v, float) for v in sentiment.values())
    
    # Vérifie les plages de valeurs
    assert -1 <= sentiment['polarity'] <= 1
    assert 0 <= sentiment['subjectivity'] <= 1
    assert 0 <= sentiment['compound'] <= 2  # (polarity + 1) * (1 - subjectivity)

def test_calculate_urgency_score(analyzer, sample_processed_data):
    """Teste le calcul du score d'urgence."""
    score = analyzer._calculate_urgency_score(
        sample_processed_data['processed_title'],
        sample_processed_data['processed_content'],
        sample_processed_data['medical_entities']
    )
    
    # Vérifie le type et la plage
    assert isinstance(score, float)
    assert 0 <= score <= 1
    
    # Vérifie que les mots-clés d'urgence sont pris en compte
    assert score > 0.5  # Le texte contient "severe" et des symptômes graves

def test_calculate_relevance_score(analyzer, sample_processed_data):
    """Teste le calcul du score de pertinence."""
    score = analyzer._calculate_relevance_score(sample_processed_data)
    
    # Vérifie le type et la plage
    assert isinstance(score, float)
    assert 0 <= score <= 1
    
    # Crée des données avec un engagement plus faible
    low_engagement_data = sample_processed_data.copy()
    low_engagement_data['score'] = 1
    low_engagement_data['num_comments'] = 0
    low_score = analyzer._calculate_relevance_score(low_engagement_data)
    
    # Vérifie que l'engagement influence le score
    assert score > low_score

def test_extract_main_symptoms(analyzer, sample_processed_data):
    """Teste l'extraction des symptômes principaux."""
    symptoms = analyzer._extract_main_symptoms(sample_processed_data['medical_entities'])
    
    # Vérifie le type de retour
    assert isinstance(symptoms, list)
    assert all(isinstance(s, str) for s in symptoms)
    
    # Vérifie les symptômes extraits
    assert 'chest pain' in symptoms
    assert 'difficulty breathing' in symptoms
    
    # Vérifie l'unicité des symptômes
    assert len(symptoms) == len(set(symptoms))

def test_categorize_post(analyzer, sample_processed_data):
    """Teste la catégorisation des posts."""
    category = analyzer._categorize_post(sample_processed_data)
    
    # Vérifie le type de retour
    assert isinstance(category, str)
    
    # Vérifie la catégorisation
    assert category == 'cardiology'  # En raison de "chest pain"
    
    # Test avec un post neurologique
    neuro_data = sample_processed_data.copy()
    neuro_data['processed_title'] = "severe headache and migraine"
    neuro_data['processed_content'] = "experiencing severe headache and migraine"
    assert analyzer._categorize_post(neuro_data) == 'neurology'
    
    # Test avec un post général
    general_data = sample_processed_data.copy()
    general_data['processed_title'] = "general health question"
    general_data['processed_content'] = "question about health"
    assert analyzer._categorize_post(general_data) == 'general'

def test_analyze_post(analyzer, sample_processed_data):
    """Teste l'analyse complète d'un post."""
    analyzed = analyzer.analyze_post(sample_processed_data)
    
    # Vérifie la structure du résultat
    assert isinstance(analyzed, dict)
    assert all(k in analyzed for k in [
        'sentiment',
        'urgency_score',
        'relevance_score',
        'symptoms',
        'medical_category',
        'analysis_metadata'
    ])
    
    # Vérifie les métadonnées d'analyse
    metadata = analyzed['analysis_metadata']
    assert isinstance(metadata, dict)
    assert all(k in metadata for k in ['analyzed_at', 'version', 'scores'])
    assert all(k in metadata['scores'] for k in ['urgency', 'relevance', 'sentiment'])
    
    # Vérifie la cohérence des scores
    assert 0 <= analyzed['urgency_score'] <= 1
    assert 0 <= analyzed['relevance_score'] <= 1
    assert isinstance(analyzed['medical_category'], str)

class TestMedicalAnalyzer:
    """Tests pour la classe MedicalAnalyzer."""

    def test_init(self):
        """Teste l'initialisation de l'analyseur."""
        analyzer = MedicalAnalyzer()
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_post')

    def test_analyze_post_basic(self, medical_analyzer, sample_processed_post):
        """Teste l'analyse basique d'un post."""
        result = medical_analyzer.analyze_post(sample_processed_post)
        
        assert 'urgency_score' in result
        assert 'relevance_score' in result
        assert 'medical_category' in result
        assert 'symptoms' in result
        
        assert 0 <= result['urgency_score'] <= 1
        assert 0 <= result['relevance_score'] <= 1
        assert isinstance(result['symptoms'], list)
        assert len(result['symptoms']) > 0

    def test_urgency_detection(self, medical_analyzer):
        """Teste la détection de l'urgence dans différents scénarios."""
        urgent_post = {
            'title': 'URGENT: Severe chest pain',
            'content': 'Experiencing intense chest pain and difficulty breathing',
            'medical_entities': ['severe chest pain', 'difficulty breathing'],
            'processed_text': 'Urgent severe chest pain difficulty breathing'
        }
        
        non_urgent_post = {
            'title': 'Minor rash on arm',
            'content': 'Small rash appeared yesterday, no pain or itching',
            'medical_entities': ['rash', 'arm'],
            'processed_text': 'Minor rash arm no pain itching'
        }
        
        urgent_result = medical_analyzer.analyze_post(urgent_post)
        non_urgent_result = medical_analyzer.analyze_post(non_urgent_post)
        
        assert urgent_result['urgency_score'] > non_urgent_result['urgency_score']
        assert urgent_result['urgency_score'] > 0.7  # Seuil d'urgence élevée

    def test_medical_categorization(self, medical_analyzer):
        """Teste la catégorisation médicale des posts."""
        test_cases = [
            {
                'post': {
                    'title': 'Heart problems',
                    'content': 'Experiencing chest pain and irregular heartbeat',
                    'medical_entities': ['chest pain', 'irregular heartbeat'],
                    'processed_text': 'Heart problems chest pain irregular heartbeat'
                },
                'expected_category': 'cardiology'
            },
            {
                'post': {
                    'title': 'Skin issue',
                    'content': 'Severe rash and itching all over body',
                    'medical_entities': ['rash', 'itching'],
                    'processed_text': 'Skin issue rash itching body'
                },
                'expected_category': 'dermatology'
            }
        ]
        
        for case in test_cases:
            result = medical_analyzer.analyze_post(case['post'])
            assert result['medical_category'] == case['expected_category']

    def test_symptom_extraction(self, medical_analyzer):
        """Teste l'extraction des symptômes."""
        post = {
            'title': 'Multiple symptoms',
            'content': 'Experiencing fever, headache, and nausea since yesterday',
            'medical_entities': ['fever', 'headache', 'nausea'],
            'processed_text': 'Multiple symptoms fever headache nausea yesterday'
        }
        
        result = medical_analyzer.analyze_post(post)
        
        assert 'fever' in result['symptoms']
        assert 'headache' in result['symptoms']
        assert 'nausea' in result['symptoms']

    def test_relevance_scoring(self, medical_analyzer):
        """Teste le calcul du score de pertinence."""
        relevant_post = {
            'title': 'Medical Emergency',
            'content': 'High fever 40°C, severe headache, and confusion',
            'medical_entities': ['high fever', 'severe headache', 'confusion'],
            'processed_text': 'Medical emergency high fever severe headache confusion'
        }
        
        irrelevant_post = {
            'title': 'General Question',
            'content': 'Looking for a good doctor in my area',
            'medical_entities': ['doctor'],
            'processed_text': 'Looking good doctor area'
        }
        
        relevant_result = medical_analyzer.analyze_post(relevant_post)
        irrelevant_result = medical_analyzer.analyze_post(irrelevant_post)
        
        assert relevant_result['relevance_score'] > irrelevant_result['relevance_score']
        assert relevant_result['relevance_score'] > 0.7  # Seuil de pertinence élevée

    def test_error_handling(self, medical_analyzer):
        """Teste la gestion des erreurs."""
        invalid_post = {
            'title': 'Test'
            # Champs manquants intentionnellement
        }
        
        with pytest.raises(KeyError):
            medical_analyzer.analyze_post(invalid_post)

    def test_empty_content(self, medical_analyzer):
        """Teste le comportement avec un contenu vide."""
        empty_post = {
            'title': '',
            'content': '',
            'medical_entities': [],
            'processed_text': ''
        }
        
        result = medical_analyzer.analyze_post(empty_post)
        
        assert result['urgency_score'] == 0
        assert result['relevance_score'] == 0
        assert len(result['symptoms']) == 0 