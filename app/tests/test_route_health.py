import pytest

def test_health_endpoint_success(client):
    response =client.get('/health')
    assert response.status_code==200
    assert response.get_json()== {"status": "healthy"}


def test_health_endpoint_invalid_method(client):
    response=client.post('/health')
    assert response.status_code== 405
