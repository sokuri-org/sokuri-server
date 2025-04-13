import os

import cv2
from ultralytics import YOLO

from sokuri.yolo.estimator import estimate_bag_size

MODEL_PATH = "sokuri/yolo/models/yolov8n.pt"
model = YOLO(MODEL_PATH)

BAG_LABELS = {"bag", "backpack", "handbag", "suitcase"}


def is_bag(label: str) -> bool:
    return label.lower() in BAG_LABELS


def normalize_label(label: str) -> str:
    return "bag" if is_bag(label) else label.lower()


def detect_and_estimate(image_path: str, scale_cm_per_px=None, save_dir=None) -> dict:
    results = model(image_path)
    img = cv2.imread(image_path)
    filename = os.path.basename(image_path)

    detections = []

    for r in results:
        for box in r.boxes:
            conf = float(box.conf)
            if conf < 0.3:
                continue

            raw_label = r.names[int(box.cls[0])]
            norm_label = normalize_label(raw_label)
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            detections.append(
                {
                    "label": raw_label,
                    "normalized_label": norm_label,
                    "confidence": round(conf, 2),
                    "bbox": [x1, y1, x2, y2],
                }
            )

            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                text = f"{norm_label} ({round(conf, 2)})"
                cv2.putText(img, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4)
                cv2.putText(
                    img, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1
                )

    if save_dir:
        out_path = os.path.join(save_dir, filename)
        cv2.imwrite(out_path, img)

    size_info = estimate_bag_size(
        detections, lambda label: normalize_label(label) == "bag", scale_cm_per_px
    )

    return {
        "filename": filename,
        "detections": detections,
        "contains_bag": any(d["normalized_label"] == "bag" for d in detections),
        "contains_reference": scale_cm_per_px is not None,
        "estimated_width_cm": size_info["cm"],
        "bag_width_px": size_info["width_px"],
        "bag_height_px": size_info["height_px"],
        "note": size_info["note"],
    }
