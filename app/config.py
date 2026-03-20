import os
from urllib.parse import urlparse
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "storage_service"

    # DigitalOcean Spaces Configuration (S3-compatible)
    _ENDPOINT_RAW: str = (
        os.getenv("STORAGE_ENDPOINT")
        or os.getenv("S3_ENDPOINT")
        or os.getenv("DO_SPACES_ENDPOINT")
        or "sfo3.digitaloceanspaces.com"
    )

    _PARSED_ENDPOINT = urlparse(_ENDPOINT_RAW) if "://" in _ENDPOINT_RAW else None
    MINIO_ENDPOINT: str = (
        (_PARSED_ENDPOINT.netloc or "") if _PARSED_ENDPOINT else _ENDPOINT_RAW
    )

    MINIO_ROOT_USER: str = (
        os.getenv("STORAGE_ACCESS_KEY")
        or os.getenv("S3_ACCESS_KEY")
        or os.getenv("DO_SPACES_ACCESS_KEY")
        or ""
    )
    MINIO_ROOT_PASSWORD: str = (
        os.getenv("STORAGE_SECRET_KEY")
        or os.getenv("S3_SECRET_KEY")
        or os.getenv("DO_SPACES_SECRET_KEY")
        or ""
    )
    MINIO_BUCKET: str = (
        os.getenv("STORAGE_BUCKET")
        or os.getenv("S3_BUCKET")
        or os.getenv("DO_SPACES_BUCKET")
        or "genesis2026"
    )

    _SECURE_RAW: str = os.getenv("STORAGE_SECURE") or ""
    if not _SECURE_RAW and _PARSED_ENDPOINT and _PARSED_ENDPOINT.scheme:
        _SECURE_RAW = "true" if _PARSED_ENDPOINT.scheme.lower() == "https" else "false"
    MINIO_SECURE: bool = (_SECURE_RAW or "true").lower() == "true"

    MINIO_REGION: str = (
        os.getenv("STORAGE_REGION")
        or os.getenv("S3_REGION")
        or os.getenv("DO_SPACES_REGION")
        or "sfo3"
    )

    class Config:
        env_file = ".env"
        env_prefix = "STORAGE_"
        case_sensitive = False


settings = Settings()
