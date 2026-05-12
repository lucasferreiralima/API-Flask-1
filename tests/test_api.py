import json

def test_ping(client):
    response = client.get('/api/ping')
    data = json.loads(response.data.decode('utf-8'))
    assert response.status_code == 200
    assert data['message'] == 'pong'

def test_health_check(client):
    response = client.get('/api/health')
    data = json.loads(response.data.decode('utf-8'))
    # In testing, if DATABASE_URL is not set, it uses in-memory sqlite
    assert response.status_code == 200
    assert data['status'] == 'up'
    assert data['database'] == 'ok'

def test_404(client):
    response = client.get('/api/non-existent')
    data = json.loads(response.data.decode('utf-8'))
    assert response.status_code == 404
    assert data['code'] == 404
    assert 'Not Found' in data['name']
