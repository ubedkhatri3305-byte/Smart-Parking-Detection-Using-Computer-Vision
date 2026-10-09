"""
Validation test script for ParkVision AI Open Parking Area Fixes
Verifies all 7 conditions requested in the urgent bug fix prompt.
"""

import os
import sys
import numpy as np
import cv2

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.cv.zone_validator import ParkingZoneValidator, ZoneClass, ZoneStatus
from backend.cv.space_analyzer import ParkingSpaceAnalyzer
from backend.cv.decision_engine import ParkingDecisionEngine, DecisionState
from backend.cv.confidence_scorer import ParkingConfidenceScorer
from backend.cv.vehicle_matcher import VehicleMatcher


def run_tests():
    print("=" * 80)
    print("PARKVISION AI — VERIFICATION TEST SUITE: OPEN PARKING AREA FIX")
    print("=" * 80)
    
    zone_val = ParkingZoneValidator()
    space_ana = ParkingSpaceAnalyzer()
    dec_eng = ParkingDecisionEngine()
    matcher = VehicleMatcher()
    
    veh_specs = matcher.get_vehicle_specs("bike_cruiser", custom_length=2.15, custom_width=0.85, custom_name="Royal Enfield Classic 350")
    
    # -------------------------------------------------------------------------
    # TEST 1: Sunlit outdoor concrete pavement (high luminance, low saturation)
    # -------------------------------------------------------------------------
    # Create synthetic sunlit concrete image (mean_v ~ 180, std ~ 15, lap_var ~ 25)
    img_h, img_w = 480, 640
    np.random.seed(42)
    noise = np.random.normal(0, 12, (img_h, img_w)).astype(np.float32)
    concrete_base = np.clip(180 + noise, 0, 255).astype(np.uint8)
    concrete_img = cv2.merge([concrete_base, concrete_base, concrete_base])
    
    z_res = zone_val.validate_zone(concrete_img, detections=[], map_context={})
    print(f"\n[Test 1] Sunlit Outdoor Concrete Classification:")
    print(f"  Zone Class: {z_res['zone_class']}")
    print(f"  Status: {z_res['status']}")
    print(f"  Is Valid/Open: {z_res.get('is_open_paved_ground', False) or z_res['is_valid']}")
    assert z_res['zone_class'] in (ZoneClass.UNMARKED_PAVED_GROUND, ZoneClass.UNKNOWN), f"Wrong class: {z_res['zone_class']}"
    print("  --> PASS: Concrete pavement is NOT rejected as domestic interior floor [✓]")
    
    # -------------------------------------------------------------------------
    # TEST 2: Candidate space generation on unmarked open ground
    # -------------------------------------------------------------------------
    candidates = space_ana.analyze_spaces(
        image_shape=(img_h, img_w),
        detections=[],
        zone_info=z_res,
        vehicle_specs=veh_specs,
        parking_mode="unmarked",
        image=concrete_img
    )
    print(f"\n[Test 2] Open Ground Candidate Space Generation:")
    print(f"  Detected candidates: {len(candidates)}")
    assert len(candidates) >= 1, "Failed to generate candidate space for open paved ground"
    cand0 = candidates[0]
    print(f"  Candidate Label: {cand0['label']}")
    print(f"  Candidate Length: {cand0['length_m']}m ({cand0['metrics']['length_ft']} ft)")
    print(f"  Candidate Width: {cand0['metrics']['width_m']}m ({cand0['metrics']['width_ft']} ft)")
    assert cand0['source'] == "unmarked_open_ground", f"Expected unmarked_open_ground, got {cand0['source']}"
    print("  --> PASS: Ground region perspective polygon generated [✓]")
    
    # -------------------------------------------------------------------------
    # TEST 3: Decision Engine on unmarked open ground (Permission Unverified)
    # -------------------------------------------------------------------------
    candidates[0]["metrics"]["calibration_verified"] = True
    dec_res = dec_eng.evaluate_decision(
        candidate_spaces=candidates,
        user_vehicle_specs=veh_specs,
        zone_info=z_res,
        detections=[],
        permission_info={"can_park_legally": False, "is_unknown": True, "is_prohibited": False}
    )
    print(f"\n[Test 3] Decision Engine Status Separation:")
    print(f"  Decision: {dec_res['decision']}")
    print(f"  Detailed Status: {dec_res['detailed_status']}")
    print(f"  Headline: {dec_res['headline']}")
    print(f"  Reason: {dec_res['reason']}")
    assert dec_res['decision'] == DecisionState.UNCERTAIN, f"Expected UNCERTAIN, got {dec_res['decision']}"
    assert dec_res['detailed_status'] == "VEHICLE FIT VERIFIED", f"Expected VEHICLE FIT VERIFIED, got {dec_res['detailed_status']}"
    assert dec_res['headline'] == "PHYSICALLY SUITABLE — PARKING PERMISSION UNVERIFIED", f"Unexpected headline: {dec_res['headline']}"
    print("  --> PASS: Output matches 'PHYSICALLY SUITABLE — PARKING PERMISSION UNVERIFIED' [✓]")
    
    # -------------------------------------------------------------------------
    # TEST 4: Peripheral Obstacle / Pedestrian Isolation (Not blocking space)
    # -------------------------------------------------------------------------
    # Pedestrian on far left (x: 20 to 80), corridor is (x: 128 to 512)
    distant_person = {
        "class_name": "person",
        "confidence": 0.88,
        "is_person": True,
        "is_vehicle": False,
        "is_obstacle": False,
        "bbox": [20, 100, 80, 260],
        "normalized_bbox": [20/img_w, 100/img_h, 60/img_w, 160/img_h]
    }
    candidates_with_ped = space_ana.analyze_spaces(
        image_shape=(img_h, img_w),
        detections=[distant_person],
        zone_info=z_res,
        vehicle_specs=veh_specs,
        parking_mode="unmarked",
        image=concrete_img
    )
    dec_res_ped = dec_eng.evaluate_decision(
        candidate_spaces=candidates_with_ped,
        user_vehicle_specs=veh_specs,
        zone_info=z_res,
        detections=[distant_person],
        permission_info={"can_park_legally": False, "is_unknown": True, "is_prohibited": False}
    )
    print(f"\n[Test 4] Peripheral Pedestrian Outside Ground Space:")
    print(f"  Detailed Status: {dec_res_ped['detailed_status']}")
    print(f"  Headline: {dec_res_ped['headline']}")
    assert dec_res_ped['detailed_status'] == "VEHICLE FIT VERIFIED", f"Expected VEHICLE FIT VERIFIED, got {dec_res_ped['detailed_status']}"
    assert "SPACE BLOCKED" not in dec_res_ped['headline'], f"Pedestrian incorrectly blocked space: {dec_res_ped['headline']}"
    print("  --> PASS: Peripheral entity does NOT block the open parking space [✓]")
    
    # -------------------------------------------------------------------------
    # TEST 5: Direct In-Space Obstacle (Should reject with BLOCKED BY OBSTACLE)
    # -------------------------------------------------------------------------
    in_space_barrier = {
        "class_name": "traffic cone",
        "confidence": 0.95,
        "is_obstacle": True,
        "is_person": False,
        "is_vehicle": False,
        "bbox": [280, 300, 360, 420]  # Directly in center of corridor
    }
    candidates_with_obs = space_ana.analyze_spaces(
        image_shape=(img_h, img_w),
        detections=[in_space_barrier],
        zone_info=z_res,
        vehicle_specs=veh_specs,
        parking_mode="unmarked",
        image=concrete_img
    )
    dec_res_obs = dec_eng.evaluate_decision(
        candidate_spaces=candidates_with_obs,
        user_vehicle_specs=veh_specs,
        zone_info=z_res,
        detections=[in_space_barrier],
        permission_info={"can_park_legally": False, "is_unknown": True}
    )
    print(f"\n[Test 5] Direct In-Space Obstacle:")
    print(f"  Decision: {dec_res_obs['decision']}")
    print(f"  Headline: {dec_res_obs['headline']}")
    assert dec_res_obs['decision'] == DecisionState.NOT_SUITABLE, f"Expected NOT_SUITABLE, got {dec_res_obs['decision']}"
    assert "BLOCKED" in dec_res_obs['headline'], f"Expected BLOCKED in headline, got {dec_res_obs['headline']}"
    print("  --> PASS: Space blocked by obstacle correctly rejects with NOT SUITABLE [✓]")
    
    # -------------------------------------------------------------------------
    # TEST 6: Space Too Small for Large Vehicle (e.g. Bus or Large Truck)
    # -------------------------------------------------------------------------
    truck_specs = {"name": "Large Truck", "length_m": 8.50, "width_m": 2.80}
    dec_res_small = dec_eng.evaluate_decision(
        candidate_spaces=candidates,
        user_vehicle_specs=truck_specs,
        zone_info=z_res,
        detections=[],
        permission_info={"can_park_legally": True, "is_unknown": False}
    )
    print(f"\n[Test 6] Vehicle Dimensions Exceed Available Space:")
    print(f"  Decision: {dec_res_small['decision']}")
    print(f"  Headline: {dec_res_small['headline']}")
    assert dec_res_small['decision'] == DecisionState.NOT_SUITABLE, f"Expected NOT_SUITABLE, got {dec_res_small['decision']}"
    assert "SPACE TOO SMALL" in dec_res_small['headline'], f"Expected SPACE TOO SMALL, got {dec_res_small['headline']}"
    print("  --> PASS: Oversized vehicle correctly receives NOT SUITABLE — SPACE TOO SMALL [✓]")

    # -------------------------------------------------------------------------
    # TEST 7: Uncalibrated Open Ground (Fit Not Verified)
    # -------------------------------------------------------------------------
    uncal_cand = [dict(cand0)]
    uncal_cand[0]["metrics"] = dict(cand0["metrics"])
    uncal_cand[0]["metrics"]["calibration_verified"] = False
    dec_res_uncal = dec_eng.evaluate_decision(
        candidate_spaces=uncal_cand,
        user_vehicle_specs=veh_specs,
        zone_info=z_res,
        detections=[],
        permission_info={"can_park_legally": False, "is_unknown": True}
    )
    print(f"\n[Test 7] Uncalibrated Open Ground Dimensions:")
    print(f"  Decision: {dec_res_uncal['decision']}")
    print(f"  Headline: {dec_res_uncal['headline']}")
    print(f"  Detailed Status: {dec_res_uncal['detailed_status']}")
    assert dec_res_uncal['decision'] == DecisionState.UNCERTAIN
    assert dec_res_uncal['headline'] == "OPEN AREA DETECTED — VEHICLE FIT NOT VERIFIED"
    assert dec_res_uncal['detailed_status'] == "OPEN AREA DETECTED"
    print("  --> PASS: Uncalibrated dimensions produce 'OPEN AREA DETECTED — VEHICLE FIT NOT VERIFIED' [✓]")

    print("\n" + "=" * 80)
    print("ALL 7 VERIFICATION CRITERIA PASSED WITH ZERO ERRORS [✓]")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
