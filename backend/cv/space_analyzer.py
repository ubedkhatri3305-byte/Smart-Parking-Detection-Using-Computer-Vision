"""
Parking Space Analyzer
======================
Analyzes candidate parking regions (Section 3).
Evaluates:
- Whether parking boundaries/markings exist (Mode A: Marked vs Mode B: Unmarked)
- Whether the region is physically free or occupied by other vehicles
- Whether obstacles/pedestrians/hazards block the region
- Metric dimensions (length & width) and perspective distortion
- Sufficient usable free clearance for the user's specific vehicle
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from shapely.geometry import Polygon, Point, box
from backend.cv.geometry import ParkingGeometry
from backend.cv.occupancy import ParkingOccupancyAnalyzer, SlotStatus
from backend.cv.vehicle_matcher import VehicleMatcher


class ParkingSpaceAnalyzer:
    """
    Evaluates candidate spatial regions, marks boundaries, checks physical occupancy,
    and calculates metric fit against user vehicle specs.
    """

    def __init__(
        self,
        geometry: Optional[ParkingGeometry] = None,
        occupancy_analyzer: Optional[ParkingOccupancyAnalyzer] = None,
        vehicle_matcher: Optional[VehicleMatcher] = None
    ):
        self.geom = geometry or ParkingGeometry()
        self.occupancy_analyzer = occupancy_analyzer or ParkingOccupancyAnalyzer()
        self.vehicle_matcher = vehicle_matcher or VehicleMatcher()

    def analyze_spaces(
        self,
        image_shape: Tuple[int, int],
        detections: List[Dict[str, Any]],
        zone_info: Dict[str, Any],
        predefined_slots: Optional[List[Dict[str, Any]]] = None,
        vehicle_specs: Optional[Dict[str, Any]] = None,
        parking_mode: str = "auto"
    ) -> List[Dict[str, Any]]:
        """
        Analyze all candidate spaces in view.
        :param image_shape: (height, width) of camera frame
        :param detections: List of YOLO detection dictionaries
        :param zone_info: Output from ParkingZoneValidator
        :param predefined_slots: Slots defined in scenario or parking lot database
        :param vehicle_specs: Target vehicle dimensions and tolerances
        :param parking_mode: 'marked', 'unmarked', or 'auto'
        :return: List of evaluated space dictionaries
        """
        h, w = image_shape[:2]
        veh_specs = vehicle_specs or self.vehicle_matcher.get_vehicle_specs("bike_cruiser")
        is_zone_valid = zone_info.get("is_valid", False)
        raw_zc = zone_info.get("zone_class", "unknown_area")
        zc_str = raw_zc.value if hasattr(raw_zc, "value") else str(raw_zc)
        if "." in zc_str:
            zc_str = zc_str.split(".", 1)[-1]
        zone_class = zc_str.lower()

        # Determine slot candidate polygons
        candidate_slots: List[Dict[str, Any]] = []

        if predefined_slots and len(predefined_slots) > 0:
            # Mode: Predefined facility slots (e.g. from known parking lot database or marked scenario)
            candidate_slots = predefined_slots
        elif is_zone_valid and zone_class in ("marked_parking_slot", "parking_lot", "known_public_parking"):
            # Mode A: Authentic marked parking surface - construct perspective slots from ground plane
            y_top = int(h * 0.40)
            y_bot = int(h * 0.94)

            # Filter out ego-vehicle hood / dashboard detections
            cleaned_ground = [
                d for d in detections
                if d["bbox"][3] >= y_top
                and not d.get("is_indoor", False)
                and not ((d["bbox"][2] - d["bbox"][0]) / float(w) > 0.75 and d["bbox"][1] > 0.40 * h)
                and not (d.get("confidence", 1.0) < 0.30 and d["bbox"][1] > 0.50 * h)
            ]

            if not cleaned_ground:
                candidate_slots = [
                    {
                        "id": "Slot 1 (Marked Bay)",
                        "label": "Marked Bay 1",
                        "polygon": [[int(w * 0.20), y_top], [int(w * 0.80), y_top], [int(w * 0.88), y_bot], [int(w * 0.12), y_bot]],
                        "rule_zone": "registered"
                    }
                ]
            else:
                candidate_slots = self._segment_corridors(w, h, y_top, y_bot, cleaned_ground)
        elif is_zone_valid and zone_class == "designated_roadside":
            # Mode B: Validated roadside parking row with infrastructure
            y_top = int(h * 0.45)
            y_bot = int(h * 0.94)
            cleaned_ground = [
                d for d in detections
                if d["bbox"][3] >= y_top
                and not d.get("is_indoor", False)
                and not ((d["bbox"][2] - d["bbox"][0]) / float(w) > 0.75 and d["bbox"][1] > 0.40 * h)
                and not (d.get("confidence", 1.0) < 0.30 and d["bbox"][1] > 0.50 * h)
            ]
            candidate_slots = self._segment_corridors(w, h, y_top, y_bot, cleaned_ground)
        else:
            # Mode C: When zone is NOT verified/valid (wall, screen, domestic floor, field, unclassified area)
            # NEVER synthesize a fake slot! Only segment corridors if genuine parked vehicles are visible in the scene!
            y_top = int(h * 0.45)
            y_bot = int(h * 0.94)
            cleaned_ground = [
                d for d in detections
                if d["bbox"][3] >= y_top
                and not d.get("is_indoor", False)
                and not ((d["bbox"][2] - d["bbox"][0]) / float(w) > 0.75 and d["bbox"][1] > 0.40 * h)
                and not (d.get("confidence", 1.0) < 0.30 and d["bbox"][1] > 0.50 * h)
            ]
            veh_count = len([d for d in cleaned_ground if d.get("is_vehicle") or d.get("class_name", "").lower() in ("car", "motorcycle", "bus", "truck", "van")])
            if is_zone_valid and veh_count >= 2:
                candidate_slots = self._segment_corridors(w, h, y_top, y_bot, cleaned_ground)
            else:
                candidate_slots = []

        # Filter out ego-vehicle hood from detections passed to occupancy evaluation
        cleaned_detections = [
            d for d in detections
            if not ((d["bbox"][2] - d["bbox"][0]) / float(w) > 0.75 and d["bbox"][1] > 0.40 * h)
            and not (d.get("confidence", 1.0) < 0.30 and d["bbox"][1] > 0.50 * h)
        ]

        if not candidate_slots:
            return []

        # Calibrate real camera pinhole homography and photogrammetry scale
        self.geom.calibrate_from_camera_and_detections(image_shape, cleaned_detections)

        # Run occupancy and vehicle fit evaluation
        evaluated_slots = self.occupancy_analyzer.evaluate_slots(candidate_slots, cleaned_detections)

        for s in evaluated_slots:
            # 1. Compute physically-grounded metric dimensions using calibrated ground homography
            s["metrics"] = self.geom.compute_slot_metric_dimensions(s["polygon"])
            # 2. Evaluate physical vehicle fit against user vehicle
            s["vehicle_fit"] = self.vehicle_matcher.evaluate_fit(s["metrics"], veh_specs)
            # 3. Check for obstacle / pedestrian blockers
            if s.get("blocked_reason"):
                s["status"] = SlotStatus.BLOCKED
                s["vehicle_fit"]["is_suitable"] = False
                s["vehicle_fit"]["fit_badge"] = "⚠️ Blocked"
                s["vehicle_fit"]["message"] = f"Blocked by {s['blocked_reason']}. Clear space before parking."
            elif not is_zone_valid and zone_info.get("is_indoor", False):
                s["status"] = SlotStatus.BLOCKED
                s["vehicle_fit"]["is_suitable"] = False
                s["vehicle_fit"]["fit_badge"] = "🏠 Indoor Space"
                s["vehicle_fit"]["message"] = "Indoor space detected. Point camera at an outdoor parking area."

        return evaluated_slots

    def _segment_corridors(
        self,
        w: int,
        h: int,
        y_top: int,
        y_bot: int,
        ground_objects: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Dynamically segment ground corridors between detected vehicles/obstacles.
        """
        # Exclude ego vehicle hood boxes
        cleaned_objects = [
            o for o in ground_objects
            if not ((o["bbox"][2] - o["bbox"][0]) / float(w) > 0.75 and o["bbox"][1] > 0.40 * h)
            and not (o.get("confidence", 1.0) < 0.30 and o["bbox"][1] > 0.50 * h)
        ]
        cleaned_objects.sort(key=lambda o: (o["bbox"][0] + o["bbox"][2]) / 2.0)
        last_x_norm = 0.04
        bay_idx = 1
        bays = []

        for obj in cleaned_objects:
            x1, y1, x2, y2 = obj["bbox"]
            x1_norm = max(0.04, min(0.96, x1 / w))
            x2_norm = max(0.04, min(0.96, x2 / w))
            obj_name = obj.get("class_name", "Obstacle").capitalize()
            is_obs = obj.get("is_obstacle", False)

            # Usable open corridor before this obstacle/vehicle
            if (x1_norm - last_x_norm) >= 0.16:
                bays.append({
                    "id": f"Bay {bay_idx}",
                    "label": f"Bay {bay_idx} (Clear Space)",
                    "span": (round(last_x_norm, 2), round(x1_norm, 2)),
                    "status": "AVAILABLE",
                    "blocked_by": None
                })
                bay_idx += 1

            # Occupied/blocked space
            bays.append({
                "id": f"Zone {bay_idx}",
                "label": f"Zone {bay_idx} ({'Obstacle' if is_obs else 'Vehicle'})",
                "span": (round(x1_norm, 2), round(x2_norm, 2)),
                "status": "BLOCKED" if is_obs else "OCCUPIED",
                "blocked_by": f"{obj_name} ({int(obj.get('confidence', 0.85)*100)}%)"
            })
            bay_idx += 1
            last_x_norm = x2_norm

        # Usable open corridor after last object
        if (0.96 - last_x_norm) >= 0.16:
            bays.append({
                "id": f"Bay {bay_idx}",
                "label": f"Bay {bay_idx} (Clear Space)",
                "span": (round(last_x_norm, 2), 0.96),
                "status": "AVAILABLE",
                "blocked_by": None
            })

        slot_definitions = []
        for b in bays:
            x_start, x_end = b["span"]
            center_x = (x_start + x_end) / 2.0
            width = x_end - x_start
            top_w = width * 0.84
            top_x1 = max(0.02, center_x - top_w / 2.0)
            top_x2 = min(0.98, center_x + top_w / 2.0)

            poly = [
                [int(top_x1 * w), y_top],
                [int(top_x2 * w), y_top],
                [int(x_end * w), y_bot],
                [int(x_start * w), y_bot]
            ]
            slot_definitions.append({
                "id": b["id"],
                "label": b["label"],
                "polygon": poly,
                "status": b["status"],
                "blocked_reason": b["blocked_by"],
                "rule_zone": "registered"
            })

        return slot_definitions
