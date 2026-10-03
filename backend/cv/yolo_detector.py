"""
YOLO Object Detection Engine for Smart Parking Detection
Detects vehicles (cars, motorcycles, trucks, buses) and obstacles (pedestrians, bicycles, debris).
"""

from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from ultralytics import YOLO


class ParkingYOLODetector:
    # Target vehicle classes
    VEHICLE_CLASSES = {"car", "motorcycle", "bus", "truck", "train"}
    
    # Common known obstacle classes from COCO
    KNOWN_OBSTACLE_CLASSES = {
        "person", "bicycle", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
        "dog", "cat", "horse", "sheep", "cow", "backpack", "umbrella", "handbag", "suitcase",
        "bottle", "cup", "chair", "couch", "potted plant", "bed", "dining table", "tv", "laptop",
        "cell phone", "box", "debris", "sports ball", "skateboard"
    }

    def __init__(self, model_name: str = "yolov8n.pt", conf_threshold: float = 0.18):
        """
        Initialize the YOLO model.
        :param model_name: Model weights ('yolov8n.pt' for fast, lightweight inference)
        :param conf_threshold: Minimum detection confidence threshold (0.18 for sensitive obstacle detection)
        """
        self.conf_threshold = conf_threshold
        self.model = YOLO(model_name)
        self.class_names = self.model.names

    def detect_ground_hazards(self, image: np.ndarray, existing_bboxes: List[List[float]]) -> List[Dict[str, Any]]:
        """
        OpenCV Computer Vision ground hazard detector.
        Catches physical ground obstacles (cones, boxes, barriers, debris, curbs)
        even if not classified by standard COCO YOLO labels.
        """
        h, w = image.shape[:2]
        y_ground = int(h * 0.40)
        ground_roi = image[y_ground:, :]
        if ground_roi.size == 0:
            return []

        # Multi-channel color edge detection catches colored obstacles (cones, barriers, red/yellow objects, debris)
        edges_b = cv2.Canny(ground_roi[:, :, 0], 25, 75)
        edges_g = cv2.Canny(ground_roi[:, :, 1], 25, 75)
        edges_r = cv2.Canny(ground_roi[:, :, 2], 25, 75)
        edges = cv2.bitwise_or(edges_b, cv2.bitwise_or(edges_g, edges_r))

        # Connect nearby contour edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hazards: List[Dict[str, Any]] = []
        min_area = (w * h) * 0.015  # At least 1.5% of frame area

        for cnt in contours:
            rx, ry, rw, rh = cv2.boundingRect(cnt)
            box_area = rw * rh
            if box_area < min_area or rw < 25 or rh < 25:
                continue

            abs_y1 = float(y_ground + ry)
            abs_y2 = float(abs_y1 + rh)
            abs_x1 = float(rx)
            abs_x2 = float(rx + rw)

            # Check overlap with existing YOLO detections
            overlaps = False
            for ex in existing_bboxes:
                ex1, ey1, ex2, ey2 = ex
                ix1 = max(abs_x1, ex1)
                iy1 = max(abs_y1, ey1)
                ix2 = min(abs_x2, ex2)
                iy2 = min(abs_y2, ey2)
                if ix2 > ix1 and iy2 > iy1:
                    inter_area = (ix2 - ix1) * (iy2 - iy1)
                    box_area = rw * rh
                    if inter_area / float(box_area) > 0.25:
                        overlaps = True
                        break

            if not overlaps:
                cx = (abs_x1 + abs_x2) / 2.0
                cy = (abs_y1 + abs_y2) / 2.0
                hazards.append({
                    "class_id": 999,
                    "class_name": "Ground Obstacle",
                    "category": "obstacle",
                    "confidence": 0.82,
                    "is_vehicle": False,
                    "is_obstacle": True,
                    "bbox": [round(abs_x1, 1), round(abs_y1, 1), round(abs_x2, 1), round(abs_y2, 1)],
                    "center": (round(cx, 1), round(cy, 1)),
                    "bottom_center": (round(cx, 1), round(abs_y2, 1)),
                    "width": round(float(rw), 1),
                    "height": round(float(rh), 1),
                    "polygon": [
                        [round(abs_x1, 1), round(abs_y1, 1)],
                        [round(abs_x2, 1), round(abs_y1, 1)],
                        [round(abs_x2, 1), round(abs_y2, 1)],
                        [round(abs_x1, 1), round(abs_y2, 1)]
                    ]
                })

        return hazards

    def detect(self, image: np.ndarray, conf_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Run inference on an image (BGR numpy array).
        Detects both vehicles and obstacles with high sensitivity.
        :param image: Input image array
        :param conf_threshold: Optional override for confidence threshold
        :return: List of detection dictionaries
        """
        threshold = conf_threshold or self.conf_threshold
        results = self.model(image, conf=threshold, verbose=False)[0]

        detections: List[Dict[str, Any]] = []
        existing_bboxes: List[List[float]] = []

        if results.boxes is not None and len(results.boxes) > 0:
            boxes = results.boxes.xyxy.cpu().numpy()
            confidences = results.boxes.conf.cpu().numpy()
            class_ids = results.boxes.cls.cpu().numpy().astype(int)

            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = [float(v) for v in box]
                cls_id = int(class_ids[i])
                cls_name = self.class_names.get(cls_id, str(cls_id)).lower()
                conf = float(confidences[i])

                is_vehicle = cls_name in self.VEHICLE_CLASSES
                # Any non-vehicle detected in parking view is an obstacle!
                is_obstacle = not is_vehicle
                category = "vehicle" if is_vehicle else "obstacle"

                # Compute key geometric references
                center_x = (x1 + x2) / 2.0
                center_y = (y1 + y2) / 2.0
                bottom_center = (center_x, y2)  # Ground contact point
                width = x2 - x1
                height = y2 - y1

                det = {
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "category": category,
                    "is_vehicle": is_vehicle,
                    "is_obstacle": is_obstacle,
                    "confidence": round(conf, 3),
                    "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                    "center": (round(center_x, 1), round(center_y, 1)),
                    "bottom_center": (round(bottom_center[0], 1), round(bottom_center[1], 1)),
                    "width": round(width, 1),
                    "height": round(height, 1),
                    "polygon": [
                        [round(x1, 1), round(y1, 1)],
                        [round(x2, 1), round(y1, 1)],
                        [round(x2, 1), round(y2, 1)],
                        [round(x1, 1), round(y2, 1)]
                    ]
                }
                detections.append(det)
                existing_bboxes.append([x1, y1, x2, y2])

        # Also detect any unclassified ground hazards (cones, debris, boxes, barriers)
        try:
            cv_hazards = self.detect_ground_hazards(image, existing_bboxes)
            detections.extend(cv_hazards)
        except Exception as e:
            # Fallback gracefully if CV morphological processing encounters an issue
            pass

        return detections
