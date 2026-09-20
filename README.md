# Smart Parking Detection Using Computer Vision

A multi-stage Computer Vision system that detects vacant and blocked parking spaces using **YOLOv8**, computes ground-plane metric geometry via **Perspective Homography ($H$)**, evaluates vehicle dimension suitability, verifies legal parking regulations, and guides users with an interactive web dashboard and GPS navigation map.

---

## 🚀 Key Features

1. **Computer Vision Core (Built First ⭐)**:
   - **YOLOv8 Object Detection**: Identifies vehicles (`car`, `truck`, `motorcycle`, `bus`) and obstacles (`bicycle`, `person`, `traffic cone`, `debris`).
   - **Camera Geometry & Homography ($H$)**: Implements 4-point projective transformation matrix to project parking bays into an orthographic **Bird's-Eye View (BEV)** and calculate ground-plane physical dimensions ($W\,\text{m} \times L\,\text{m}$).
   - **Spatial Occupancy Engine**: Overlap & IoU analysis classifying bays into:
     - 🟢 **Available**: Empty, clear of obstacles.
     - 🔴 **Occupied**: Vehicle parked inside.
     - 🟡 **Blocked**: Blocked by bicycle, pedestrian, or encroachment.
2. **Vehicle Dimension Matcher**:
   - Compares physical slot size against vehicle profiles (SUV $4.6 \times 1.9\,\text{m}$, Sedan $4.4 \times 1.8\,\text{m}$, Compact $3.8 \times 1.7\,\text{m}$, Bike $2.0 \times 0.8\,\text{m}$, or custom dimensions).
   - Computes door clearance margins (e.g. $+0.82\,\text{m}$ clearance).
3. **GPS Map & Navigation Layer**:
   - Interactive OpenStreetMap/Leaflet integration.
   - Shows user GPS coordinates, nearby parking facilities, live capacities, hourly rates, and simulated driving route lines.
4. **Parking Rules & Regulatory Verification**:
   - Registered Parking Lot ✅
   - Public Permitted Curbside ✅
   - Strict No-Parking / Tow-Away Zone ❌
   - Private / Unknown Permit 🟡
5. **Interactive Web Dashboard**:
   - Dark-mode glassmorphic interface with live camera feed simulation, HUD counters, scenario picker, custom image upload, and step-by-step driver flow.
6. **Standalone CLI Coursework Script (`test_cv.py`)**:
   - Instant terminal verification with formatted diagnostic tables and visual output generation (`output_annotated.jpg`).

---

## 📁 Project Structure

```
parking/
├── backend/
│   ├── main.py                     # FastAPI backend server & static router
│   ├── cv/
│   │   ├── yolo_detector.py        # YOLOv8 object detector
│   │   ├── geometry.py             # Perspective transform, homography H & BEV
│   │   ├── occupancy.py            # Overlap IoU & slot state classifier
│   │   ├── vehicle_matcher.py      # Vehicle footprint & clearance evaluator
│   │   └── visualizer.py           # Polygons, bounding boxes & HUD renderer
│   ├── rules/
│   │   └── rule_engine.py          # Parking regulations & zone compliance
│   └── data/
│       └── scenarios/              # Curated parking scenarios & configs
├── frontend/
│   ├── index.html                  # Main Web UI
│   ├── style.css                   # Glassmorphic dark theme stylesheet
│   └── app.js                      # Application controller & Leaflet map logic
├── test_cv.py                      # Standalone CLI demonstration script
└── pyproject.toml                  # Python package specifications
```

---

## ⚡ Quick Start

### 1. Launch the Interactive Web Application
```bash
# In the project root:
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your web browser.

### 2. Run the Computer Vision CLI Demo
```bash
# Test Scenario 1 (Overhead bays with vacant spots for SUV):
uv run python test_cv.py --scenario scenario_1_aerial --vehicle suv

# Test Scenario 2 (Driver view with bicycle obstruction):
uv run python test_cv.py --scenario scenario_2_driver --vehicle sedan

# Test Scenario 4 (Narrow bay test):
uv run python test_cv.py --scenario scenario_4_tight --vehicle suv

# Test on any custom photo:
uv run python test_cv.py --image path/to/parking.jpg --vehicle compact
```
Annotated images will be saved as `output_annotated.jpg` and `output_bev.jpg`.
