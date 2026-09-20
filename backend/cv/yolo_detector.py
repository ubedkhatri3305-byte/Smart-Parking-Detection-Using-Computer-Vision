"""
YOLO Object Detection Engine for Smart Parking Detection
Detects vehicles (cars, motorcycles, trucks, buses) and obstacles (pedestrians, bicycles, debris).
"""

from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from ultralytics import YOLO


class ParkingYOLODetector:
    # Target classes from COCO dataset relevant to parking detection
    VEHICLE_CLASSES = {"car", "motorcycle", "bus", "truck"}
    OBSTACLE_CLASSES = {"person", "bicycle", "stop sign", "traffic light", "fire hydrant", "backpack", "suitcase"}

    def __init__(self, model_name: str = "yolov8n.pt", conf_threshold: float = 0.25):
        """
        Initialize the YOLO model.
        :param model_name: Model weights ('yolov8n.pt' for fast, lightweight inference)
        :param conf_threshold: Minimum detection confidence threshold
        """
        self.conf_threshold = conf_threshold
        self.model = YOLO(model_name)
        self.class_names = self.model.names

    def detect(self, image: np.ndarray, conf_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Run inference on an image (BGR numpy array).
        :param image: Input image array
        :param conf_threshold: Optional override for confidence threshold
        :return: List of detection dictionaries
        """
        threshold = conf_threshold or self.conf_threshold
        results = self.model(image, conf=threshold, verbose=False)[0]

        detections: List[Dict[str, Any]] = []

        if results.boxes is None or len(results.boxes) == 0:
            return detections

        boxes = results.boxes.xyxy.cpu().numpy()
        confidences = results.boxes.conf.cpu().numpy()
        class_ids = results.boxes.cls.cpu().numpy().astype(int)

        for i, box in enumerate(boxes):
            x1, y1, x2, y2 = [float(v) for v in box]
            cls_id = int(class_ids[i])
            cls_name = self.class_names.get(cls_id, str(cls_id))
            conf = float(confidences[i])

            is_vehicle = cls_name in self.VEHICLE_CLASSES
            is_obstacle = cls_name in self.OBSTACLE_CLASSES or cls_name == "person"

            # Determine category
            if is_vehicle:
                category = "vehicle"
            elif is_obstacle:
                category = "obstacle"
            else:
                category = "other"

            # Compute key geometric references
            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0
            bottom_center = (center_x, y2)  # Contact point with ground plane
            width = x2 - x1
            height = y2 - y1

            detections.append({
                "class_id": cls_id,
                "class_name": cls_name,
                "category": category,
                "confidence": round(conf, 3),
                "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                "center": (round(center_x, 1), round(center_y, 1)),
                "bottom_center": (round(bottom_center[0], 1), round(bottom_center[1], 1)),
                "width": round(width, 1),
                "height": round(height, 1),
                # 4-corner polygon
                "polygon": [
                    [round(x1, 1), round(y1, 1)],
                    [round(x2, 1), round(y1, 1)],
                    [round(x2, 1), round(y2, 1)],
                    [round(x1, 1), round(y2, 1)]
                ]
            })

        return detections
