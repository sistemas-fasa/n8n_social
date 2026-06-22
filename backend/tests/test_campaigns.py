from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_session() -> Generator[Session, None, None]:
        with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_create_and_list_campaigns(client: TestClient) -> None:
    response = client.post(
        "/campaigns",
        json={
            "name": "Mes aniversario",
            "description": "Campania comercial de junio",
            "starts_at": "2026-06-22T10:00:00",
            "ends_at": "2026-06-30T20:00:00",
            "status": "borrador",
        },
    )

    assert response.status_code == 201
    created = response.json()
    assert created["id"] > 0
    assert created["name"] == "Mes aniversario"
    assert created["status"] == "borrador"

    list_response = client.get("/campaigns")

    assert list_response.status_code == 200
    assert [campaign["name"] for campaign in list_response.json()] == ["Mes aniversario"]


def test_get_update_and_cancel_campaign(client: TestClient) -> None:
    created = client.post("/campaigns", json={"name": "Ceramicas"}).json()

    get_response = client.get(f"/campaigns/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Ceramicas"

    update_response = client.put(
        f"/campaigns/{created['id']}",
        json={
            "name": "Ceramicas y porcelanatos",
            "status": "aprobado",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Ceramicas y porcelanatos"
    assert update_response.json()["status"] == "aprobado"

    delete_response = client.delete(f"/campaigns/{created['id']}")
    assert delete_response.status_code == 204

    cancelled = client.get(f"/campaigns/{created['id']}").json()
    assert cancelled["status"] == "cancelado"


def test_campaign_not_found_returns_404(client: TestClient) -> None:
    response = client.get("/campaigns/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Campaign not found"


def test_campaign_rejects_end_date_before_start_date(client: TestClient) -> None:
    response = client.post(
        "/campaigns",
        json={
            "name": "Fechas invalidas",
            "starts_at": "2026-06-30T20:00:00",
            "ends_at": "2026-06-22T10:00:00",
        },
    )

    assert response.status_code == 422
