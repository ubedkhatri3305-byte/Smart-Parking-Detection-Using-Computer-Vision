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
    VEHICLE_CLASSES = {"car", "motorcycle", "bus", "truck", "train", "bicycle"}
    
    # Outdoor street and traffic infrastructure
    OUTDOOR_ROAD_OBJECTS = {"traffic light", "fire hydrant", "stop sign", "parking meter", "bench"}

    # Common indoor furniture, home appliances, and domestic items from COCO
    INDOOR_CLASSES = {
        "chair", "couch", "bed", "dining table", "toilet",
        "tv", "laptop", "mouse", "remote", "keyboard", "cell phone",
        "microwave", "oven", "toaster", "sink", "refrigerator",
        "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush",
        "cup", "fork", "knife", "spoon", "bowl", "wine glass", "potted plant", "bottle"
    }

    # Physical road obstacles on pavement/street
    ROAD_OBSTACLE_CLASSES = {
        "person", "dog", "cat", "horse", "sheep", "cow", "backpack", "umbrella", "handbag",
        "suitcase", "sports ball", "skateboard", "debris", "box"
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

    def analyze_scene_environment(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Classifies whether the camera view is an authentic outdoor parking environment
        or an indoor domestic setting (room, living room, bedroom, kitchen, wall, ceiling).
        """
        indoor_items = [d for d in detections if d.get("is_indoor", False) or d.get("class_name", "").lower() in self.INDOOR_CLASSES]
        vehicles = [d for d in detections if d.get("is_vehicle", False)]
        road_objects = [d for d in detections if d.get("class_name", "").lower() in self.OUTDOOR_ROAD_OBJECTS]

        # 1. Direct indoor items detected by YOLO neural network
        if indoor_items:
            indoor_names = sorted(list(set(d["class_name"].capitalize() for d in indoor_items)))
            return {
                "is_parking_scene": False,
                "is_indoor": True,
                "scene_type": "indoor_home",
                "confidence": 0.95,
                "indoor_objects": indoor_names,
                "vehicles_count": len(vehicles),
                "reason": f"Indoor domestic area detected ({', '.join(indoor_names[:4])}). Please point camera outside at a road or parking lot."
            }

        # 2. Real vehicles or road infrastructure present
        if len(vehicles) > 0 or len(road_objects) > 0:
            return {
                "is_parking_scene": True,
                "is_indoor": False,
                "scene_type": "outdoor_parking",
                "confidence": 0.95,
                "indoor_objects": [],
                "vehicles_count": len(vehicles),
                "reason": f"Verified parking environment ({len(vehicles)} vehicles detected)."
            }

        # 3. No objects detected — examine ground surface texture & color
        h, w = image.shape[:2]
        ground_roi = image[int(h * 0.38):, :]
        if ground_roi.size == 0:
            return {
                "is_parking_scene": False,
                "is_indoor": False,
                "scene_type": "invalid_frame",
                "confidence": 0.0,
                "indoor_objects": [],
                "vehicles_count": 0,
                "reason": "Camera frame not loaded."
            }

        hsv = cv2.cvtColor(ground_roi, cv2.COLOR_BGR2HSV)
        s_channel = hsv[:, :, 1]
        v_channel = hsv[:, :, 2]
        h_channel = hsv[:, :, 0]

        mean_s = float(np.mean(s_channel))
        mean_v = float(np.mean(v_channel))
        std_v = float(np.std(v_channel))

        # Blank wall, ceiling, or covered lens (very uniform color)
        if std_v < 13.0 or mean_v < 20 or mean_v > 248:
            return {
                "is_parking_scene": False,
                "is_indoor": True,
                "scene_type": "blank_surface",
                "confidence": 0.90,
                "indoor_objects": ["Wall / Ceiling / Uniform Surface"],
                "vehicles_count": 0,
                "reason": "Camera is pointed at a wall, ceiling, or uniform surface. Point camera toward the road surface."
            }

        # Warm indoor floor (hardwood, tiles, carpets, indoor lighting with high saturation)
        if mean_s > 65.0:
            return {
                "is_parking_scene": False,
                "is_indoor": True,
                "scene_type": "indoor_home",
                "confidence": 0.85,
                "indoor_objects": ["Indoor Floor / Carpet"],
                "vehicles_count": 0,
                "reason": "Indoor floor or carpet detected. Please point camera outside at a road or parking lot."
            }

        # Check for painted road markings (white/yellow bay stripes) on asphalt
        white_mask = (s_channel < 45) & (v_channel > 185)
        yellow_mask = (h_channel >= 15) & (h_channel <= 38) & (s_channel > 80) & (v_channel > 130)
        marking_pixels = np.count_nonzero(white_mask | yellow_mask)
        total_ground_pixels = ground_roi.shape[0] * ground_roi.shape[1]
        marking_ratio = marking_pixels / float(total_ground_pixels)

        if mean_s < 48.0 and marking_ratio >= 0.008:
            return {
                "is_parking_scene": True,
                "is_indoor": False,
                "scene_type": "outdoor_parking",
                "confidence": 0.88,
                "indoor_objects": [],
                "vehicles_count": 0,
                "reason": "Outdoor asphalt surface with marked parking bays detected."
            }

        # Unconfirmed surface without parking markers
        return {
            "is_parking_scene": False,
            "is_indoor": False,
            "scene_type": "unconfirmed_surface",
            "confidence": 0.70,
            "indoor_objects": [],
            "vehicles_count": 0,
            "reason": "Searching for parking area. Align camera with parking bays, road markings, or parked vehicles."
        }

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
                    "is_indoor": False,
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
        Detects both vehicles, obstacles, and indoor objects with high precision.
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
                is_indoor = cls_name in self.INDOOR_CLASSES
                is_road_object = cls_name in self.OUTDOOR_ROAD_OBJECTS
                is_obstacle = not is_vehicle and not is_indoor

                if is_vehicle:
                    category = "vehicle"
                elif is_indoor:
                    category = "indoor_object"
                else:
                    category = "obstacle"

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
                    "is_indoor": is_indoor,
                    "is_road_object": is_road_object,
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

        # Detect physical ground hazards only if not in an indoor room
        indoor_count = sum(1 for d in detections if d.get("is_indoor", False))
        if indoor_count == 0:
            try:
                cv_hazards = self.detect_ground_hazards(image, existing_bboxes)
                detections.extend(cv_hazards)
            except Exception:
                pass

        return detections

