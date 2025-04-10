def estimate_bag_size(detections, is_bag_fn):

    bag_boxes = [d for d in detections if is_bag_fn(d.get("normalized_label"))]

    if not bag_boxes:
        return {
            "width_px": 0,
            "height_px": 0,
            "cm": None,
            "note": "가방이 감지되지 않음"
        }

    def bbox_area(bbox):
        x1, y1, x2, y2 = bbox
        return abs((x2 - x1) * (y2 - y1))

    largest_box = max(bag_boxes, key=lambda d: bbox_area(d["bbox"]))
    x1, y1, x2, y2 = largest_box["bbox"]

    width_px = x2 - x1
    height_px = y2 - y1

    result = {
        "width_px": width_px,
        "height_px": height_px,
        "cm": None,
        "note": "기준 객체 없음 - 실측 생략"
    }

    return result
