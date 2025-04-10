import json
import os
import sys

from detectors.yolo_v8 import detect_and_estimate
from utils.file import copy_image_and_json_to_sfm

SFM_IMG_DIR = "sfm_inputs/images/"
SFM_META_DIR = "sfm_inputs/metadata/"
TEMP_JSON_DIR = "temp/json/"
os.makedirs(TEMP_JSON_DIR, exist_ok=True)


def clear_dir(folder):
    if not os.path.exists(folder):
        return
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        if os.path.isfile(path):
            os.remove(path)


def generate_detection_jsons(image_folder):
    for fname in os.listdir(image_folder):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        path = os.path.join(image_folder, fname)
        result = detect_and_estimate(path, scale_cm_per_px=None, save_dir=None)

        result["filename"] = fname
        result["valid_for_sfm"] = any(d["normalized_label"] == "bag" for d in result["detections"])
        result["avg_conf"] = round(
            sum(d["confidence"] for d in result["detections"] if d["normalized_label"] == "bag")
            / max(1, len([d for d in result["detections"] if d["normalized_label"] == "bag"])),
            3,
        )

        json_path = os.path.join(TEMP_JSON_DIR, f"{fname}.json")
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2)


def copy_valid_images_to_sfm(image_folder):
    for fname in os.listdir(TEMP_JSON_DIR):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(TEMP_JSON_DIR, fname)) as f:
            data = json.load(f)

        if not data.get("valid_for_sfm"):
            continue

        image_path = os.path.join(image_folder, data["filename"])
        if not os.path.exists(image_path):
            print(f"이미지 없음: {data['filename']}")
            continue

        copy_image_and_json_to_sfm(image_path, data, SFM_IMG_DIR, SFM_META_DIR)
        print(f"{data['filename']} → SFM 저장 완료")


# Main
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("사용법: python main.py <이미지 폴더 경로>")
        sys.exit(1)

    folder = sys.argv[1]

    print("🧹 이전 결과 정리 중...")
    clear_dir(SFM_IMG_DIR)
    clear_dir(SFM_META_DIR)
    clear_dir(TEMP_JSON_DIR)

    os.makedirs(SFM_IMG_DIR, exist_ok=True)
    os.makedirs(SFM_META_DIR, exist_ok=True)
    os.makedirs(TEMP_JSON_DIR, exist_ok=True)

    print("YOLO 감지 및 JSON 생성 중...")
    generate_detection_jsons(folder)

    print("유효 이미지만 SFM으로 이동 중...")
    copy_valid_images_to_sfm(folder)

    print("전체 완료!")
