"""
Basic tests for CycloneOPS PRO
Run with: pytest tests/ -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfig:
    """Test configuration loading"""
    def test_config_import(self):
        from core.config import Config
        assert Config.SECRET_KEY is not None
        assert Config.INPUT_SIZE == 6
        assert len(Config.CATEGORIES) == 6


class TestDataset:
    """Test dataset loading and cleaning"""
    def test_import_dataset(self):
        from core.dataset import load_raw, clean
        assert callable(load_raw)
        assert callable(clean)


class TestModel:
    """Test model initialization"""
    def test_model_import(self):
        from core.model import get_model
        assert callable(get_model)


class TestApp:
    """Test Flask app basic routes"""
    def test_app_import(self):
        from app.main import app
        assert app is not None
    
    def test_login_route(self):
        from app.main import app
        client = app.test_client()
        response = client.get('/login')
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
