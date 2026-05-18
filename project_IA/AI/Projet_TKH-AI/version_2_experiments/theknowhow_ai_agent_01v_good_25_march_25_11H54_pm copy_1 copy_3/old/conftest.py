"""
Fixtures communes pour les tests end-to-end.
"""

import pytest
import tempfile
from pathlib import Path
import logging
from datetime import datetime

@pytest.fixture
def e2e_workspace():
    """Crée un espace de travail pour les tests e2e."""
    with tempfile.TemporaryDirectory() as temp_dir:
        workspace = Path(temp_dir)
        (workspace / "data" / "databases").mkdir(parents=True)
        (workspace / "data" / "logs").mkdir(parents=True)
        (workspace / "data" / "raw").mkdir(parents=True)
        (workspace / "data" / "processed").mkdir(parents=True)
        
        paths = {
            'workspace': workspace,
            'databases': workspace / "data" / "databases",
            'logs': workspace / "data" / "logs",
            'raw': workspace / "data" / "raw",
            'processed': workspace / "data" / "processed"
        }
        
        yield paths

@pytest.fixture
def e2e_config():
    """Configuration de base pour les tests e2e."""
    return {
        'processing': {
            'batch_size': 10,
            'min_relevance': 0.5,
            'max_retries': 3,
            'timeout': 60
        },
        'storage': {
            'max_connections': 5,
            'timeout': 30,
            'backup_interval': 3600
        },
        'monitoring': {
            'enabled': True,
            'interval': 300,
            'metrics': ['cpu', 'memory', 'disk', 'network']
        },
        'logging': {
            'level': logging.INFO,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'rotation': '1 day',
            'retention': '1 week'
        }
    }

@pytest.fixture
def e2e_logger(e2e_workspace):
    """Configure le logging pour les tests e2e."""
    def setup_logger(platform: str, test_name: str):
        logger = logging.getLogger(f"e2e_{platform}_{test_name}")
        logger.setLevel(logging.INFO)
        
        # Log file
        log_file = e2e_workspace['logs'] / f"{platform}_{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(file_handler)
        
        # Console output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        )
        logger.addHandler(console_handler)
        
        return logger
    
    return setup_logger

@pytest.fixture
def performance_metrics():
    """Fixture pour collecter les métriques de performance."""
    class Metrics:
        def __init__(self):
            self.start_time = datetime.now()
            self.measurements = []
        
        def add_measurement(self, operation: str, duration: float, success: bool):
            self.measurements.append({
                'operation': operation,
                'duration': duration,
                'success': success,
                'timestamp': datetime.now()
            })
        
        def get_summary(self):
            if not self.measurements:
                return {}
            
            total_duration = sum(m['duration'] for m in self.measurements)
            success_rate = sum(1 for m in self.measurements if m['success']) / len(self.measurements)
            
            return {
                'total_duration': total_duration,
                'success_rate': success_rate,
                'operation_count': len(self.measurements),
                'start_time': self.start_time,
                'end_time': datetime.now()
            }
    
    return Metrics() 