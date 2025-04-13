from fastapi import APIRouter
from sokuri.routers.images import router as images_router

router = APIRouter()
router.include_router(images_router)
