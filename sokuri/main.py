import json
import os
import sys

from fastapi import FastAPI

from sokuri.routers.images import router as images_router
from sokuri.yolo.detect import detect_and_estimate

DETECTION_JSON_DIR = "data/json/"
RESULT_IMAGE_DIR = "data/results/"

app = FastAPI(
    title="Sokuri YOLO API", description="이미지 감지 및 분석을 위한 API 서비스", version="1.0.0"
)

app.include_router(images_router)


@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Sokuri YOLO API is alive"}


def clear_dir(folder):
    if not os.path.exists(folder):
        return
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if os.path.isfile(path):
            os.remove(path)


def generate_detection_results(image_folder):
    os.makedirs(DETECTION_JSON_DIR, exist_ok=True)
    os.makedirs(RESULT_IMAGE_DIR, exist_ok=True)

    for filename in os.listdir(image_folder):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(image_folder, filename)

        result = detect_and_estimate(image_path, scale_cm_per_px=None, save_dir=RESULT_IMAGE_DIR)

        result["filename"] = filename
        result["valid"] = any(d["normalized_label"] == "bag" for d in result["detections"])

        bag_confidences = [
            d["confidence"] for d in result["detections"] if d["normalized_label"] == "bag"
        ]
        result["avg_conf"] = round(sum(bag_confidences) / max(1, len(bag_confidences)), 3)

        json_path = os.path.join(DETECTION_JSON_DIR, f"{filename}.json")
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2)

        print(f"{filename} → bbox: {result['bag_width_px']}px | conf: {result['avg_conf']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python main.py <이미지 폴더 경로>")
        sys.exit(1)

    image_folder = sys.argv[1]

    print("🧹 이전 감지 결과 정리 중...")
    clear_dir(DETECTION_JSON_DIR)
    clear_dir(RESULT_IMAGE_DIR)

    print("YOLO 감지 및 bbox 추정 중...")
    generate_detection_results(image_folder)

    print("감지 완료: 결과 JSON 및 시각화 이미지 저장됨")
