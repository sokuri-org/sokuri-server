from ultralytics import YOLO

model = YOLO("yolov8s.pt")

BAG_LABELS = {"bag", "backpack", "handbag", "suitcase"}

def is_bag(label: str) -> bool:
    return label.lower() in BAG_LABELS

def detect_and_estimate(image_path: str) -> dict:
    results = model(image_path)

    bag_detections = []

    for r in results:
        for box in r.boxes:
            conf = float(box.conf)
            if conf < 0.3:
                continue

            raw_label = r.names[int(box.cls[0])]

            if is_bag(raw_label):
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                width = x2 - x1
                height = y2 - y1
                area = width * height

                bag_detections.append({
                    "confidence": conf,
                    "area": area,
                    "bbox": [x1, y1, x2, y2],
                })

    if not bag_detections:
        raise ValueError("가방을 찾지 못했습니다.")

    best_bag = max(bag_detections, key=lambda d: d["confidence"] * d["area"])

    x1, y1, x2, y2 = best_bag["bbox"]
    width_px = float(x2 - x1)
    height_px = float(y2 - y1)
    confidence = float(best_bag["confidence"])

    return {
        "width_px": width_px,
        "height_px": height_px,
        "confidence": confidence
    }
