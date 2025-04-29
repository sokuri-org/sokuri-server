from pydantic import BaseModel


class ImageUploadRequest(BaseModel):
    product_id: str
    category: str
    image_urls: list[str]
