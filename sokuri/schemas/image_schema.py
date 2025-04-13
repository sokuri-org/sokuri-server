from typing import List
from pydantic import BaseModel

class ImageUploadRequest(BaseModel):
    product_id: str
    source: str
    image_urls: List[str]
