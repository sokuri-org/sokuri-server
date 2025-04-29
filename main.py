import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sokuri.routers.crawl_Images import router as crawl_router
from sokuri.routers.packs import router as pack_router

load_dotenv()

app = FastAPI(
    title="Sokuri", description="소쿠리 앱용 가방 이미지 분석 및 수납 시뮬레이션 API", version="1.0.0"
)

app.include_router(crawl_router, prefix="/bags/images", tags=["크롤링"])
app.include_router(pack_router, prefix="/bags/packages", tags=["패킹"])

origins = [os.getenv("CLIENT_URL")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
