import pytest
from app.views import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    resp = client.get('/')
    assert resp.status_code == 200
    html = resp.data.decode(errors='ignore')
    assert 'Unit Converter' in html

def test_length_convert(client):
    resp = client.post('/length', data={'value': '1', 'from': 'm', 'to': 'cm'})
    assert resp.status_code == 200
    assert b'100' in resp.data

def test_weight_convert(client):
    resp = client.post('/weight', data={'value': '1', 'from': 'kg', 'to': 'g'})
    assert resp.status_code == 200
    assert b'1000' in resp.data

def test_temperature_convert(client):
    resp = client.post('/temperature', data={'value': '0', 'from': 'C', 'to': 'F'})
    assert resp.status_code == 200
    assert b'32' in resp.data

def test_length_invalid_unit(client):
    resp = client.post('/length', data={'value': '1', 'from': 'm', 'to': 'invalid'})
    assert resp.status_code == 200
    assert b'Error' in resp.data

def test_weight_invalid_value(client):
    resp = client.post('/weight', data={'value': 'abc', 'from': 'kg', 'to': 'g'})
    assert resp.status_code == 200
    assert b'Error' in resp.data
