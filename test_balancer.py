import pytest
from balancer import loadbalancer

LOAD_BALANCER_IP = '10.0.0.4:5000'
url = f'http://{LOAD_BALANCER_IP}'

@pytest.fixture
def client():
    with loadbalancer.test_client() as client:
            yield client

def test_host_routing_service1(client):
      result = client.get(f'{url}/service1')
      assert b'Server1' in result.data
      result = client.get(f'{url}/service1')
      assert b'Server2' in result.data
      result = client.get(f'{url}/service1')
      assert b'Server2' in result.data
      result = client.get(f'{url}/service1')
      assert b'Server1' in result.data
 

def test_host_routing_service1_multiple(client):
      result = client.get('/', headers={'Host': 'www.apple.com'})
      assert result.status_code == 404

def test_routing_not_found(client):
      result = client.get(f'{url}/service1')
      assert b'Server2' in result.data
 

def test_try_access_server_directly(client):
      result = client.get('http://10.0.0.5:5000')
      assert result.status_code == 404
