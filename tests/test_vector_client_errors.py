import sys
import pytest
import httpx

# Add service path so we can import vector_client despite hyphenated parent directories pattern
sys.path.insert(0, 'services/document-processing')

from vector_client import VectorDBClient  # type: ignore
from config import settings  # type: ignore


@pytest.mark.asyncio
async def test_vector_client_disabled(monkeypatch):
    original = settings.enable_vector_db
    settings.enable_vector_db = False

    client = VectorDBClient(base_url="http://invalid", timeout=0.1)

    # If disabled, should short-circuit and return None without attempting HTTP
    result = await client.process_document(1, full_text="text", sections=None)
    assert result is None

    search_result = await client.search("query")
    assert search_result is None

    settings.enable_vector_db = original


class FakeTimeoutClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):  # simulate timeout on post
        raise httpx.TimeoutException("simulated timeout")

    async def get(self, *args, **kwargs):
        raise httpx.TimeoutException("simulated timeout")


@pytest.mark.asyncio
async def test_vector_client_timeout(monkeypatch):
    # Ensure enabled
    settings.enable_vector_db = True

    monkeypatch.setattr(httpx, "AsyncClient", FakeTimeoutClient)

    client = VectorDBClient(base_url="http://localhost:8002", timeout=0.01)

    result = await client.process_document(1, full_text="text", sections=None)
    assert result is None, "Timeout should be swallowed and None returned"

    search_result = await client.search("query")
    assert search_result is None, "Search timeout should return None"


@pytest.mark.asyncio
async def test_vector_client_health_timeout(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", FakeTimeoutClient)
    client = VectorDBClient(base_url="http://localhost:8002")
    healthy = await client.health_check()
    assert healthy is False
