# Test utilities and fixtures
import pytest


@pytest.fixture
def app():
    """Fixture for Flask app testing"""
    from app.main import app as flask_app
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    """Fixture for Flask test client"""
    return app.test_client()
