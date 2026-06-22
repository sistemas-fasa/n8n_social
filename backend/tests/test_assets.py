from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.main import app
from app.models.social import SocialAsset


@pytest.fixture()
def asset_client(tmp_path: Path) -> Generator[tuple[TestClient, Session], None, None]:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.db import Base

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    def override_get_session() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = override_get_session
    app.state.asset_storage_path = tmp_path / "assets"
    app.state.asset_public_base_url = "http://testserver/public/assets"
    app.state.asset_max_size_bytes = 1024
    app.state.asset_public_url_verifier = lambda public_url: True

    try:
        yield TestClient(app), session
    finally:
        app.dependency_overrides.clear()
        for attr in (
            "asset_storage_backend",
            "asset_storage_path",
            "asset_public_base_url",
            "asset_max_size_bytes",
            "asset_public_url_verifier",
        ):
            if hasattr(app.state, attr):
                delattr(app.state, attr)
        session.close()


def test_upload_image_returns_asset_id_and_public_url(asset_client: tuple[TestClient, Session]) -> None:
    client, _ = asset_client

    response = client.post(
        "/assets/upload",
        files={"file": ("test-image.jpg", b"fake image bytes", "image/jpeg")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["asset_id"] > 0
    assert payload["public_url"].startswith("http://testserver/public/assets/")
    assert payload["file_name"].endswith(".jpg")
    assert payload["mime_type"] == "image/jpeg"
    assert payload["size_bytes"] == len(b"fake image bytes")


def test_upload_image_creates_social_asset_record(asset_client: tuple[TestClient, Session]) -> None:
    client, session = asset_client

    response = client.post(
        "/assets/upload",
        files={"file": ("pieza.png", b"png bytes", "image/png")},
    )

    assert response.status_code == 201
    asset = session.scalar(select(SocialAsset))
    assert asset is not None
    assert asset.id == response.json()["asset_id"]
    assert asset.public_url == response.json()["public_url"]
    assert asset.mime_type == "image/png"
    assert asset.size_bytes == len(b"png bytes")


def test_upload_rejects_unsupported_mime_type(asset_client: tuple[TestClient, Session]) -> None:
    client, _ = asset_client

    response = client.post(
        "/assets/upload",
        files={"file": ("payload.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported asset MIME type"


def test_upload_rejects_empty_file(asset_client: tuple[TestClient, Session]) -> None:
    client, _ = asset_client

    response = client.post(
        "/assets/upload",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded asset is empty"


def test_upload_rejects_file_over_configured_size(asset_client: tuple[TestClient, Session]) -> None:
    client, _ = asset_client

    response = client.post(
        "/assets/upload",
        files={"file": ("large.mp4", b"x" * 1025, "video/mp4")},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Uploaded asset is too large"


def test_upload_reports_storage_write_error(asset_client: tuple[TestClient, Session], tmp_path: Path) -> None:
    client, session = asset_client
    blocked_path = tmp_path / "not-a-directory"
    blocked_path.write_text("blocks mkdir")
    app.state.asset_storage_path = blocked_path

    response = client.post(
        "/assets/upload",
        files={"file": ("pieza.jpg", b"image bytes", "image/jpeg")},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Uploaded asset could not be stored"
    assert session.scalar(select(SocialAsset)) is None


def test_upload_reports_unsupported_storage_backend(asset_client: tuple[TestClient, Session]) -> None:
    client, session = asset_client
    app.state.asset_storage_backend = "ftp"

    response = client.post(
        "/assets/upload",
        files={"file": ("pieza.jpg", b"image bytes", "image/jpeg")},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Configured asset storage backend is not supported"
    assert session.scalar(select(SocialAsset)) is None


def test_upload_reports_public_url_verification_failure(asset_client: tuple[TestClient, Session]) -> None:
    client, session = asset_client
    app.state.asset_public_url_verifier = lambda public_url: False

    response = client.post(
        "/assets/upload",
        files={"file": ("pieza.webp", b"webp bytes", "image/webp")},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Uploaded asset public URL could not be verified"
    assert session.scalar(select(SocialAsset)) is None
