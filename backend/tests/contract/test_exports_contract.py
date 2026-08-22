import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from src.main import app


@pytest.mark.asyncio
async def test_endpoints_exportacion_son_publicos_y_validan_formato():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        inexistente = uuid.uuid4()
        for resource in ("standings", "matches"):
            response = await client.get(f"/api/v1/leagues/{inexistente}/{resource}/export")
            assert response.status_code == 404
            assert response.json()["error"]["code"] == "league_not_found"
            invalid = await client.get(
                f"/api/v1/leagues/{inexistente}/{resource}/export?format=pdf"
            )
            assert invalid.status_code == 400
            assert invalid.json()["error"]["code"] == "validation_error"


def test_openapi_declara_descargas_csv():
    schema = app.openapi()
    for path in (
        "/api/v1/leagues/{league_id}/standings/export",
        "/api/v1/leagues/{league_id}/matches/export",
    ):
        operation = schema["paths"][path]["get"]
        assert "200" in operation["responses"]
        assert operation.get("security") in (None, [])
