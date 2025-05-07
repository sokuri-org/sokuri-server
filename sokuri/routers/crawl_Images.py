import os

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from sokuri.schemas.image_schema import ImageUploadRequest
from sokuri.services.estimate_service import process_images

load_dotenv()

router = APIRouter(prefix="/bags/images", tags=["images"])

CRAWLER_API_URL = os.getenv("CRAWLER_API_URL")

class CrawlRequest(BaseModel):
    url: str

@router.post("/")
async def crawl_and_analyze(payload: CrawlRequest):
    try:
        url = payload.url
        if not url:
            raise HTTPException(status_code=400, detail="URL이 필요합니다.")

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(CRAWLER_API_URL, json={"url": url})
            response.raise_for_status()
            result = response.json()

        image_urls = result.get("images")
        product_id = result.get("product_id")
        category = result.get("category")

        if not image_urls:
            raise HTTPException(status_code=404, detail="후기 이미지를 찾을 수 없습니다.")

        payload_for_process = ImageUploadRequest(
            image_urls=image_urls,
            product_id=product_id,
            category=category,
        )

        results = process_images(payload_for_process)

        if not results:
            raise HTTPException(status_code=500, detail="모든 이미지 처리 실패")

        filtered = [r for r in results if r["confidence"] >= 0.5]

        if not filtered:
            print("신뢰도 높은 이미지가 없어, 가장 신뢰도 높은 결과를 사용합니다")
            best_result = max(results, key=lambda r: r["confidence"])
            filtered = [best_result]

        width_list = [r["width_cm"] for r in results]
        height_list = [r["height_cm"] for r in results]
        depth_list = [r["depth_cm"] for r in results]

        avg_width = round(sum(width_list) / len(width_list), 1)
        avg_height = round(sum(height_list) / len(height_list), 1)
        avg_depth = round(sum(depth_list) / len(depth_list), 1)


        return {
            "bag": {
                "width": avg_width,
                "height": avg_height,
                "depth": avg_depth,
            },
            "category": category,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
