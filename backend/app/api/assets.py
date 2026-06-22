from pathlib import Path
from urllib.error import URLError
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db import get_session
from app.models.social import SocialAsset
from app.schemas.assets import AssetUploadRead
from app.services.asset_storage import ALLOWED_ASSET_MIME_TYPES, LocalAssetStorage

router = APIRouter(prefix="/assets", tags=["assets"])


def verify_public_url(public_url: str) -> bool:
    request = UrlRequest(public_url, method="GET")
    try:
        with urlopen(request, timeout=5) as response:
            return 200 <= response.status < 400
    except (OSError, URLError):
        return False


def get_max_size_bytes(request: Request) -> int:
    if hasattr(request.app.state, "asset_max_size_bytes"):
        return int(request.app.state.asset_max_size_bytes)
    settings = get_settings()
    return settings.asset_max_size_mb * 1024 * 1024


def get_storage(request: Request) -> LocalAssetStorage:
    if hasattr(request.app.state, "asset_storage_backend"):
        storage_backend = str(request.app.state.asset_storage_backend)
    else:
        storage_backend = get_settings().asset_storage_backend
    if storage_backend != "local":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configured asset storage backend is not supported",
        )

    if hasattr(request.app.state, "asset_storage_path"):
        storage_path = Path(request.app.state.asset_storage_path)
    else:
        storage_path = Path(get_settings().asset_storage_path)

    if hasattr(request.app.state, "asset_public_base_url"):
        public_base_url = str(request.app.state.asset_public_base_url)
    else:
        public_base_url = get_settings().asset_public_base_url

    if hasattr(request.app.state, "asset_public_verify_base_url"):
        public_verify_base_url = str(request.app.state.asset_public_verify_base_url)
    else:
        public_verify_base_url = get_settings().asset_public_verify_base_url

    return LocalAssetStorage(
        storage_path=storage_path,
        public_base_url=public_base_url,
        public_verify_base_url=public_verify_base_url,
    )


def get_url_verifier(request: Request):
    if hasattr(request.app.state, "asset_public_url_verifier"):
        return request.app.state.asset_public_url_verifier
    return verify_public_url


@router.post("/upload", response_model=AssetUploadRead, status_code=status.HTTP_201_CREATED)
def upload_asset(
    file: UploadFile,
    session: Session = Depends(get_session),
    max_size_bytes: int = Depends(get_max_size_bytes),
    storage: LocalAssetStorage = Depends(get_storage),
    url_verifier=Depends(get_url_verifier),
) -> AssetUploadRead:
    mime_type = file.content_type or ""
    if mime_type not in ALLOWED_ASSET_MIME_TYPES:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported asset MIME type")

    content = file.file.read(max_size_bytes + 1)
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded asset is empty")
    if len(content) > max_size_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Uploaded asset is too large")

    try:
        stored = storage.save(file.filename or "asset", mime_type, content)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Uploaded asset could not be stored",
        ) from exc

    if not url_verifier(stored.verification_url):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Uploaded asset public URL could not be verified",
        )

    asset = SocialAsset(
        file_name=stored.file_name,
        public_url=stored.public_url,
        mime_type=mime_type,
        size_bytes=stored.size_bytes,
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)

    return AssetUploadRead(
        asset_id=asset.id,
        public_url=asset.public_url,
        file_name=asset.file_name,
        mime_type=asset.mime_type,
        size_bytes=asset.size_bytes or 0,
    )
