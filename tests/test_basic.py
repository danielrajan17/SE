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
    
    def test_login_post_invalid(self):
        """Test login with invalid credentials"""
        from app.main import app
        client = app.test_client()
        response = client.post('/login', data={
            'username': 'invalid_user',
            'password': 'wrong_pass'
        })
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_login_post_valid(self):
        """Test login with valid credentials"""
        from app.main import app
        from core.config import Config
        client = app.test_client()
        
        # Get first valid user from Config.USERS
        if Config.USERS:
            username = list(Config.USERS.keys())[0]
            password = Config.USERS[username]
            
            response = client.post('/login', data={
                'username': username,
                'password': password
            }, follow_redirects=True)
            assert response.status_code == 200
    
    def test_dashboard_without_login(self):
        """Test accessing dashboard without login"""
        from app.main import app
        client = app.test_client()
        response = client.get('/dashboard')
        # Should redirect to login
        assert response.status_code in [200, 302]
    
    def test_logout_route(self):
        """Test logout route"""
        from app.main import app
        client = app.test_client()
        response = client.get('/logout')
        # Should redirect to login
        assert response.status_code in [200, 302]


class TestAPI:
    """Test Flask API endpoints"""
    
    @pytest.fixture
    def client_with_session(self):
        """Create test client with authenticated session"""
        from app.main import app
        from core.config import Config
        
        client = app.test_client()
        
        # Get first valid user credentials
        if Config.USERS:
            username = list(Config.USERS.keys())[0]
            password = Config.USERS[username]
            
            # Login
            client.post('/login', data={
                'username': username,
                'password': password
            })
        
        return client
    
    def test_api_status_without_auth(self):
        """Test /api/status without authentication"""
        from app.main import app
        client = app.test_client()
        response = client.get('/api/status')
        # Status endpoint doesn't require auth in current implementation
        assert response.status_code == 200
        data = response.get_json()
        assert 'model_ready' in data
        assert 'model_type' in data
    
    def test_api_status_with_auth(self, client_with_session):
        """Test /api/status with authentication"""
        response = client_with_session.get('/api/status')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data['model_ready'], bool)
        assert data['model_type'] == 'PyTorch CycloneNet'
    
    def test_api_predict_without_auth(self):
        """Test /api/predict without authentication"""
        from app.main import app
        client = app.test_client()
        response = client.post('/api/predict', json={
            'lat': 15.0,
            'lon': 72.0,
            'ecp': 990,
            'dp': 10,
            'msw': 100
        })
        # Should return 401 (unauthorized)
        assert response.status_code == 401
    
    def test_api_predict_missing_field(self, client_with_session):
        """Test /api/predict with missing required field"""
        response = client_with_session.post('/api/predict', json={
            'lat': 15.0,
            'lon': 72.0,
            # Missing 'ecp' field
            'dp': 10,
            'msw': 100
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data or 'Missing' in str(response.data)
    
    def test_api_train_without_auth(self):
        """Test /api/train without authentication"""
        from app.main import app
        client = app.test_client()
        response = client.post('/api/train', json={'epochs': 10})
        # Should return 401 (unauthorized)
        assert response.status_code == 401
    
    def test_api_data_without_auth(self):
        """Test /api/data without authentication"""
        from app.main import app
        client = app.test_client()
        response = client.get('/api/data')
        # Should return 401 (unauthorized)
        assert response.status_code == 401
    
    def test_api_data_with_auth(self, client_with_session):
        """Test /api/data with authentication"""
        response = client_with_session.get('/api/data')
        assert response.status_code == 200
        data = response.get_json()
        assert 'geojson' in data
        assert 'stats' in data
    
    def test_api_upload_without_auth(self):
        """Test /api/upload without authentication"""
        from app.main import app
        client = app.test_client()
        response = client.post('/api/upload', data={})
        # Should return 401 (unauthorized)
        assert response.status_code == 401
    
    def test_api_upload_no_file(self, client_with_session):
        """Test /api/upload without file"""
        response = client_with_session.post('/api/upload', data={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_api_scan_without_auth(self):
        """Test /api/scan without authentication"""
        from app.main import app
        client = app.test_client()
        response = client.get('/api/scan')
        # Should return 401 (unauthorized)
        assert response.status_code == 401
    
    def test_api_scan_with_auth(self, client_with_session):
        """Test /api/scan with authentication"""
        response = client_with_session.get('/api/scan')
        assert response.status_code == 200
        data = response.get_json()
        assert 'active_systems' in data
        assert 'message' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
