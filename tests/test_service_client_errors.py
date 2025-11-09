import sys
import pytest
import httpx

sys.path.insert(0, 'services/api-gateway')
from service_client import ServiceClient  # type: ignore
from config import settings  # type: ignore


class FakeErrorClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        raise httpx.HTTPError("simulated post error")

    async def get(self, *args, **kwargs):
        # Simulate non-200 response for get_document style functions
        class R:
            status_code = 500
            def json(self):
                return {"error": "failure"}
        return R()

    async def delete(self, *args, **kwargs):
        class R:
            status_code = 500
        return R()


@pytest.mark.asyncio
async def test_service_client_upload_error(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", FakeErrorClient)
    client = ServiceClient()
    with pytest.raises(Exception):
        await client.upload_document(b"%PDF-1.4", "sample.pdf")


@pytest.mark.asyncio
async def test_service_client_get_document_failure(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", FakeErrorClient)
    client = ServiceClient()
    doc = await client.get_document(999)
    assert doc is None


@pytest.mark.asyncio
async def test_service_client_delete_document_failure(monkeypatch):
    monkeypatch.setattr(httpx, "AsyncClient", FakeErrorClient)
    client = ServiceClient()
    success = await client.delete_document(999)
    assert success is False
