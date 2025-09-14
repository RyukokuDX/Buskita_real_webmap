import pytest
from buskita import create_app

@pytest.fixture
def app():
    app = create_app(init_background_thread=False)
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_route(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Ryukoku Bus Navi" in response.data

def test_timetable_route(client):
    """Test that the timetable page loads correctly."""
    response = client.get('/timetable')
    assert response.status_code == 200
    assert b"Timetable" in response.data
