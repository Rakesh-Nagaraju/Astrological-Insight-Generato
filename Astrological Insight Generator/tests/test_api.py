"""
Tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.api import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestZodiacEndpoint:
    """Test zodiac calculation endpoint."""
    
    def test_get_zodiac_valid_date(self, client):
        """Test getting zodiac for valid date."""
        response = client.get("/zodiac/1995-08-20")
        assert response.status_code == 200
        data = response.json()
        assert data["zodiac"] == "Leo"
        assert data["birth_date"] == "1995-08-20"
    
    def test_get_zodiac_invalid_date(self, client):
        """Test getting zodiac for invalid date."""
        response = client.get("/zodiac/invalid-date")
        assert response.status_code == 400
    
    def test_get_zodiac_all_signs(self, client):
        """Test zodiac endpoint for all signs."""
        test_cases = [
            ("2000-01-20", "Aquarius"),
            ("2000-03-21", "Aries"),
            ("2000-07-23", "Leo"),
            ("2000-12-22", "Capricorn"),
        ]
        
        for date_str, expected_sign in test_cases:
            response = client.get(f"/zodiac/{date_str}")
            assert response.status_code == 200
            assert response.json()["zodiac"] == expected_sign


class TestPredictEndpoint:
    """Test prediction endpoint."""
    
    def test_predict_valid_input(self, client):
        """Test prediction with valid input."""
        payload = {
            "name": "Ritika",
            "birth_date": "1995-08-20",
            "birth_time": "14:30",
            "birth_place": "Jaipur, India",
            "language": "en"
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "zodiac" in data
        assert "insight" in data
        assert "language" in data
        assert data["zodiac"] == "Leo"
        assert data["language"] == "en"
        assert len(data["insight"]) > 0
    
    def test_predict_invalid_date(self, client):
        """Test prediction with invalid date."""
        payload = {
            "name": "Test",
            "birth_date": "invalid-date",
            "birth_time": "14:30",
            "birth_place": "Test",
            "language": "en"
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 400
    
    def test_predict_invalid_time(self, client):
        """Test prediction with invalid time."""
        payload = {
            "name": "Test",
            "birth_date": "1995-08-20",
            "birth_time": "invalid-time",
            "birth_place": "Test",
            "language": "en"
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 400
    
    def test_predict_invalid_language(self, client):
        """Test prediction with invalid language."""
        payload = {
            "name": "Test",
            "birth_date": "1995-08-20",
            "birth_time": "14:30",
            "birth_place": "Test",
            "language": "fr"  # Invalid
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 400
    
    def test_predict_missing_fields(self, client):
        """Test prediction with missing required fields."""
        payload = {
            "name": "Test",
            "birth_date": "1995-08-20"
            # Missing required fields
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_predict_hindi_language(self, client):
        """Test prediction with Hindi language."""
        payload = {
            "name": "Ritika",
            "birth_date": "1995-08-20",
            "birth_time": "14:30",
            "birth_place": "Jaipur, India",
            "language": "hi"
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "hi"
    
    def test_predict_all_zodiac_signs(self, client):
        """Test prediction for all zodiac signs."""
        test_dates = [
            ("2000-01-20", "Aquarius"),
            ("2000-03-21", "Aries"),
            ("2000-07-23", "Leo"),
            ("2000-12-22", "Capricorn"),
        ]
        
        for date_str, expected_sign in test_dates:
            payload = {
                "name": "Test",
                "birth_date": date_str,
                "birth_time": "12:00",
                "birth_place": "Test",
                "language": "en"
            }
            response = client.post("/predict", json=payload)
            assert response.status_code == 200
            assert response.json()["zodiac"] == expected_sign


class TestInsightEndpoint:
    """Test CLI-friendly insight endpoint."""
    
    def test_insight_get_endpoint(self, client):
        """Test GET insight endpoint."""
        response = client.get(
            "/insight",
            params={
                "name": "Ritika",
                "birth_date": "1995-08-20",
                "birth_time": "14:30",
                "birth_place": "Jaipur, India",
                "language": "en"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "zodiac" in data
        assert "insight" in data
        assert data["zodiac"] == "Leo"
    
    def test_insight_missing_params(self, client):
        """Test insight endpoint with missing parameters."""
        response = client.get("/insight", params={"name": "Test"})
        assert response.status_code == 422  # Validation error

