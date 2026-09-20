"""
FastAPI Backend Server for Smart Parking Detection System
Connects Computer Vision pipeline, GPS navigation, and Rule Engine with Web Interface.
"""

import os
import io
import base64
import json
from typing import Optional, List, Dict, Any
import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from backend.cv.yolo_detector import ParkingYOLODetector
from backend.cv.geometry import ParkingGeometry
from backend.cv.occupancy import ParkingOccupancyAnalyzer
from backend.cv.vehicle_matcher import VehicleMatcher, VehicleProfiles
from backend.cv.visualizer import ParkingVisualizer
from backend.rules.rule_engine import RuleEngine

app = FastAPI(
    title="Smart Parking Detection API",
    description="Computer Vision, Homography, Occupancy, and Vehicle Matching API",
    version="1.0.0"
)

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCENARIOS_DIR = os.path.join(BASE_DIR, "data", "scenarios")
CONFIG_PATH = os.path.join(SCENARIOS_DIR, "scenarios_config.json")
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

# Initialize global CV modules
detector = ParkingYOLODetector(conf_threshold=0.25)
analyzer = ParkingOccupancyAnalyzer()
matcher = VehicleMatcher()

# Mount scenario images
app.mount("/static/scenarios", StaticFiles(directory=SCENARIOS_DIR), name="scenarios")


def load_scenarios():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f).get("scenarios", {})
    return {}


# GPS Parking Facilities Database (Step 6)
GPS_PARKING_LOCATIONS = [
    {
        "id": "lot-1",
        "name": "Metro Grand Plaza Deck",
        "type": "Multi-Level Covered Deck",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "total_capacity": 120,
        "live_available": 18,
        "distance_km": 0.4,
        "price_per_hr": "$4.50",
        "rule_type": "registered",
        "scenario_key": "scenario_1_aerial",
        "features": ["EV Charging", "Disabled Bays", "Security 24/7"]
    },
    {
        "id": "lot-2",
        "name": "Civic Center Curbside Bays",
        "type": "Public Street Parking",
        "latitude": 37.7785,
        "longitude": -122.4150,
        "total_capacity": 45,
        "live_available": 3,
        "distance_km": 0.8,
        "price_per_hr": "$2.00",
        "rule_type": "public_permitted",
        "scenario_key": "scenario_2_driver",
        "features": ["2-Hour Limit", "Street Level", "Solar Meter"]
    },
    {
        "id": "lot-3",
        "name": "Market Square Rooftop Deck",
        "type": "Elevated Rooftop Lot",
        "latitude": 37.7710,
        "longitude": -122.4230,
        "total_capacity": 80,
        "live_available": 0,
        "distance_km": 1.2,
        "price_per_hr": "$3.00",
        "rule_type": "registered",
        "scenario_key": "scenario_3_rooftop",
        "features": ["Elevator Access", "CCTV Monitored"]
    },
    {
        "id": "lot-4",
        "name": "Harbor View Compact Bays",
        "type": "Express Compact Lot",
        "latitude": 37.7810,
        "longitude": -122.4110,
        "total_capacity": 30,
        "live_available": 1,
        "distance_km": 1.5,
        "price_per_hr": "$3.50",
        "rule_type": "registered",
        "scenario_key": "scenario_4_tight",
        "features": ["Narrow Bays", "Compact Priority"]
    }
]


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "engine": "Ultralytics YOLOv8",
        "device": "CPU / DirectML",
        "cv_modules": ["YOLO", "Homography", "Occupancy", "VehicleMatcher", "RuleEngine"]
    }


@app.get("/api/vehicles")
def get_vehicles():
    """Return available vehicle profiles."""
    return VehicleProfiles.PROFILES


@app.get("/api/scenarios")
def get_scenarios():
    """Return configured test scenarios with metadata."""
    scenarios = load_scenarios()
    output = []
    for key, data in scenarios.items():
        output.append({
            "id": key,
            "title": data["title"],
            "description": data["description"],
            "image_url": f"/static/scenarios/{os.path.basename(data['image_path'])}",
            "slots_count": len(data.get("slots", []))
        })
    return output


@app.get("/api/parking/locations")
def get_parking_locations():
    """Return nearby GPS parking locations (Step 6)."""
    return GPS_PARKING_LOCATIONS


@app.post("/api/cv/analyze")
async def analyze_parking(
    scenario_key: Optional[str] = Form(None),
    vehicle_type: str = Form("suv"),
    custom_length: Optional[float] = Form(None),
    custom_width: Optional[float] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    custom_slots_json: Optional[str] = Form(None)
):
    """
    Main Computer Vision inference endpoint.
    Performs:
    1. YOLO detection (vehicles, pedestrians, obstacles)
    2. Perspective homography transformation & BEV projection
    3. Parking slot occupancy evaluation (Available / Occupied / Blocked)
    4. Vehicle dimension suitability matching
    5. Parking regulation verification
    6. Recommendation selection
    """
    scenarios = load_scenarios()
    scenario_data = None

    if image_file:
        contents = await image_file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid uploaded image format")
    elif scenario_key and scenario_key in scenarios:
        scenario_data = scenarios[scenario_key]
        img_path = scenario_data["image_path"]
        if not os.path.isabs(img_path):
            img_path = os.path.join(BASE_DIR, "..", img_path)
        image = cv2.imread(img_path)
        if image is None:
            raise HTTPException(status_code=404, detail=f"Scenario image not found at {img_path}")
    else:
        # Default to scenario 1
        scenario_data = scenarios.get("scenario_1_aerial")
        img_path = os.path.join(SCENARIOS_DIR, "scenario_1_aerial.jpg")
        image = cv2.imread(img_path)

    h, w = image.shape[:2]

    # 1. Run YOLO detection
    detections = detector.detect(image)

    # 2. Setup Geometry & Homography
    if scenario_data and "homography" in scenario_data:
        h_cfg = scenario_data["homography"]
        geom = ParkingGeometry(
            src_points=h_cfg["src_points"],
            ground_size_meters=tuple(h_cfg["ground_size_meters"]),
            bev_resolution=tuple(h_cfg["bev_resolution"])
        )
    else:
        geom = ParkingGeometry()

    # 3. Setup Slot Polygons
    if custom_slots_json:
        try:
            slot_definitions = json.loads(custom_slots_json)
        except Exception:
            slot_definitions = scenario_data.get("slots", []) if scenario_data else []
    elif scenario_data and "slots" in scenario_data:
        slot_definitions = scenario_data["slots"]
    else:
        # Auto generate 3 default slots if no coordinates given
        slot_definitions = [
            {"id": "A1", "label": "Bay A1", "polygon": [[int(w*0.1), int(h*0.35)], [int(w*0.35), int(h*0.35)], [int(w*0.35), int(h*0.75)], [int(w*0.1), int(h*0.75)]], "rule_zone": "registered"},
            {"id": "A2", "label": "Bay A2", "polygon": [[int(w*0.38), int(h*0.35)], [int(w*0.63), int(h*0.35)], [int(w*0.63), int(h*0.75)], [int(w*0.38), int(h*0.75)]], "rule_zone": "registered"},
            {"id": "A3", "label": "Bay A3", "polygon": [[int(w*0.66), int(h*0.35)], [int(w*0.9), int(h*0.35)], [int(w*0.9), int(h*0.75)], [int(w*0.66), int(h*0.75)]], "rule_zone": "registered"}
        ]

    # 4. Occupancy Analysis
    analyzed_slots = analyzer.evaluate_slots(slot_definitions, detections)

    # 5. Vehicle Fit & Metric Calculation
    veh_specs = matcher.get_vehicle_specs(vehicle_type, custom_length, custom_width)

    for s in analyzed_slots:
        # Calculate metric dimensions
        s["metrics"] = geom.compute_slot_metric_dimensions(s["polygon"])
        # Evaluate vehicle fit
        s["vehicle_fit"] = matcher.evaluate_fit(s["metrics"], veh_specs)
        # Verify parking rules
        rule_zone = s.get("custom_metadata", {}).get("rule_zone") or s.get("rule_zone", "registered")
        s["rules"] = RuleEngine.verify_slot_legality({"status": s["status"], "rule_zone": rule_zone})

    # 6. Recommendation Selection
    recommended_slot = None
    # Pick first available slot that fits vehicle and is legal
    for s in analyzed_slots:
        if s["status"] == "AVAILABLE" and s["vehicle_fit"]["is_suitable"] and s["rules"]["can_park_legally"]:
            recommended_slot = s
            break
    # Fallback to any available slot
    if not recommended_slot:
        for s in analyzed_slots:
            if s["status"] == "AVAILABLE":
                recommended_slot = s
                break

    # 7. Render Visual Annotations
    annotated_img = ParkingVisualizer.annotate_frame(
        image=image,
        analyzed_slots=analyzed_slots,
        detections=detections,
        vehicle_name=veh_specs["name"]
    )

    # Encode annotated frame to Base64 JPEG
    _, buffer_ann = cv2.imencode('.jpg', annotated_img, [cv2.IMWRITE_JPEG_QUALITY, 88])
    annotated_base64 = base64.b64encode(buffer_ann).decode('utf-8')

    # Warp and encode BEV
    bev_base64 = None
    bev_img = geom.warp_to_bird_eye_view(image)
    if bev_img is not None:
        _, buffer_bev = cv2.imencode('.jpg', bev_img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        bev_base64 = base64.b64encode(buffer_bev).decode('utf-8')

    # Summary
    avail_count = sum(1 for s in analyzed_slots if s["status"] == "AVAILABLE")
    occ_count = sum(1 for s in analyzed_slots if s["status"] == "OCCUPIED")
    block_count = sum(1 for s in analyzed_slots if s["status"] == "BLOCKED")

    # Serialize homography matrix
    h_matrix_list = geom.H.tolist() if geom.H is not None else None

    return {
        "success": True,
        "summary": {
            "total_slots": len(analyzed_slots),
            "available": avail_count,
            "occupied": occ_count,
            "blocked": block_count
        },
        "vehicle": veh_specs,
        "recommended_slot": recommended_slot,
        "slots": analyzed_slots,
        "detections_count": len(detections),
        "detections": detections,
        "homography_matrix": h_matrix_list,
        "annotated_image": f"data:image/jpeg;base64,{annotated_base64}",
        "bev_image": f"data:image/jpeg;base64,{bev_base64}" if bev_base64 else None
    }


# Mount frontend static files at root (after API routes so API takes precedence)
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")



