from pydantic import BaseModel


class AssetUploadRead(BaseModel):
    asset_id: int
    public_url: str
    file_name: str
    mime_type: str
    size_bytes: int
