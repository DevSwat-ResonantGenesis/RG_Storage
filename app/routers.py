from typing import List, Optional
from datetime import datetime
import io

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .config import settings
from .minio_client import ensure_bucket_exists, get_client


router = APIRouter(prefix="/storage", tags=["storage"])


class FileInfo(BaseModel):
    key: str
    size: int
    content_type: Optional[str]
    last_modified: Optional[str]
    bucket: str


class UploadResponse(BaseModel):
    bucket: str
    key: str
    size: int
    url: str


class BucketInfo(BaseModel):
    name: str
    creation_date: Optional[str]


@router.get("/health")
async def health():
    return {"service": "storage", "status": "ok"}


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    key: Optional[str] = None,
    bucket: Optional[str] = None,
    request: Request = None,
):
    """Upload a file to storage."""
    target_bucket = bucket or settings.MINIO_BUCKET
    ensure_bucket_exists(target_bucket)
    client = get_client()

    object_name = key or file.filename
    data = await file.read()
    size = len(data)

    client.put_object(
        target_bucket,
        object_name,
        data=io.BytesIO(data),
        length=size,
        content_type=file.content_type or "application/octet-stream",
    )

    # Generate URL
    url = f"/api/storage/download/{object_name}"

    return UploadResponse(
        bucket=target_bucket,
        key=object_name,
        size=size,
        url=url,
    )


@router.post("/upload/batch")
async def upload_batch(
    files: List[UploadFile] = File(...),
    bucket: Optional[str] = None,
):
    """Upload multiple files."""
    target_bucket = bucket or settings.MINIO_BUCKET
    ensure_bucket_exists(target_bucket)
    client = get_client()

    results = []
    for file in files:
        data = await file.read()
        size = len(data)

        client.put_object(
            target_bucket,
            file.filename,
            data=io.BytesIO(data),
            length=size,
            content_type=file.content_type or "application/octet-stream",
        )

        results.append({
            "key": file.filename,
            "size": size,
            "bucket": target_bucket,
        })

    return {"uploaded": len(results), "files": results}


@router.get("/download/{key:path}")
async def download_file(key: str, bucket: Optional[str] = None):
    """Download a file from storage."""
    target_bucket = bucket or settings.MINIO_BUCKET
    client = get_client()

    try:
        response = client.get_object(target_bucket, key)
        
        # Get content type from stat
        stat = client.stat_object(target_bucket, key)
        content_type = stat.content_type or "application/octet-stream"

        return StreamingResponse(
            response,
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={key.split('/')[-1]}"},
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {key}")


@router.get("/files", response_model=List[FileInfo])
async def list_files(
    prefix: Optional[str] = None,
    bucket: Optional[str] = None,
    limit: int = 100,
):
    """List files in storage."""
    target_bucket = bucket or settings.MINIO_BUCKET
    ensure_bucket_exists(target_bucket)
    client = get_client()

    objects = client.list_objects(target_bucket, prefix=prefix or "", recursive=True)

    files = []
    count = 0
    for obj in objects:
        if count >= limit:
            break
        files.append(FileInfo(
            key=obj.object_name,
            size=obj.size,
            content_type=obj.content_type,
            last_modified=str(obj.last_modified) if obj.last_modified else None,
            bucket=target_bucket,
        ))
        count += 1

    return files


@router.get("/files/{key:path}", response_model=FileInfo)
async def get_file_info(key: str, bucket: Optional[str] = None):
    """Get file metadata."""
    target_bucket = bucket or settings.MINIO_BUCKET
    client = get_client()

    try:
        stat = client.stat_object(target_bucket, key)
        return FileInfo(
            key=key,
            size=stat.size,
            content_type=stat.content_type,
            last_modified=str(stat.last_modified) if stat.last_modified else None,
            bucket=target_bucket,
        )
    except Exception:
        raise HTTPException(status_code=404, detail=f"File not found: {key}")


@router.delete("/files/{key:path}")
async def delete_file(key: str, bucket: Optional[str] = None):
    """Delete a file from storage."""
    target_bucket = bucket or settings.MINIO_BUCKET
    client = get_client()

    try:
        client.remove_object(target_bucket, key)
        return {"status": "deleted", "key": key, "bucket": target_bucket}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {key}")


@router.get("/buckets", response_model=List[BucketInfo])
async def list_buckets():
    """List all buckets."""
    client = get_client()
    buckets = client.list_buckets()

    return [
        BucketInfo(
            name=b.name,
            creation_date=str(b.creation_date) if b.creation_date else None,
        )
        for b in buckets
    ]


@router.post("/buckets/{bucket_name}")
async def create_bucket(bucket_name: str):
    """Create a new bucket."""
    client = get_client()

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        return {"status": "created", "bucket": bucket_name}
    
    return {"status": "exists", "bucket": bucket_name}


@router.get("/presigned/{key:path}")
async def get_presigned_url(
    key: str,
    bucket: Optional[str] = None,
    expires: int = 3600,
):
    """Generate a presigned URL for file access."""
    target_bucket = bucket or settings.MINIO_BUCKET
    client = get_client()

    try:
        from datetime import timedelta
        url = client.presigned_get_object(
            target_bucket,
            key,
            expires=timedelta(seconds=expires),
        )
        return {"url": url, "expires_in": expires}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {key}")
