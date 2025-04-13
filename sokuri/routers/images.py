from fastapi import APIRouter, HTTPException
from sokuri.schemas.image_schema import ImageUploadRequest
from sokuri.services.image_service import process_images

router = APIRouter(prefix="/api/v1/images", tags=["Images"])

@router.post("/")
async def upload_images(payload: ImageUploadRequest):
    try:
        results = await process_images(payload)
        return {"status": "success", "processed": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
