"""
Parking Space Occupancy Analyzer
Evaluates parking slot occupancy status (Available 🟢, Occupied 🔴, Blocked 🟡)
using Shapely polygon intersection, IoU, and obstacle spatial analysis.
"""

from typing import List, Dict, Any, Optional, Tuple
from shapely.geometry import Polygon, Point, box


class SlotStatus:
    AVAILABLE = "AVAILABLE"    # 🟢 Clear & ready for vehicle
    OCCUPIED = "OCCUPIED"      # 🔴 Parked vehicle present
    BLOCKED = "BLOCKED"        # 🟡 Blocked by pedestrian, bike, cone, or obstruction


class ParkingOccupancyAnalyzer:
    def __init__(
        self,
        vehicle_iou_threshold: float = 0.20,
        obstacle_iou_threshold: float = 0.05,
        min_overlap_area_ratio: float = 0.15
    ):
        """
        :param vehicle_iou_threshold: Overlap ratio of slot covered by vehicle to consider occupied
        :param obstacle_iou_threshold: Overlap ratio of slot covered by obstacle to consider blocked
        :param min_overlap_area_ratio: Minimum ratio of object area falling inside the slot
        """
        self.vehicle_iou_threshold = vehicle_iou_threshold
        self.obstacle_iou_threshold = obstacle_iou_threshold
        self.min_overlap_area_ratio = min_overlap_area_ratio

    def evaluate_slots(
        self,
        slots: List[Dict[str, Any]],
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate a list of defined slot polygons against YOLO detections.
        :param slots: List of slot definitions containing 'id', 'polygon': [[x,y],...]
        :param detections: List of YOLO detection dictionaries
        :return: Analyzed slot list with status and diagnostic metadata
        """
        analyzed_slots = []

        # Convert detections to Shapely polygons and bottom contact points
        det_objects = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            poly = box(x1, y1, x2, y2)
            bottom_pt = Point(det["bottom_center"][0], det["bottom_center"][1])
            center_pt = Point(det["center"][0], det["center"][1])
            det_objects.append({
                "det": det,
                "poly": poly,
                "area": poly.area,
                "bottom_pt": bottom_pt,
                "center_pt": center_pt
            })

        for slot in slots:
            slot_id = slot.get("id", "Unknown")
            slot_poly_coords = slot["polygon"]
            slot_shapely = Polygon(slot_poly_coords)
            slot_area = slot_shapely.area if slot_shapely.is_valid and slot_shapely.area > 0 else 1.0

            status = SlotStatus.AVAILABLE
            occupied_by = None
            blocked_reason = None
            max_overlap_ratio = 0.0
            matched_detection = None

            # First priority check: Vehicles inside or overlapping the slot
            for obj in det_objects:
                det = obj["det"]
                category = det["category"]
                cls_name = det["class_name"]

                if not slot_shapely.is_valid or not obj["poly"].is_valid:
                    continue

                if slot_shapely.intersects(obj["poly"]):
                    intersection_area = slot_shapely.intersection(obj["poly"]).area
                    slot_overlap = intersection_area / slot_area
                    obj_inside_ratio = intersection_area / obj["area"]

                    # Check if bottom ground contact point is inside slot
                    contact_inside = slot_shapely.contains(obj["bottom_pt"]) or slot_shapely.contains(obj["center_pt"])

                    if category == "vehicle":
                        if slot_overlap > self.vehicle_iou_threshold or (contact_inside and obj_inside_ratio > 0.3):
                            if slot_overlap > max_overlap_ratio:
                                max_overlap_ratio = slot_overlap
                                status = SlotStatus.OCCUPIED
                                occupied_by = f"{cls_name.capitalize()} ({det['confidence']*100:.0f}%)"
                                matched_detection = det

            # Second priority check: Obstacles (people, bikes, traffic cones) blocking the slot
            if status != SlotStatus.OCCUPIED:
                for obj in det_objects:
                    det = obj["det"]
                    category = det["category"]
                    cls_name = det["class_name"]

                    if category == "obstacle" or cls_name in {"bicycle", "person", "stop sign"}:
                        if slot_shapely.intersects(obj["poly"]):
                            intersection_area = slot_shapely.intersection(obj["poly"]).area
                            slot_overlap = intersection_area / slot_area
                            contact_inside = slot_shapely.contains(obj["bottom_pt"]) or slot_shapely.contains(obj["center_pt"])

                            if slot_overlap > self.obstacle_iou_threshold or contact_inside:
                                status = SlotStatus.BLOCKED
                                blocked_reason = f"Blocked by {cls_name} ({det['confidence']*100:.0f}%)"
                                matched_detection = det
                                max_overlap_ratio = max(max_overlap_ratio, slot_overlap)
                                break

            # Color coding according to requirements:
            # 🟢 Available / 🔴 Occupied / 🟡 Blocked
            if status == SlotStatus.AVAILABLE:
                color_hex = "#22c55e"
                color_bgr = (94, 197, 34)
                status_icon = "🟢"
            elif status == SlotStatus.OCCUPIED:
                color_hex = "#ef4444"
                color_bgr = (68, 68, 239)
                status_icon = "🔴"
            else:
                color_hex = "#eab308"
                color_bgr = (8, 179, 234)
                status_icon = "🟡"

            analyzed_slots.append({
                "id": slot_id,
                "label": slot.get("label", f"Bay {slot_id}"),
                "status": status,
                "status_icon": status_icon,
                "color_hex": color_hex,
                "color_bgr": color_bgr,
                "occupied_by": occupied_by,
                "blocked_reason": blocked_reason,
                "overlap_ratio": round(max_overlap_ratio, 3),
                "matched_detection": matched_detection,
                "polygon": slot_poly_coords,
                "custom_metadata": slot.get("custom_metadata", {})
            })

        return analyzed_slots
