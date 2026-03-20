from typing import Optional
from minio import Minio

from .config import settings


_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ROOT_USER,
    secret_key=settings.MINIO_ROOT_PASSWORD,
    secure=settings.MINIO_SECURE,
    region=settings.MINIO_REGION,
)


def get_client() -> Minio:
    return _client


def ensure_bucket_exists(bucket_name: Optional[str] = None) -> None:
    """Ensure a bucket exists, creating it if necessary."""
    target_bucket = bucket_name or settings.MINIO_BUCKET
    if not _client.bucket_exists(target_bucket):
        _client.make_bucket(target_bucket, location=settings.MINIO_REGION)
