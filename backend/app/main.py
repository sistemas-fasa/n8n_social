from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.assets import router as assets_router
from app.api.campaigns import router as campaigns_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="FASA Social Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

asset_storage_path = Path(settings.asset_storage_path)
app.mount("/public/assets", StaticFiles(directory=asset_storage_path, check_dir=False), name="public-assets")
app.include_router(assets_router)
app.include_router(campaigns_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.service_name,
    }
