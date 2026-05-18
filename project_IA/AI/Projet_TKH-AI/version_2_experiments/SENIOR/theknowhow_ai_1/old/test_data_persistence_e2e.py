"""
Tests end-to-end pour la persistance des données médicales.
"""

import pytest
import tempfile
from pathlib import Path
import logging
from datetime import datetime, timedelta
import time
import random
import json

from src.core.data_collection.preprocessing.text_processor import TextProcessor
from src.core.data_collection.analysis.medical_analyzer import MedicalAnalyzer
from src.core.data_collection.storage.sqlite_storage import SQLiteStorage

@pytest.fixture
def e2e_pipeline(base_e2e_workspace):
    """Configure le pipeline complet pour les tests e2e."""
    db_path = base_e2e_workspace['databases_dir'] / "medical_e2e_test.db"
    return {
        'processor': TextProcessor(),
        'analyzer': MedicalAnalyzer(),
        'storage': SQLiteStorage(str(db_path))
    }

@pytest.fixture
def sample_medical_data():
    """Génère un ensemble de données médicales réalistes pour les tests."""
    current_time = datetime.now()
    
    # Création d'un ensemble de données varié
    data = []
    for i in range(50):  # Test avec un volume significatif de données
        severity = random.choice(['Mild', 'Moderate', 'Severe'])
        condition = random.choice([
            'Headache', 'Chest Pain', 'Fever', 'Cough',
            'Back Pain', 'Nausea', 'Dizziness', 'Rash'
        ])
        duration = random.randint(1, 30)
        
        post = {
            'id': f'test_{i}',
            'title': f'{severity} {condition}',
            'content': generate_realistic_content(severity, condition, duration),
            'created_at': (current_time - timedelta(days=random.randint(0, 30))).timestamp()
        }
        data.append(post)
    
    return data

def generate_realistic_content(severity, condition, duration):
    """Génère un contenu réaliste pour les posts médicaux."""
    templates = {
        'Mild': [
            "Having a {condition} for {duration} days. It's manageable but annoying.",
            "Experiencing mild {condition}. Started {duration} days ago.",
            "Slight {condition} that comes and goes. Been like this for {duration} days."
        ],
        'Moderate': [
            "Concerned about persistent {condition} for {duration} days. Getting worse.",
            "{condition} is becoming more frequent, lasting {duration} days now.",
            "Moderate {condition} affecting daily activities for {duration} days."
        ],
        'Severe': [
            "URGENT: Severe {condition} for {duration} days. Need immediate advice.",
            "Experiencing intense {condition}. Can't function normally. Day {duration}.",
            "Extremely worried about severe {condition}. {duration} days of agony."
        ]
    }
    
    template = random.choice(templates[severity])
    return template.format(condition=condition.lower(), duration=duration)

@pytest.mark.e2e
def test_complete_data_lifecycle(e2e_pipeline, sample_medical_data):
    """
    Teste le cycle de vie complet des données, du traitement au stockage et à la récupération.
    """
    processor = e2e_pipeline['processor']
    analyzer = e2e_pipeline['analyzer']
    storage = e2e_pipeline['storage']
    
    processed_data = []
    analyzed_data = []
    
    # 1. Traitement et analyse des données
    for post in sample_medical_data:
        # Prétraitement
        processed = processor.process_medical_post(post)
        processed_data.append(processed)
        
        # Analyse
        analyzed = analyzer.analyze_post(processed)
        analyzed_data.append(analyzed)
        
        # Stockage
        storage.save_analyzed_post(analyzed)
        
        # Simulation de latence réaliste
        time.sleep(0.1)
    
    # 2. Vérification du stockage
    stored_posts = storage.get_analyzed_posts()
    assert len(stored_posts) == len(sample_medical_data)
    
    # 3. Vérification des requêtes complexes
    urgent_cases = storage.get_posts_by_urgency_threshold(0.8)
    assert len(urgent_cases) > 0
    
    # 4. Vérification de la cohérence des données
    for original, stored in zip(analyzed_data, stored_posts):
        assert stored['urgency_score'] == original['urgency_score']
        assert stored['medical_category'] == original['medical_category']
        assert set(stored['symptoms']) == set(original['symptoms'])

@pytest.mark.e2e
def test_data_recovery_and_consistency(e2e_pipeline, sample_medical_data):
    """
    Teste la récupération et la cohérence des données après des interruptions simulées.
    """
    processor = e2e_pipeline['processor']
    analyzer = e2e_pipeline['analyzer']
    storage = e2e_pipeline['storage']
    
    # 1. Traitement initial par lots
    batch_size = 10
    for i in range(0, len(sample_medical_data), batch_size):
        batch = sample_medical_data[i:i+batch_size]
        
        for post in batch:
            processed = processor.process_medical_post(post)
            analyzed = analyzer.analyze_post(processed)
            storage.save_analyzed_post(analyzed)
        
        # Simulation d'interruption
        if i == batch_size:
            # Réinitialisation de la connexion
            db_path = storage.db_path
            storage = SQLiteStorage(db_path)
    
    # 2. Vérification après interruption
    stored_posts = storage.get_analyzed_posts()
    assert len(stored_posts) == len(sample_medical_data)
    
    # 3. Vérification de l'intégrité des données
    categories = {post['medical_category'] for post in stored_posts}
    assert len(categories) > 1  # Plusieurs catégories devraient être présentes
    
    # 4. Test de récupération par catégorie
    for category in categories:
        category_posts = storage.get_posts_by_category(category)
        assert len(category_posts) > 0
        assert all(post['medical_category'] == category for post in category_posts)

@pytest.mark.e2e
def test_data_export_and_backup(e2e_pipeline, sample_medical_data, base_e2e_workspace):
    """
    Teste l'exportation et la sauvegarde des données.
    """
    processor = e2e_pipeline['processor']
    analyzer = e2e_pipeline['analyzer']
    storage = e2e_pipeline['storage']
    
    # 1. Traitement et stockage initial
    for post in sample_medical_data[:20]:  # Test avec un sous-ensemble
        processed = processor.process_medical_post(post)
        analyzed = analyzer.analyze_post(processed)
        storage.save_analyzed_post(analyzed)
    
    # 2. Export des données
    export_path = base_e2e_workspace['data_dir'] / "exports" / "medical_data_export.json"
    export_path.parent.mkdir(exist_ok=True)
    
    stored_posts = storage.get_analyzed_posts()
    with open(export_path, 'w') as f:
        json.dump(stored_posts, f, indent=2)
    
    # 3. Vérification de l'export
    with open(export_path, 'r') as f:
        exported_data = json.load(f)
    
    assert len(exported_data) == len(stored_posts)
    
    # 4. Test de restauration
    new_db_path = base_e2e_workspace['databases_dir'] / "medical_restore_test.db"
    restore_storage = SQLiteStorage(str(new_db_path))
    
    for post in exported_data:
        restore_storage.save_analyzed_post(post)
    
    restored_posts = restore_storage.get_analyzed_posts()
    assert len(restored_posts) == len(stored_posts)
    
    # 5. Vérification de la cohérence après restauration
    for original, restored in zip(stored_posts, restored_posts):
        assert restored['id'] == original['id']
        assert restored['urgency_score'] == original['urgency_score']
        assert restored['medical_category'] == original['medical_category']
        assert set(restored['symptoms']) == set(original['symptoms']) 