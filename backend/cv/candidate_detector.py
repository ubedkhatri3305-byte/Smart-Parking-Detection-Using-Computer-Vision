"""
Dynamic Parking Candidate Detector
==================================
Discovers, projects, and validates candidate parking spaces dynamically from camera imagery.
Implements Sections 6, 7, 8, 10 of the Core Specification:
- Generates candidate regions dynamically from image analysis
- Calculates realistic estimated real-world metric dimensions via camera perspective homography
- NEVER uses hardcoded default rectangles or synthetic coordinates
- Evaluates multi-candidate spaces
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from backend.cv.free_space_analyzer import FreeSpaceAnalyzer
from backend.cv.geometry import ParkingGeometry
from backend.cv.occupancy import ParkingOccupancyAnalyzer, SlotStatus
from backend.cv.vehicle_matcher import VehicleMatcher


class ParkingCandidateDetector:
    """
    Dynamically generates and evaluates candidate parking bays from camera frames.
    """

    def __init__(
        self,
        free_space_analyzer: Optional[FreeSpaceAnalyzer] = None,
        geometry: Optional[ParkingGeometry] = None,
        occupancy_analyzer: Optional[ParkingOccupancyAnalyzer] = None,
        vehicle_matcher: Optional[VehicleMatcher] = None
    ):
        self.free_space_analyzer = free_space_analyzer or FreeSpaceAnalyzer()
        self.geometry = geometry or ParkingGeometry()
        self.occupancy_analyzer = occupancy_analyzer or ParkingOccupancyAnalyzer()
        self.vehicle_matcher = vehicle_matcher or VehicleMatcher()

    def detect_candidates(
        self,
        image: Optional[np.ndarray],
        detections: List[Dict[str, Any]],
        image_shape: Optional[Tuple[int, int]] = None,
        zone_info: Optional[Dict[str, Any]] = None,
        predefined_slots: Optional[List[Dict[str, Any]]] = None,
        user_vehicle_specs: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Dynamically discover and evaluate all candidate parking bays in the scene.
        """
        if isinstance(image_shape, dict) and zone_info is None:
            zone_info = image_shape
            image_shape = None

        if image_shape is None:
            image_shape = image.shape[:2] if image is not None else (480, 640)

        zone_info = zone_info or {}
        h, w = image_shape[:2]
        veh_specs = user_vehicle_specs or self.vehicle_matcher.get_vehicle_specs("car_sedan")
        is_zone_valid = zone_info.get("is_valid", False)

        # 1. Determine candidate spatial regions
        raw_candidates: List[Dict[str, Any]] = []

        if predefined_slots and len(predefined_slots) > 0:
            # Benchmark scenarios (e.g. Scenario 1 aerial 6-bay lot, Scenario 2 driver view)
            raw_candidates = predefined_slots
        else:
            # DYNAMIC CAMERA DETECTION: Discover free spaces from image analysis
            raw_candidates = self.free_space_analyzer.analyze_frame_free_spaces(
                image=image,
                detections=detections,
                image_shape=image_shape,
                zone_info=zone_info
            )

        # If no genuine physical candidates were discovered in the scene, return empty list
        if not raw_candidates:
            return []

        # 2. Calibrate camera homography using detected reference entities and pinhole optics
        cleaned_detections = [
            d for d in detections
            if not ((d["bbox"][2] - d["bbox"][0]) / float(w) > 0.75 and d["bbox"][1] > 0.42 * h)
            and not (d.get("confidence", 1.0) < 0.25 and d["bbox"][1] > 0.50 * h)
        ]
        self.geometry.calibrate_from_camera_and_detections(image_shape, cleaned_detections)

        # 3. Evaluate physical occupancy and obstacle intersections using Shapely
        evaluated_slots = self.occupancy_analyzer.evaluate_slots(raw_candidates, cleaned_detections)

        # 4. Compute estimated real-world metric dimensions and match vehicle physical footprint
        processed_candidates = []
        for s in evaluated_slots:
            poly = s["polygon"]
            # Estimate physical dimensions from projective ground plane
            metrics = self.geometry.compute_slot_metric_dimensions(poly)
            s["metrics"] = metrics
            s["width_m"] = metrics["width_m"]
            s["length_m"] = metrics["length_m"]
            s["width_ft"] = metrics["width_ft"]
            s["length_ft"] = metrics["length_ft"]
            s["dims_ft"] = metrics["dims_ft"]
            s["dims_m"] = metrics["dims_m"]

            # Physical fit check against the user's specific vehicle
            s["vehicle_fit"] = self.vehicle_matcher.evaluate_fit(metrics, veh_specs)

            # Check if an obstacle or person blocks the space
            if s.get("blocked_reason"):
                s["status"] = SlotStatus.BLOCKED
                s["vehicle_fit"]["is_suitable"] = False
                s["vehicle_fit"]["fit_badge"] = "⚠️ Blocked"
                s["vehicle_fit"]["message"] = f"Blocked by {s['blocked_reason']}. Space is not clear."
            elif not is_zone_valid and zone_info.get("is_indoor", False):
                s["status"] = SlotStatus.BLOCKED
                s["vehicle_fit"]["is_suitable"] = False
                s["vehicle_fit"]["fit_badge"] = "🏠 Indoor Space"
                s["vehicle_fit"]["message"] = "Indoor space detected. Point camera at an outdoor parking area."

            processed_candidates.append(s)

        return processed_candidates
