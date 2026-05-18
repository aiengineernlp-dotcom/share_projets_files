"""Tests pour le module de monitoring."""

import pytest
import time
from datetime import datetime, timedelta
from monitoring import MonitoringManager, APIMetrics, SystemMetrics

@pytest.fixture
def monitoring_manager():
    """Fixture pour créer une instance de MonitoringManager."""
    return MonitoringManager()

def test_api_metrics_initialization(monitoring_manager):
    """Test l'initialisation des métriques API."""
    assert monitoring_manager.api_metrics.total_requests == 0
    assert monitoring_manager.api_metrics.successful_requests == 0
    assert monitoring_manager.api_metrics.failed_requests == 0
    assert monitoring_manager.api_metrics.total_tokens == 0
    assert monitoring_manager.api_metrics.average_response_time == 0.0
    assert monitoring_manager.api_metrics.last_request_time is None

def test_system_metrics_initialization(monitoring_manager):
    """Test l'initialisation des métriques système."""
    assert isinstance(monitoring_manager.system_metrics.cpu_percent, float)
    assert isinstance(monitoring_manager.system_metrics.memory_percent, float)
    assert isinstance(monitoring_manager.system_metrics.disk_usage_percent, float)
    assert isinstance(monitoring_manager.system_metrics.timestamp, datetime)

def test_record_api_request(monitoring_manager):
    """Test l'enregistrement des requêtes API."""
    # Test d'une requête réussie
    monitoring_manager.record_api_request(True, 100, 0.5)
    assert monitoring_manager.api_metrics.total_requests == 1
    assert monitoring_manager.api_metrics.successful_requests == 1
    assert monitoring_manager.api_metrics.failed_requests == 0
    assert monitoring_manager.api_metrics.total_tokens == 100
    assert monitoring_manager.api_metrics.average_response_time == 0.5
    
    # Test d'une requête échouée
    monitoring_manager.record_api_request(False, 50, 0.3)
    assert monitoring_manager.api_metrics.total_requests == 2
    assert monitoring_manager.api_metrics.successful_requests == 1
    assert monitoring_manager.api_metrics.failed_requests == 1
    assert monitoring_manager.api_metrics.total_tokens == 150
    assert monitoring_manager.api_metrics.average_response_time == 0.4

def test_record_error(monitoring_manager):
    """Test l'enregistrement des erreurs."""
    monitoring_manager.record_error("TestError")
    assert monitoring_manager.error_counts["TestError"] == 1
    
    monitoring_manager.record_error("TestError")
    assert monitoring_manager.error_counts["TestError"] == 2

def test_update_system_metrics(monitoring_manager):
    """Test la mise à jour des métriques système."""
    monitoring_manager.update_system_metrics()
    assert 0 <= monitoring_manager.system_metrics.cpu_percent <= 100
    assert 0 <= monitoring_manager.system_metrics.memory_percent <= 100
    assert 0 <= monitoring_manager.system_metrics.disk_usage_percent <= 100
    assert isinstance(monitoring_manager.system_metrics.timestamp, datetime)

def test_get_uptime(monitoring_manager):
    """Test le calcul du temps de fonctionnement."""
    # Simuler un temps de fonctionnement
    monitoring_manager.start_time = datetime.now() - timedelta(hours=2)
    uptime = monitoring_manager.get_uptime()
    assert 1.9 <= uptime <= 2.1  # Permettre une marge d'erreur de 0.1 heure

def test_get_metrics_summary(monitoring_manager):
    """Test la génération du résumé des métriques."""
    # Enregistrer quelques métriques
    monitoring_manager.record_api_request(True, 100, 0.5)
    monitoring_manager.record_error("TestError")
    monitoring_manager.update_system_metrics()
    
    summary = monitoring_manager.get_metrics_summary()
    
    # Vérifier la structure du résumé
    assert "api_metrics" in summary
    assert "system_metrics" in summary
    assert "error_counts" in summary
    assert "uptime_hours" in summary
    
    # Vérifier les valeurs
    assert summary["api_metrics"]["total_requests"] == 1
    assert summary["api_metrics"]["success_rate"] == 100.0
    assert summary["api_metrics"]["total_tokens"] == 100
    assert summary["api_metrics"]["average_response_time"] == 0.5
    assert summary["error_counts"]["TestError"] == 1
    assert isinstance(summary["uptime_hours"], float) 