import pytest
from balancer import loadbalancer

@pytest.fixture
def client():
    with loadbalancer.test_client() as client:
            yield client

def test_hello(client):
      result = client.get('/')
      assert b'hello' in result.data

def test_host_routing_mango(client):
      result = client.get('/', headers={'Host': 'www.mango.com'})
      assert b'This is the mango application.' in result.data

def test_host_routing_apple(client):
      result = client.get('/', headers={'Host': 'www.apple.com'})
      assert b'This is the apple application' in result.data

def test_routing_not_found(client):
      result = client.get('/', headers={'Host': 'notmango.com'})
      assert b'Not Found' in result.data
      assert result.status_code == 404

