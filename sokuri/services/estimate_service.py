import logging
import os
import uuid

import requests

from sokuri.schemas.image_schema import ImageUploadRequest
from sokuri.utils.bag_average_size import CATEGORY_AVERAGE_SIZES
from sokuri.yolo.detect import detect_and_estimate

SAVE_DIR = "sokuri/yolo/data/images/crawler_images"
os.makedirs(SAVE_DIR, exist_ok=True)

logger = logging.getLogger("image_service")
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)

def download_image(url: str, product_id: str) -> str:
    unique_id = uuid.uuid4().hex
    filename = f"{product_id}_{unique_id}.jpg"
    image_path = os.path.join(SAVE_DIR, filename)

    logger.info(f"📥 이미지 다운로드 {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout as err:
        logger.error(f"다운로드 타임아웃 발생: {url} - {err}")
        raise
    except requests.exceptions.ConnectionError as err:
        logger.error(f"서버 연결 실패: {url} - {err}")
        raise
    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP 오류 발생: {url} - {err}")
        raise
    except requests.exceptions.RequestException as err:
        logger.error(f"요청 실패: {url} - {err}")
        raise

    with open(image_path, "wb") as f:
        f.write(response.content)

    return image_path

def handle_review_image(url: str, product_id: str, category: str) -> dict[str, float | str]:
    image_path = download_image(url, product_id)

    detect_result = detect_and_estimate(image_path)

    width_px = detect_result["width_px"]
    height_px = detect_result["height_px"]
    confidence = detect_result["confidence"]

    avg_size = CATEGORY_AVERAGE_SIZES.get(category)
    if not avg_size:
        raise ValueError(f"가방 {category} 데이터가 없습니다")

    width_ratio = width_px / height_px if height_px != 0 else 1.0
    estimated_width_cm = avg_size["width_cm"] * width_ratio

    return {
        "width_cm": round(estimated_width_cm, 1),
        "height_cm": round(avg_size["height_cm"], 1),
        "depth_cm": round(avg_size["depth_cm"], 1),
        "confidence": confidence,
        "filename": os.path.basename(image_path)
    }

def process_images(payload: ImageUploadRequest) -> list[dict]:
    results = []

    for url in payload.image_urls:
        try:
            result = handle_review_image(url, payload.product_id, payload.category)
            results.append(result)

        except requests.exceptions.Timeout as err:
            logger.warning(f"타임아웃: {url} - {err}")
        except requests.exceptions.ConnectionError as err:
            logger.warning(f"서버 연결 실패: {url} - {err}")
        except requests.exceptions.HTTPError as err:
            logger.warning(f"HTTP 오류: {url} - {err}")
        except requests.exceptions.RequestException as err:
            logger.warning(f"요청 실패: {url} - {err}")
        except ValueError as err:
            logger.error(f"잘못된 데이터 오류: {url} - {err}")
        except KeyError as err:
            logger.error(f"키 에러 발생: {url} - {err}")
        except Exception as err:
            logger.error(f"기타 에러 발생: {url} - {err}", exc_info=True)

    return results
