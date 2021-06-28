import pytest

from api import app


@pytest.fixture
def client():
    yield app.test_client()
