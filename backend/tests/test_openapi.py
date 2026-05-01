from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi_schema_accessible() -> None:
    """OpenAPI schema endpoint should return 200."""
    response = client.get("/openapi.json")
    assert response.status_code == 200


def test_health_route_registered() -> None:
    """Health route should appear in the OpenAPI schema paths."""
    schema = client.get("/openapi.json").json()
    assert "/api/v1/health" in schema["paths"]
