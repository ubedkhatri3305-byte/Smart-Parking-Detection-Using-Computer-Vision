"""
Comprehensive Test Suite for Core Parking Detection Architecture
=================================================================
Verifies all 11 explicit test cases required in Section 18:

1. Empty home floor                      -> NOT SUITABLE
2. Empty house driveway                  -> UNCERTAIN / NOT SUITABLE
3. Empty garden                          -> NOT SUITABLE
4. Empty field                           -> NOT SUITABLE
5. Empty footpath                        -> NOT SUITABLE
6. Empty road / traffic lane             -> NOT SUITABLE / UNCERTAIN
7. Empty marked parking slot             -> SUITABLE
8. Occupied parking slot                 -> NOT SUITABLE
9. Parking slot with obstacle            -> NOT SUITABLE
10. Known public parking with empty slot -> SUITABLE
11. Unknown roadside space               -> UNCERTAIN

Enforces: EMPTY SPACE != PARKING SPACE.
"""

import unittest
import numpy as np
import cv2
from typing import Dict, Any, List, Optional

from backend.cv.zone_validator import ParkingZoneValidator, ZoneClass, ZoneStatus
from backend.cv.space_analyzer import ParkingSpaceAnalyzer
from backend.cv.confidence_scorer import ParkingConfidenceScorer, DecisionState
from backend.cv.temporal_tracker import TemporalParkingTracker
from backend.cv.vehicle_matcher import VehicleMatcher


class TestCoreParkingPipeline(unittest.TestCase):
    def setUp(self):
        self.validator = ParkingZoneValidator()
        self.space_analyzer = ParkingSpaceAnalyzer()
        self.matcher = VehicleMatcher()
        self.bike_specs = self.matcher.get_vehicle_specs("bike_cruiser", 2.15, 0.85, "Royal Enfield 350")
        self.car_specs = self.matcher.get_vehicle_specs("suv", 4.75, 1.90, "Hyundai Creta")

    # -------------------------------------------------------------
    # 1. Empty Home Floor -> NOT SUITABLE
    # -------------------------------------------------------------
    def test_01_empty_home_floor(self):
        """Empty floor in a home (e.g. living room with sofa/tv or wooden floor) must NOT be detected as parking."""
        # Simulated detections showing an indoor TV or couch
        detections = [
            {"class_name": "couch", "confidence": 0.91, "bbox": [100, 100, 300, 250], "category": "indoor_object", "is_indoor": True, "bottom_center": (200, 250), "center": (200, 175)},
            {"class_name": "tv", "confidence": 0.88, "bbox": [350, 50, 500, 180], "category": "indoor_object", "is_indoor": True, "bottom_center": (425, 180), "center": (425, 115)}
        ]
        zone = self.validator.validate_zone(None, detections)
        self.assertEqual(zone["status"], ZoneStatus.INVALID)
        self.assertEqual(zone["zone_class"], ZoneClass.HOUSE_FLOOR)

        # Scorer evaluation
        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 5.0, "width_m": 3.0}, self.bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        self.assertEqual(result["decision"], DecisionState.NOT_SUITABLE)
        self.assertFalse(result["can_recommend"])

        # Test 1b: Bare tiled floor image with ZERO YOLO object detections (enforces EMPTY != PARKING)
        bare_tile_img = np.zeros((480, 640, 3), dtype=np.uint8)
        bare_tile_img[:, :] = (210, 210, 210)  # Light interior ceramic/marble floor
        zone_bare = self.validator.validate_zone(bare_tile_img, [])
        self.assertEqual(zone_bare["status"], ZoneStatus.INVALID)
        self.assertEqual(zone_bare["zone_class"], ZoneClass.HOUSE_FLOOR)

        result_bare = ParkingConfidenceScorer.evaluate(
            zone_result=zone_bare,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 5.0, "width_m": 3.0}, self.bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        self.assertEqual(result_bare["decision"], DecisionState.NOT_SUITABLE)
        self.assertFalse(result_bare["can_recommend"])

    # -------------------------------------------------------------
    # 2. Empty House Driveway -> UNCERTAIN / NOT SUITABLE
    # -------------------------------------------------------------
    def test_02_empty_house_driveway(self):
        """Empty private driveway with gate/boundary must NOT be marked as free public parking."""
        detections = [
            {"class_name": "gate", "confidence": 0.85, "bbox": [50, 80, 550, 300], "category": "obstacle", "is_indoor": False, "bottom_center": (300, 300), "center": (300, 190)}
        ]
        map_context = {"is_known_parking": False, "is_private": True}
        zone = self.validator.validate_zone(None, detections, map_context=map_context)
        self.assertEqual(zone["status"], ZoneStatus.INVALID)

        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 5.0, "width_m": 2.5}, self.bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": False, "is_prohibited": True}
        )
        self.assertIn(result["decision"], [DecisionState.NOT_SUITABLE, DecisionState.UNCERTAIN])
        self.assertFalse(result["can_recommend"])

    # -------------------------------------------------------------
    # 3. Empty Garden -> NOT SUITABLE
    # -------------------------------------------------------------
    def test_03_empty_garden(self):
        """Green lawn or garden must be rejected."""
        # Create a green test image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:, :] = (35, 140, 45)  # Green grass BGR
        zone = self.validator.validate_zone(img, [])
        self.assertEqual(zone["status"], ZoneStatus.INVALID)
        self.assertEqual(zone["zone_class"], ZoneClass.GARDEN)

        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 5.0, "width_m": 2.5}, self.bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        self.assertEqual(result["decision"], DecisionState.NOT_SUITABLE)

    # -------------------------------------------------------------
    # 4. Empty Field -> NOT SUITABLE
    # -------------------------------------------------------------
    def test_04_empty_field(self):
        """Unpaved barren dirt field must be rejected."""
        # Create a brown earth test image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:, :] = (30, 80, 110)  # Brown soil BGR
        zone = self.validator.validate_zone(img, [])
        self.assertEqual(zone["status"], ZoneStatus.INVALID)
        self.assertEqual(zone["zone_class"], ZoneClass.FIELD)

        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 6.0, "width_m": 3.0}, self.bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        self.assertEqual(result["decision"], DecisionState.NOT_SUITABLE)

    # -------------------------------------------------------------
    # 5. Empty Footpath -> NOT SUITABLE
    # -------------------------------------------------------------
    def test_05_empty_footpath(self):
        """Pedestrian sidewalk paver area must be rejected."""
        # Grayscale paver texture with high edge density
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:, :] = (180, 180, 180)
        for x in range(0, 640, 20):
            cv2.line(img, (x, 200), (x, 480), (80, 80, 80), 2)
        zone = self.validator.validate_zone(img, [])
        self.assertEqual(zone["status"], ZoneStatus.INVALID)
        self.assertEqual(zone["zone_class"], ZoneClass.FOOTPATH)

        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 4.0, "width_m": 2.0}, self.bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        self.assertEqual(result["decision"], DecisionState.NOT_SUITABLE)

    # -------------------------------------------------------------
    # 6. Empty Road / Traffic Lane -> NOT SUITABLE / UNCERTAIN
    # -------------------------------------------------------------
    def test_06_empty_road_traffic_lane(self):
        """An empty asphalt road lane without marked bays must NOT become a parking space."""
        # Plain asphalt with no bay markings
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:, :] = (70, 70, 70)  # Dark asphalt
        zone = self.validator.validate_zone(img, [], map_context={"is_known_parking": False})
        self.assertIn(zone["status"], [ZoneStatus.INVALID, ZoneStatus.UNKNOWN])

        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 5.0, "width_m": 3.0}, self.bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        self.assertIn(result["decision"], [DecisionState.NOT_SUITABLE, DecisionState.UNCERTAIN])
        self.assertFalse(result["can_recommend"])

    # -------------------------------------------------------------
    # 7. Empty Marked Parking Slot -> SUITABLE
    # -------------------------------------------------------------
    def test_07_empty_marked_parking_slot(self):
        """Marked stall with white lines on asphalt with no obstructions must be SUITABLE."""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        img[:, :] = (65, 65, 65)
        # Draw clear white parking bay stall lines
        cv2.line(img, (150, 200), (100, 470), (255, 255, 255), 6)
        cv2.line(img, (490, 200), (540, 470), (255, 255, 255), 6)
        cv2.line(img, (150, 200), (490, 200), (255, 255, 255), 6)

        zone = self.validator.validate_zone(img, [])
        self.assertEqual(zone["status"], ZoneStatus.VALID)
        self.assertEqual(zone["zone_class"], ZoneClass.MARKED_SLOT)

        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 4.5, "width_m": 2.2}, self.bike_specs),
            permission_info={"can_park_legally": True, "is_unknown": False}
        )
        self.assertEqual(result["decision"], DecisionState.SUITABLE)
        self.assertTrue(result["can_recommend"])

    # -------------------------------------------------------------
    # 8. Occupied Parking Slot -> NOT SUITABLE
    # -------------------------------------------------------------
    def test_08_occupied_parking_slot(self):
        """Marked slot occupied by another vehicle must be NOT SUITABLE."""
        zone = {
            "status": ZoneStatus.VALID,
            "zone_class": ZoneClass.MARKED_SLOT,
            "confidence": 0.95,
            "is_valid": True
        }
        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="OCCUPIED",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 4.5, "width_m": 2.2}, self.bike_specs),
            permission_info={"can_park_legally": True, "is_unknown": False}
        )
        self.assertEqual(result["decision"], DecisionState.NOT_SUITABLE)
        self.assertFalse(result["can_recommend"])

    # -------------------------------------------------------------
    # 9. Parking Slot with Obstacle -> NOT SUITABLE
    # -------------------------------------------------------------
    def test_09_parking_slot_with_obstacle(self):
        """Marked slot blocked by pedestrian, traffic cone, or debris must be NOT SUITABLE."""
        zone = {
            "status": ZoneStatus.VALID,
            "zone_class": ZoneClass.MARKED_SLOT,
            "confidence": 0.92,
            "is_valid": True
        }
        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="BLOCKED",
            obstacle_detected=True,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 4.5, "width_m": 2.2}, self.bike_specs),
            permission_info={"can_park_legally": True, "is_unknown": False},
            blocked_reason="Blocked by traffic cone"
        )
        self.assertEqual(result["decision"], DecisionState.NOT_SUITABLE)
        self.assertFalse(result["can_recommend"])

    # -------------------------------------------------------------
    # 10. Known Public Parking Location with Empty Slot -> SUITABLE
    # -------------------------------------------------------------
    def test_10_known_public_parking_location(self):
        """Location verified in municipal public parking database with clear slot must be SUITABLE."""
        map_context = {
            "is_known_parking": True,
            "type": "public",
            "name": "Central Municipal Bike Stand"
        }
        zone = self.validator.validate_zone(None, [], map_context=map_context)
        self.assertEqual(zone["status"], ZoneStatus.VALID)

        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 3.0, "width_m": 1.5}, self.bike_specs),
            permission_info={"can_park_legally": True, "is_unknown": False}
        )
        self.assertEqual(result["decision"], DecisionState.SUITABLE)
        self.assertTrue(result["can_recommend"])

    # -------------------------------------------------------------
    # 11. Unknown Roadside Space -> UNCERTAIN
    # -------------------------------------------------------------
    def test_11_unknown_roadside_space(self):
        """Unverified roadside area without parking signs or markings must be UNCERTAIN."""
        zone = self.validator.validate_zone(None, [], map_context={"is_known_parking": False})
        self.assertEqual(zone["status"], ZoneStatus.UNKNOWN)

        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=self.matcher.evaluate_fit({"length_m": 5.0, "width_m": 2.5}, self.bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        self.assertEqual(result["decision"], DecisionState.UNCERTAIN)
        self.assertFalse(result["can_recommend"])

    # -------------------------------------------------------------
    # 12. Temporal Stability Tracker
    # -------------------------------------------------------------
    def test_12_temporal_stability(self):
        """Multi-frame consistency must detect frame flickers and flag them as UNCERTAIN."""
        tracker = TemporalParkingTracker(window_size=4)
        
        # Frame 1: SUITABLE
        r1 = tracker.add_frame_result({"decision": "SUITABLE", "confidence_score": 0.88})
        # Frame 2: NOT_SUITABLE (flicker)
        r2 = tracker.add_frame_result({"decision": "NOT_SUITABLE", "confidence_score": 0.30})
        
        # Instability must result in UNCERTAIN
        self.assertEqual(r2["decision"], "UNCERTAIN")
        self.assertFalse(r2["temporal_stable"])

    # -------------------------------------------------------------
    # 13. Camera Pointed at Wall -> NO PARKING / 0 SLOTS
    # -------------------------------------------------------------
    def test_13_camera_on_wall_no_parking(self):
        """Camera pointed at a painted wall must NOT detect parking and must produce 0 slots."""
        wall_white = np.full((480, 640, 3), 215, dtype=np.uint8)
        zone = self.validator.validate_zone(wall_white, [])
        self.assertIn(zone["status"], (ZoneStatus.INVALID, ZoneStatus.UNKNOWN))

        slots = self.space_analyzer.analyze_spaces((480, 640), [], zone, None, self.bike_specs)
        self.assertEqual(len(slots), 0, "No parking bays should be synthesized on a wall.")

        result = ParkingConfidenceScorer.evaluate(
            zone_result=zone,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit={"is_suitable": False, "message": "No delineated slots found."},
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        self.assertIn(result["decision"], (DecisionState.NOT_SUITABLE, DecisionState.UNCERTAIN))
        self.assertFalse(result["can_recommend"])

    # -------------------------------------------------------------
    # 14. Camera Pointed at Laptop Screen -> NO PARKING / 0 SLOTS
    # -------------------------------------------------------------
    def test_14_camera_on_laptop_screen_no_parking(self):
        """Camera pointed at a laptop or monitor screen must NOT detect parking and must produce 0 slots."""
        # 14a. Computer display image
        screen_img = np.zeros((480, 640, 3), dtype=np.uint8)
        screen_img[:] = (190, 110, 45)  # Screen background color
        zone_screen = self.validator.validate_zone(screen_img, [])
        self.assertIn(zone_screen["status"], (ZoneStatus.INVALID, ZoneStatus.UNKNOWN))
        slots_screen = self.space_analyzer.analyze_spaces((480, 640), [], zone_screen, None, self.bike_specs)
        self.assertEqual(len(slots_screen), 0, "No parking bays should be synthesized on a laptop display.")

        # 14b. Laptop detected by YOLO
        dets_laptop = [
            {"class_name": "laptop", "confidence": 0.95, "bbox": [80, 60, 560, 420], "is_indoor": True}
        ]
        zone_laptop = self.validator.validate_zone(None, dets_laptop)
        self.assertEqual(zone_laptop["status"], ZoneStatus.INVALID)
        self.assertEqual(zone_laptop["zone_class"], ZoneClass.HOUSE_FLOOR)
        slots_laptop = self.space_analyzer.analyze_spaces((480, 640), dets_laptop, zone_laptop, None, self.bike_specs)
        self.assertEqual(len(slots_laptop), 0, "No parking bays should be created when laptop is in view.")


class CoreScenarioRunner:
    """
    Executes all 11 Core Scenarios required by Section 18 dynamically
    and returns comprehensive structured results for API, UI, and CLI testing.
    """

    @classmethod
    def run_all_scenarios(cls) -> Dict[str, Any]:
        validator = ParkingZoneValidator()
        matcher = VehicleMatcher()
        bike_specs = matcher.get_vehicle_specs("bike_cruiser", 2.15, 0.85, "Royal Enfield 350")
        results = []

        # 1. Empty Home Floor
        detections_1 = [
            {"class_name": "couch", "confidence": 0.91, "bbox": [100, 100, 300, 250], "category": "indoor_object", "is_indoor": True, "bottom_center": (200, 250), "center": (200, 175)},
            {"class_name": "tv", "confidence": 0.88, "bbox": [350, 50, 500, 180], "category": "indoor_object", "is_indoor": True, "bottom_center": (425, 180), "center": (425, 115)}
        ]
        zone_1 = validator.validate_zone(None, detections_1)
        res_1 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_1,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=matcher.evaluate_fit({"length_m": 5.0, "width_m": 3.0}, bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        passed_1 = (res_1["decision"] == DecisionState.NOT_SUITABLE)
        results.append({
            "id": 1,
            "name": "Empty Home Floor",
            "expected": "NOT_SUITABLE",
            "actual": res_1["decision"],
            "passed": passed_1,
            "confidence_percent": res_1["confidence_percent"],
            "headline": res_1["headline"],
            "reason": res_1["reason"],
            "checklist": res_1["checklist"]
        })

        # 2. Empty House Driveway
        detections_2 = [
            {"class_name": "gate", "confidence": 0.85, "bbox": [50, 80, 550, 300], "category": "obstacle", "is_indoor": False, "bottom_center": (300, 300), "center": (300, 190)}
        ]
        zone_2 = validator.validate_zone(None, detections_2, map_context={"is_known_parking": False, "is_private": True})
        res_2 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_2,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=matcher.evaluate_fit({"length_m": 5.0, "width_m": 2.5}, bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": False, "is_prohibited": True}
        )
        passed_2 = res_2["decision"] in [DecisionState.NOT_SUITABLE, DecisionState.UNCERTAIN]
        results.append({
            "id": 2,
            "name": "Empty House Driveway",
            "expected": "UNCERTAIN / NOT_SUITABLE",
            "actual": res_2["decision"],
            "passed": passed_2,
            "confidence_percent": res_2["confidence_percent"],
            "headline": res_2["headline"],
            "reason": res_2["reason"],
            "checklist": res_2["checklist"]
        })

        # 3. Empty Garden
        img_3 = np.zeros((480, 640, 3), dtype=np.uint8)
        img_3[:, :] = (35, 140, 45)  # Green grass
        zone_3 = validator.validate_zone(img_3, [])
        res_3 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_3,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=matcher.evaluate_fit({"length_m": 5.0, "width_m": 2.5}, bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        passed_3 = (res_3["decision"] == DecisionState.NOT_SUITABLE)
        results.append({
            "id": 3,
            "name": "Empty Garden / Lawn",
            "expected": "NOT_SUITABLE",
            "actual": res_3["decision"],
            "passed": passed_3,
            "confidence_percent": res_3["confidence_percent"],
            "headline": res_3["headline"],
            "reason": res_3["reason"],
            "checklist": res_3["checklist"]
        })

        # 4. Empty Field
        img_4 = np.zeros((480, 640, 3), dtype=np.uint8)
        img_4[:, :] = (30, 80, 110)  # Brown earth
        zone_4 = validator.validate_zone(img_4, [])
        res_4 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_4,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=matcher.evaluate_fit({"length_m": 6.0, "width_m": 3.0}, bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        passed_4 = (res_4["decision"] == DecisionState.NOT_SUITABLE)
        results.append({
            "id": 4,
            "name": "Empty Agricultural Field",
            "expected": "NOT_SUITABLE",
            "actual": res_4["decision"],
            "passed": passed_4,
            "confidence_percent": res_4["confidence_percent"],
            "headline": res_4["headline"],
            "reason": res_4["reason"],
            "checklist": res_4["checklist"]
        })

        # 5. Empty Footpath
        img_5 = np.zeros((480, 640, 3), dtype=np.uint8)
        img_5[:, :] = (180, 180, 180)
        for x in range(0, 640, 20):
            cv2.line(img_5, (x, 200), (x, 480), (80, 80, 80), 2)
        zone_5 = validator.validate_zone(img_5, [])
        res_5 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_5,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=matcher.evaluate_fit({"length_m": 4.0, "width_m": 2.0}, bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        passed_5 = (res_5["decision"] == DecisionState.NOT_SUITABLE)
        results.append({
            "id": 5,
            "name": "Empty Footpath / Sidewalk",
            "expected": "NOT_SUITABLE",
            "actual": res_5["decision"],
            "passed": passed_5,
            "confidence_percent": res_5["confidence_percent"],
            "headline": res_5["headline"],
            "reason": res_5["reason"],
            "checklist": res_5["checklist"]
        })

        # 6. Empty Road / Traffic Lane
        img_6 = np.zeros((480, 640, 3), dtype=np.uint8)
        img_6[:, :] = (70, 70, 70)  # Asphalt
        zone_6 = validator.validate_zone(img_6, [], map_context={"is_known_parking": False})
        res_6 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_6,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=matcher.evaluate_fit({"length_m": 5.0, "width_m": 3.0}, bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        passed_6 = res_6["decision"] in [DecisionState.NOT_SUITABLE, DecisionState.UNCERTAIN]
        results.append({
            "id": 6,
            "name": "Empty Road / Traffic Lane",
            "expected": "NOT_SUITABLE / UNCERTAIN",
            "actual": res_6["decision"],
            "passed": passed_6,
            "confidence_percent": res_6["confidence_percent"],
            "headline": res_6["headline"],
            "reason": res_6["reason"],
            "checklist": res_6["checklist"]
        })

        # 7. Empty Marked Parking Slot
        img_7 = np.zeros((480, 640, 3), dtype=np.uint8)
        img_7[:, :] = (65, 65, 65)
        cv2.line(img_7, (150, 200), (100, 470), (255, 255, 255), 6)
        cv2.line(img_7, (490, 200), (540, 470), (255, 255, 255), 6)
        cv2.line(img_7, (150, 200), (490, 200), (255, 255, 255), 6)
        zone_7 = validator.validate_zone(img_7, [])
        res_7 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_7,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=matcher.evaluate_fit({"length_m": 4.5, "width_m": 2.2}, bike_specs),
            permission_info={"can_park_legally": True, "is_unknown": False}
        )
        passed_7 = (res_7["decision"] == DecisionState.SUITABLE)
        results.append({
            "id": 7,
            "name": "Empty Marked Parking Slot",
            "expected": "SUITABLE",
            "actual": res_7["decision"],
            "passed": passed_7,
            "confidence_percent": res_7["confidence_percent"],
            "headline": res_7["headline"],
            "reason": res_7["reason"],
            "checklist": res_7["checklist"]
        })

        # 8. Occupied Parking Slot
        zone_8 = {"status": ZoneStatus.VALID, "zone_class": ZoneClass.MARKED_SLOT, "confidence": 0.95, "is_valid": True}
        res_8 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_8,
            occupancy_status="OCCUPIED",
            obstacle_detected=False,
            vehicle_fit=matcher.evaluate_fit({"length_m": 4.5, "width_m": 2.2}, bike_specs),
            permission_info={"can_park_legally": True, "is_unknown": False}
        )
        passed_8 = (res_8["decision"] == DecisionState.NOT_SUITABLE)
        results.append({
            "id": 8,
            "name": "Occupied Parking Slot",
            "expected": "NOT_SUITABLE",
            "actual": res_8["decision"],
            "passed": passed_8,
            "confidence_percent": res_8["confidence_percent"],
            "headline": res_8["headline"],
            "reason": res_8["reason"],
            "checklist": res_8["checklist"]
        })

        # 9. Parking Slot with Obstacle
        zone_9 = {"status": ZoneStatus.VALID, "zone_class": ZoneClass.MARKED_SLOT, "confidence": 0.92, "is_valid": True}
        res_9 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_9,
            occupancy_status="BLOCKED",
            obstacle_detected=True,
            vehicle_fit=matcher.evaluate_fit({"length_m": 4.5, "width_m": 2.2}, bike_specs),
            permission_info={"can_park_legally": True, "is_unknown": False},
            blocked_reason="Blocked by ground obstacle"
        )
        passed_9 = (res_9["decision"] == DecisionState.NOT_SUITABLE)
        results.append({
            "id": 9,
            "name": "Parking Slot with Obstacle",
            "expected": "NOT_SUITABLE",
            "actual": res_9["decision"],
            "passed": passed_9,
            "confidence_percent": res_9["confidence_percent"],
            "headline": res_9["headline"],
            "reason": res_9["reason"],
            "checklist": res_9["checklist"]
        })

        # 10. Known Public Parking Location with Empty Slot
        zone_10 = validator.validate_zone(None, [], map_context={"is_known_parking": True, "type": "public", "name": "Municipal Central Stand"})
        res_10 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_10,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=matcher.evaluate_fit({"length_m": 3.0, "width_m": 1.5}, bike_specs),
            permission_info={"can_park_legally": True, "is_unknown": False}
        )
        passed_10 = (res_10["decision"] == DecisionState.SUITABLE)
        results.append({
            "id": 10,
            "name": "Known Public Parking Location",
            "expected": "SUITABLE",
            "actual": res_10["decision"],
            "passed": passed_10,
            "confidence_percent": res_10["confidence_percent"],
            "headline": res_10["headline"],
            "reason": res_10["reason"],
            "checklist": res_10["checklist"]
        })

        # 11. Unknown Roadside Space
        zone_11 = validator.validate_zone(None, [], map_context={"is_known_parking": False})
        res_11 = ParkingConfidenceScorer.evaluate(
            zone_result=zone_11,
            occupancy_status="AVAILABLE",
            obstacle_detected=False,
            vehicle_fit=matcher.evaluate_fit({"length_m": 5.0, "width_m": 2.5}, bike_specs),
            permission_info={"can_park_legally": False, "is_unknown": True}
        )
        passed_11 = (res_11["decision"] == DecisionState.UNCERTAIN)
        results.append({
            "id": 11,
            "name": "Unknown Roadside Space",
            "expected": "UNCERTAIN",
            "actual": res_11["decision"],
            "passed": passed_11,
            "confidence_percent": res_11["confidence_percent"],
            "headline": res_11["headline"],
            "reason": res_11["reason"],
            "checklist": res_11["checklist"]
        })

        all_passed = all(r["passed"] for r in results)
        return {
            "success": True,
            "total_scenarios": len(results),
            "passed_count": sum(1 for r in results if r["passed"]),
            "failed_count": sum(1 for r in results if not r["passed"]),
            "all_passed": all_passed,
            "core_principle": "EMPTY SPACE != PARKING SPACE verified across all 11 scenarios",
            "scenarios": results
        }


if __name__ == "__main__":
    unittest.main()

