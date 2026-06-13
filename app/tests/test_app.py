from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data
    assert "hostname" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "system" in data
    assert "app" in data
    assert "cpu_utilization_percent" in data["system"]
    assert "memory" in data["system"]
    assert "uptime_seconds" in data["app"]

def test_secure_data():
    response = client.get("/api/v1/secure-data")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]) == 2
    assert data["compliance"]["encryption_in_transit"] == "TLSv1.3"
