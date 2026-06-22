from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


ALLOWED_ASSET_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
}


@dataclass(frozen=True)
class StoredAsset:
    file_name: str
    public_url: str
    verification_url: str
    size_bytes: int


class LocalAssetStorage:
    def __init__(self, storage_path: Path, public_base_url: str, public_verify_base_url: str | None = None) -> None:
        self.storage_path = storage_path
        self.public_base_url = public_base_url.rstrip("/")
        self.public_verify_base_url = (public_verify_base_url or public_base_url).rstrip("/")

    def save(self, original_file_name: str, mime_type: str, content: bytes) -> StoredAsset:
        extension = self._extension_for(original_file_name, mime_type)
        file_name = f"{uuid4().hex}{extension}"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        target = self.storage_path / file_name
        target.write_bytes(content)
        return StoredAsset(
            file_name=file_name,
            public_url=f"{self.public_base_url}/{file_name}",
            verification_url=f"{self.public_verify_base_url}/{file_name}",
            size_bytes=len(content),
        )

    def _extension_for(self, original_file_name: str, mime_type: str) -> str:
        allowed_extension = ALLOWED_ASSET_MIME_TYPES[mime_type]
        original_extension = Path(original_file_name).suffix.lower()
        if original_extension == ".jpeg" and mime_type == "image/jpeg":
            return ".jpg"
        if original_extension == allowed_extension:
            return original_extension
        return allowed_extension
