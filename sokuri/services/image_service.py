import os
import json
import uuid
import requests
import logging
from typing import List
from sokuri.yolo.detect import detect_and_estimate
from sokuri.schemas.image_schema import ImageUploadRequest

SAVE_DIR = "sokuri/yolo/data/images/crawler_images"
RESULT_DIR = "sokuri/yolo/data/results"
JSON_DIR = "sokuri/yolo/data/json"

for path in [SAVE_DIR, RESULT_DIR, JSON_DIR]:
    os.makedirs(path, exist_ok=True)

logger = logging.getLogger("image_service")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

def handle_single_image(url: str, product_id: str) -> dict:
    unique_id = uuid.uuid4().hex
    filename = f"{product_id}_{unique_id}.jpg"
    image_path = os.path.join(SAVE_DIR, filename)

    logger.info(f"📥 Downloading image from {url}")
    response = requests.get(url, timeout=5)
    response.raise_for_status()

    with open(image_path, "wb") as f:
        f.write(response.content)

    logger.info(f"Running YOLO detection for {filename}")
    result = detect_and_estimate(
        image_path,
        scale_cm_per_px=None,
        save_dir=RESULT_DIR
    )

    result["filename"] = filename

    json_path = os.path.join(JSON_DIR, f"{filename}.json")
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)

    return result

async def process_images(payload: ImageUploadRequest) -> List[dict]:
    results = []

    for url in payload.image_urls:
        try:
            result = handle_single_image(url, payload.product_id)
            results.append(result)

        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to download image: {url} - {e}")
        except Exception as e:
            logger.error(f"Error processing image {url}: {e}", exc_info=True)

    return results
