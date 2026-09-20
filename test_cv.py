#!/usr/bin/env python3
"""
Smart Parking Detection Using Computer Vision
CLI Demonstration and Coursework Verification Script

Usage:
  python test_cv.py --scenario scenario_1_aerial --vehicle suv
  python test_cv.py --scenario scenario_2_driver --vehicle sedan
  python test_cv.py --scenario scenario_4_tight --vehicle suv
  python test_cv.py --image path/to/custom_image.jpg --vehicle compact
"""

import sys
import os
import argparse
import json
import cv2
import numpy as np

# Ensure backend package is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.cv.yolo_detector import ParkingYOLODetector
from backend.cv.geometry import ParkingGeometry
from backend.cv.occupancy import ParkingOccupancyAnalyzer
from backend.cv.vehicle_matcher import VehicleMatcher, VehicleProfiles
from backend.cv.visualizer import ParkingVisualizer


def load_scenarios_config():
    cfg_path = os.path.join(os.path.dirname(__file__), "backend", "data", "scenarios", "scenarios_config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r") as f:
            return json.load(f).get("scenarios", {})
    return {}


def main():
    parser = argparse.ArgumentParser(description="Smart Parking Computer Vision Analysis Pipeline")
    parser.add_argument("--scenario", type=str, default="scenario_1_aerial",
                        choices=["scenario_1_aerial", "scenario_2_driver", "scenario_3_rooftop", "scenario_4_tight"],
                        help="Pre-configured test scenario key")
    parser.add_argument("--image", type=str, default=None,
                        help="Optional path to a custom parking image")
    parser.add_argument("--vehicle", type=str, default="suv",
                        choices=["suv", "sedan", "compact", "bike", "van"],
                        help="Target vehicle profile to match against detected slots")
    parser.add_argument("--out", type=str, default="output_annotated.jpg",
                        help="Path to save annotated output visualization")
    parser.add_argument("--bev-out", type=str, default="output_bev.jpg",
                        help="Path to save bird's-eye view warped image")
    args = parser.parse_args()

    print("\n" + "=" * 75)
    print("      SMART PARKING DETECTION USING COMPUTER VISION")
    print("          YOLO + Perspective Homography + Occupancy + Fit")
    print("=" * 75)

    scenarios = load_scenarios_config()

    if args.image:
        img_path = args.image
        scenario_data = None
        print(f"[*] Analyzing custom image: {img_path}")
    else:
        scenario_key = args.scenario
        scenario_data = scenarios.get(scenario_key)
        if not scenario_data:
            print(f"[!] Scenario '{scenario_key}' not found in configuration.")
            return
        img_path = scenario_data["image_path"]
        print(f"[*] Scenario: {scenario_data['title']}")
        print(f"[*] Description: {scenario_data['description']}")
        print(f"[*] Image File: {img_path}")

    # 1. Load Image
    image = cv2.imread(img_path)
    if image is None:
        print(f"[!] Error: Could not read image at '{img_path}'")
        return
    h, w = image.shape[:2]
    print(f"[*] Resolution: {w} × {h} pixels")

    # 2. Initialize and Run YOLO
    print("\n" + "-" * 75)
    print(" STEP 2: YOLO Object Detection (Vehicles & Obstacles)")
    print("-" * 75)
    detector = ParkingYOLODetector(conf_threshold=0.25)
    detections = detector.detect(image)
    print(f"[*] Total Objects Detected: {len(detections)}")

    vehicles_detected = [d for d in detections if d["category"] == "vehicle"]
    obstacles_detected = [d for d in detections if d["category"] == "obstacle"]

    print(f"    - Vehicles (Cars/Trucks/Bikes): {len(vehicles_detected)}")
    print(f"    - Obstacles (Pedestrians/Bicycles/Cones): {len(obstacles_detected)}")
    for d in detections:
        print(f"      • {d['class_name'].upper():<12} conf: {d['confidence']*100:.1f}%  bbox: {d['bbox']}")

    # 3. Geometry & Homography Matrix
    print("\n" + "-" * 75)
    print(" STEP 4: Camera Geometry & Perspective Homography Transform")
    print("-" * 75)
    if scenario_data and "homography" in scenario_data:
        h_cfg = scenario_data["homography"]
        geom = ParkingGeometry(
            src_points=h_cfg["src_points"],
            ground_size_meters=tuple(h_cfg["ground_size_meters"]),
            bev_resolution=tuple(h_cfg["bev_resolution"])
        )
        print("[*] Computed 3x3 Projective Homography Matrix H:")
        for row in geom.H:
            print(f"    [ {row[0]:11.4e}  {row[1]:11.4e}  {row[2]:11.4e} ]")

        # Generate Bird's-Eye View
        bev_image = geom.warp_to_bird_eye_view(image)
        if bev_image is not None:
            cv2.imwrite(args.bev_out, bev_image)
            print(f"[*] Bird's-Eye View (BEV) orthographic projection saved to: {args.bev_out}")
    else:
        # Fallback default geometry
        geom = ParkingGeometry()
        print("[*] Using default calibrated ground-plane geometry.")

    # 4. Slot Occupancy Analysis
    print("\n" + "-" * 75)
    print(" STEP 4: Parking Space Occupancy Analysis")
    print("-" * 75)
    if scenario_data and "slots" in scenario_data:
        slot_definitions = scenario_data["slots"]
    else:
        # Generate default slots across middle if not defined
        slot_definitions = [
            {"id": "A1", "label": "Slot A1", "polygon": [[int(w*0.1), int(h*0.4)], [int(w*0.35), int(h*0.4)], [int(w*0.35), int(h*0.8)], [int(w*0.1), int(h*0.8)]]},
            {"id": "A2", "label": "Slot A2", "polygon": [[int(w*0.38), int(h*0.4)], [int(w*0.63), int(h*0.4)], [int(w*0.63), int(h*0.8)], [int(w*0.38), int(h*0.8)]]},
            {"id": "A3", "label": "Slot A3", "polygon": [[int(w*0.66), int(h*0.4)], [int(w*0.9), int(h*0.4)], [int(w*0.9), int(h*0.8)], [int(w*0.66), int(h*0.8)]]}
        ]

    analyzer = ParkingOccupancyAnalyzer()
    analyzed_slots = analyzer.evaluate_slots(slot_definitions, detections)

    # Attach metric dimensions to each slot
    for s in analyzed_slots:
        s["metrics"] = geom.compute_slot_metric_dimensions(s["polygon"])

    # 5. Vehicle Matching (Step 5)
    print("\n" + "-" * 75)
    print(f" STEP 5: Vehicle Dimension Matching for '{args.vehicle.upper()}'")
    print("-" * 75)
    matcher = VehicleMatcher()
    veh_specs = matcher.get_vehicle_specs(args.vehicle)
    print(f"[*] Selected Vehicle: {veh_specs['name']} ({veh_specs['icon']})")
    print(f"    Required Dimensions: {veh_specs['length_m']}m (L) × {veh_specs['width_m']}m (W)")
    print(f"    Door Opening Clearance: ±{veh_specs['door_clearance_m']}m")

    for s in analyzed_slots:
        fit = matcher.evaluate_fit(s["metrics"], veh_specs)
        s["vehicle_fit"] = fit

    # Print Table
    print("\n" + "=" * 90)
    print(f"{'SLOT ID':<10} | {'STATUS':<14} | {'DIMENSIONS (W×L)':<18} | {'VEHICLE SUITABILITY':<25} | {'DETAILS':<18}")
    print("-" * 90)

    recommended_slot = None

    for s in analyzed_slots:
        m = s["metrics"]
        dims_str = f"{m['width_m']:.1f}m × {m['length_m']:.1f}m"
        status_str = f"{s['status_icon']} {s['status']}"

        if s["status"] == "AVAILABLE":
            fit = s["vehicle_fit"]
            fit_str = fit["fit_badge"]
            details = f"Clearance: +{fit['width_margin_m']}m"
            if fit["is_suitable"] and recommended_slot is None:
                recommended_slot = s
        elif s["status"] == "OCCUPIED":
            fit_str = "—"
            details = s.get("occupied_by") or "Vehicle parked"
        else:  # BLOCKED
            fit_str = "—"
            details = s.get("blocked_reason") or "Obstacle present"

        print(f"{s['label']:<10} | {status_str:<14} | {dims_str:<18} | {fit_str:<25} | {details:<18}")

    print("=" * 90)

    # Summary and Recommendation
    avail_count = sum(1 for s in analyzed_slots if s["status"] == "AVAILABLE")
    occ_count = sum(1 for s in analyzed_slots if s["status"] == "OCCUPIED")
    block_count = sum(1 for s in analyzed_slots if s["status"] == "BLOCKED")

    print(f"\n[SUMMARY] Total Slots: {len(analyzed_slots)} | 🟢 Available: {avail_count} | 🔴 Occupied: {occ_count} | 🟡 Blocked: {block_count}")

    if recommended_slot:
        print("\n" + "★" * 75)
        print(f" ★ RECOMMENDED PARKING SPACE: {recommended_slot['label']} ★")
        print(f"   Status: 🟢 Available")
        print(f"   Dimensions: {recommended_slot['metrics']['width_m']}m (Width) × {recommended_slot['metrics']['length_m']}m (Length)")
        print(f"   Suitability: {recommended_slot['vehicle_fit']['fit_badge']}")
        print(f"   Guidance: {recommended_slot['vehicle_fit']['message']}")
        print("★" * 75)
    else:
        print("\n[!] No suitable parking spaces currently available for this vehicle profile.")

    # 6. Render Visual Annotations
    annotated_img = ParkingVisualizer.annotate_frame(
        image=image,
        analyzed_slots=analyzed_slots,
        detections=detections,
        vehicle_name=veh_specs["name"]
    )
    cv2.imwrite(args.out, annotated_img)
    print(f"\n[✓] Annotated visual output saved to: {args.out}")


if __name__ == "__main__":
    main()
