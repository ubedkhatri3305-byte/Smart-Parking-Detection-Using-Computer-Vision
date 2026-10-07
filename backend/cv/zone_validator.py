"""
Parking Zone Validator
======================
Determines whether an observed visual region is an authentic, legal, and plausible
parking zone. Enforces the core principle:

    EMPTY SPACE != PARKING SPACE

Distinguishes between valid parking facilities and invalid/private/traffic areas:
VALID:
- marked parking slot
- parking lot
- designated roadside parking area
- known public parking area
- known temporary parking area

INVALID:
- house floor
- house entrance / gate
- private property / driveway
- garden / lawn
- open agricultural field
- footpath / pedestrian walkway
- active road / traffic lane
- restricted no-parking zone

UNKNOWN:
- unclassified empty land (defaults to NOT RECOMMENDING parking)
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np


class ZoneClass(str, Enum):
    # Valid parking zones
    MARKED_SLOT = "marked_parking_slot"
    PARKING_LOT = "parking_lot"
    DESIGNATED_ROADSIDE = "designated_roadside"
    KNOWN_PUBLIC_PARKING = "known_public_parking"
    TEMPORARY_PARKING = "temporary_parking"

    # Invalid non-parking areas
    HOUSE_FLOOR = "house_floor"
    HOUSE_ENTRANCE = "house_entrance"
    PRIVATE_PROPERTY = "private_property"
    DRIVEWAY = "driveway"
    GARDEN = "garden"
    FIELD = "field"
    FOOTPATH = "footpath"
    ROAD_TRAFFIC_LANE = "road_traffic_lane"
    RESTRICTED_NO_PARKING = "restricted_no_parking"

    # Unknown / unverified
    UNKNOWN = "unknown_area"


class ZoneStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    UNKNOWN = "UNKNOWN"


class ParkingZoneValidator:
    """
    Validates whether a candidate region is an authentic, permissible parking zone.
    Combines neural object detection, surface color/texture analysis, line/marking
    geometry, and contextual signals.
    """

    # Indoor domestic items (COCO classes)
    INDOOR_OBJECTS = {
        "chair", "couch", "bed", "dining table", "toilet",
        "tv", "laptop", "mouse", "remote", "keyboard", "cell phone",
        "microwave", "oven", "toaster", "sink", "refrigerator",
        "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush",
        "cup", "fork", "knife", "spoon", "bowl", "wine glass", "potted plant", "bottle"
    }

    # Contextual residential / private perimeter indicators
    PRIVATE_RESIDENTIAL_OBJECTS = {
        "gate", "door", "fence", "window", "house", "mailbox"
    }

    # Street / traffic infrastructure
    ROAD_INFRASTRUCTURE = {
        "traffic light", "fire hydrant", "stop sign", "parking meter", "bench"
    }

    # Active moving vehicle classes
    VEHICLE_CLASSES = {"car", "motorcycle", "bus", "truck", "train", "bicycle"}

    def __init__(self):
        pass

    def validate_zone(
        self,
        image: Optional[np.ndarray],
        detections: List[Dict[str, Any]],
        map_context: Optional[Dict[str, Any]] = None,
        parking_mode: str = "auto"
    ) -> Dict[str, Any]:
        """
        Evaluate if the scene is a valid parking zone.
        :param image: BGR numpy image frame (optional, for computer vision tests)
        :param detections: List of YOLO detection dictionaries
        :param map_context: Metadata from map/database (e.g. {'is_known_parking': True, 'type': 'public_lot'})
        :param parking_mode: 'marked', 'unmarked', or 'auto'
        :return: Dict with validation results, confidence, zone classification, and evidence
        """
        evidence_positive: List[str] = []
        evidence_negative: List[str] = []
        map_context = map_context or {}

        # -------------------------------------------------------------
        # 1. DATABASE / MAP CONTEXT VERIFICATION (Strongest ground truth)
        # -------------------------------------------------------------
        is_known_parking = map_context.get("is_known_parking", False)
        facility_type = map_context.get("type", "unknown")
        is_private_geo = map_context.get("is_private", False)
        is_no_parking_zone = map_context.get("is_no_parking", False)

        if is_no_parking_zone:
            return {
                "status": ZoneStatus.INVALID,
                "zone_class": ZoneClass.RESTRICTED_NO_PARKING,
                "confidence": 0.98,
                "is_valid": False,
                "headline": "RESTRICTED NO-PARKING ZONE",
                "reason": "Location is mapped as a strict no-parking or tow-away zone.",
                "evidence_positive": [],
                "evidence_negative": ["Mapped strict no-parking zone", "Tow-away regulation active"]
            }

        if is_private_geo:
            return {
                "status": ZoneStatus.INVALID,
                "zone_class": ZoneClass.PRIVATE_PROPERTY,
                "confidence": 0.90,
                "is_valid": False,
                "headline": "PRIVATE PROPERTY",
                "reason": "Location is identified as private residential property. Parking permission could not be verified.",
                "evidence_positive": [],
                "evidence_negative": ["Private property registry", "Permission unverified"]
            }

        if is_known_parking:
            evidence_positive.append(f"Verified parking facility in database: {facility_type}")

        # -------------------------------------------------------------
        # 2. YOLO CONTEXTUAL OBJECT ANALYSIS
        # -------------------------------------------------------------
        indoor_items = []
        residential_items = []
        road_infra_items = []
        vehicles = []
        obstacles = []

        for d in detections:
            cname = str(d.get("class_name", "")).lower()
            if cname in self.INDOOR_OBJECTS or d.get("is_indoor", False):
                indoor_items.append(cname)
            elif cname in self.PRIVATE_RESIDENTIAL_OBJECTS:
                residential_items.append(cname)
            elif cname in self.ROAD_INFRASTRUCTURE or d.get("is_road_object", False):
                road_infra_items.append(cname)
            elif cname in self.VEHICLE_CLASSES or d.get("is_vehicle", False):
                vehicles.append(d)
            else:
                obstacles.append(d)

        # REJECTION: Domestic Indoor Setting
        if indoor_items:
            items_str = ", ".join(sorted(list(set(indoor_items)))[:3])
            return {
                "status": ZoneStatus.INVALID,
                "zone_class": ZoneClass.HOUSE_FLOOR,
                "confidence": 0.96,
                "is_valid": False,
                "headline": "INDOOR / HOUSE FLOOR DETECTED",
                "reason": f"Indoor furniture and domestic setting detected ({items_str}). Not a parking zone.",
                "evidence_positive": [],
                "evidence_negative": [f"Indoor items: {items_str}", "Non-road domestic surface"]
            }

        # REJECTION: Private Driveway / House Entrance
        if residential_items and not is_known_parking:
            items_str = ", ".join(sorted(list(set(residential_items)))[:3])
            return {
                "status": ZoneStatus.INVALID,
                "zone_class": ZoneClass.HOUSE_ENTRANCE,
                "confidence": 0.88,
                "is_valid": False,
                "headline": "HOUSE ENTRANCE / PRIVATE DRIVEWAY",
                "reason": f"Private boundary or entrance detected ({items_str}). Parking permission cannot be verified.",
                "evidence_positive": [],
                "evidence_negative": [f"Residential perimeter: {items_str}", "Private vehicular access"]
            }

        # -------------------------------------------------------------
        # 3. SURFACE & TEXTURE ANALYSIS (If Image Available)
        # -------------------------------------------------------------
        marking_detected = False
        surface_type = "unknown"

        if image is not None and isinstance(image, np.ndarray) and image.size > 0:
            surface_info = self._analyze_surface_and_markings(image)
            surface_type = surface_info["surface_type"]
            marking_detected = surface_info["has_parking_lines"]

            if surface_type == "garden_lawn":
                return {
                    "status": ZoneStatus.INVALID,
                    "zone_class": ZoneClass.GARDEN,
                    "confidence": 0.92,
                    "is_valid": False,
                    "headline": "GARDEN / LAWN DETECTED",
                    "reason": "Surface analysis detected grass or landscape garden. Parking is prohibited on vegetation.",
                    "evidence_positive": [],
                    "evidence_negative": ["Grass / vegetative surface", "No vehicular pavement"]
                }

            if surface_type == "field":
                return {
                    "status": ZoneStatus.INVALID,
                    "zone_class": ZoneClass.FIELD,
                    "confidence": 0.90,
                    "is_valid": False,
                    "headline": "OPEN FIELD / UNPAVED TERRAIN",
                    "reason": "Open field or unpaved unmanaged terrain detected. Not an authorized parking area.",
                    "evidence_positive": [],
                    "evidence_negative": ["Unpaved dirt / soil terrain", "No parking demarcations"]
                }

            if surface_type == "footpath":
                return {
                    "status": ZoneStatus.INVALID,
                    "zone_class": ZoneClass.FOOTPATH,
                    "confidence": 0.89,
                    "is_valid": False,
                    "headline": "FOOTPATH / PEDESTRIAN WALKWAY",
                    "reason": "Pedestrian sidewalk paving / curb detected. Parking on footpaths is illegal.",
                    "evidence_positive": [],
                    "evidence_negative": ["Sidewalk paver geometry", "Pedestrian right-of-way"]
                }

            if surface_type == "indoor_flooring" and len(vehicles) == 0 and not is_known_parking:
                return {
                    "status": ZoneStatus.INVALID,
                    "zone_class": ZoneClass.HOUSE_FLOOR,
                    "confidence": 0.94,
                    "is_valid": False,
                    "headline": "DOMESTIC INTERIOR FLOOR",
                    "reason": "Indoor tile, hardwood, or carpet flooring detected. Point camera outdoors at a parking space.",
                    "evidence_positive": [],
                    "evidence_negative": ["High saturation indoor floor reflection", "Absence of road asphalt"]
                }

            if surface_type == "road_lane":
                evidence_negative.append("Active vehicular traffic lane texture")

            if marking_detected:
                evidence_positive.append("Demarcated parking stall striping detected on pavement")

        # Check for explicit parking infrastructure
        parking_meters = [d for d in detections if d.get("class_name", "").lower() == "parking meter"]
        if parking_meters:
            evidence_positive.append("Parking meter infrastructure verified")

        # -------------------------------------------------------------
        # 4. DECISION SYNTHESIS: VALID vs UNKNOWN vs INVALID
        # -------------------------------------------------------------
        # A) Explicit marked parking slot
        if marking_detected:
            return {
                "status": ZoneStatus.VALID,
                "zone_class": ZoneClass.MARKED_SLOT,
                "confidence": 0.92,
                "is_valid": True,
                "headline": "DESIGNATED MARKED PARKING SLOT",
                "reason": "Authentic marked parking bay with visible road striping detected on asphalt.",
                "evidence_positive": evidence_positive,
                "evidence_negative": evidence_negative
            }

        # B) Known public parking facility from database
        if is_known_parking:
            return {
                "status": ZoneStatus.VALID,
                "zone_class": ZoneClass.KNOWN_PUBLIC_PARKING if facility_type == "public" else ZoneClass.PARKING_LOT,
                "confidence": 0.94,
                "is_valid": True,
                "headline": "KNOWN PUBLIC PARKING AREA",
                "reason": f"Verified public parking facility ({map_context.get('name', 'Designated Facility')}).",
                "evidence_positive": evidence_positive,
                "evidence_negative": evidence_negative
            }

        # C) Parked vehicles in row or designated parking lot cluster
        if len(vehicles) >= 2:
            return {
                "status": ZoneStatus.VALID,
                "zone_class": ZoneClass.PARKING_LOT if is_known_parking else ZoneClass.DESIGNATED_ROADSIDE,
                "confidence": 0.85,
                "is_valid": True,
                "headline": "DESIGNATED PARKING AREA" if not is_known_parking else "KNOWN PUBLIC PARKING AREA",
                "reason": f"Cluster of {len(vehicles)} parked vehicles detected in parking formation.",
                "evidence_positive": evidence_positive + [f"{len(vehicles)} parked vehicles aligned along parking row"],
                "evidence_negative": evidence_negative
            }

        # D) Road traffic lane without parking markings
        if surface_type == "road_lane" and not marking_detected and not is_known_parking:
            return {
                "status": ZoneStatus.INVALID,
                "zone_class": ZoneClass.ROAD_TRAFFIC_LANE,
                "confidence": 0.85,
                "is_valid": False,
                "headline": "ACTIVE ROAD / TRAFFIC LANE",
                "reason": "Area is an open vehicular roadway or traffic lane. Parking in travel lanes is prohibited.",
                "evidence_positive": [],
                "evidence_negative": ["Active carriageway asphalt", "No parking bay demarcations", "Traffic lane"]
            }

        # E) Default: UNKNOWN EMPTY AREA (Must NOT recommend parking!)
        return {
            "status": ZoneStatus.UNKNOWN,
            "zone_class": ZoneClass.UNKNOWN,
            "confidence": 0.50,
            "is_valid": False,
            "headline": "UNVERIFIED / UNKNOWN AREA",
            "reason": "An open area is visible, but valid parking status and permission could not be verified.",
            "evidence_positive": evidence_positive,
            "evidence_negative": ["Absence of parking demarcations", "Location not in public parking database", "Permission unknown"]
        }

    def _analyze_surface_and_markings(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract ground region and analyze color, texture, and linear road markings.
        Enforces: EMPTY SPACE != PARKING SPACE.
        Distinguishes:
        - Light indoor ceramic/marble tiles (high luminance, no asphalt aggregate)
        - Warm indoor hardwood/parquet/carpet (warm hue, saturation, smooth)
        - Vegetative lawns and gardens
        - Open unpaved dirt fields
        - Sidewalk pavers / footpaths
        - Active road lanes (dark asphalt without parking demarcations)
        - Authentic marked parking slots (dark asphalt with high-contrast longitudinal stripes)
        """
        h, w = image.shape[:2]
        ground_roi = image[int(h * 0.40):, :]
        if ground_roi.size == 0:
            return {"surface_type": "unknown", "has_parking_lines": False}

        hsv = cv2.cvtColor(ground_roi, cv2.COLOR_BGR2HSV)
        h_ch = hsv[:, :, 0]
        s_ch = hsv[:, :, 1]
        v_ch = hsv[:, :, 2]

        mean_h = float(np.mean(h_ch))
        mean_s = float(np.mean(s_ch))
        mean_v = float(np.mean(v_ch))
        std_v = float(np.std(v_ch))

        # 1. Vegetation / Garden (Hue 35-85 with medium/high saturation)
        green_mask = (h_ch >= 35) & (h_ch <= 85) & (s_ch > 45) & (v_ch > 40)
        green_ratio = float(np.count_nonzero(green_mask)) / float(ground_roi.shape[0] * ground_roi.shape[1])
        if green_ratio > 0.30:
            return {"surface_type": "garden_lawn", "has_parking_lines": False}

        # 2. Dirt / Field / Earth (Brown/Yellowish hue 10-25 with low-mid value and matte texture)
        brown_mask = (h_ch >= 10) & (h_ch <= 26) & (s_ch > 55) & (v_ch < 170)
        brown_ratio = float(np.count_nonzero(brown_mask)) / float(ground_roi.shape[0] * ground_roi.shape[1])
        if brown_ratio > 0.40:
            return {"surface_type": "field", "has_parking_lines": False}

        # 3. Footpath / Sidewalk curb texture (repetitive paver pattern or light gray curb)
        gray = cv2.cvtColor(ground_roi, cv2.COLOR_BGR2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edges = (np.abs(sobel_x) > 50) | (np.abs(sobel_y) > 50)
        edge_density = float(np.count_nonzero(edges)) / float(gray.size)

        # Footpath paver repetitive tiling pattern with high edge density
        if edge_density > 0.14 and mean_s < 40.0:
            return {"surface_type": "footpath", "has_parking_lines": False}

        # 4. Domestic Indoor Flooring Detection (Enforces home floor rejection)
        # 4a. High-saturation domestic flooring (hardwood, terracotta, warm laminate, rugs)
        if mean_s > 80.0 and green_ratio < 0.15 and brown_ratio < 0.35:
            return {"surface_type": "indoor_flooring", "has_parking_lines": False}

        # 4b. Light-colored ceramic tile, porcelain, marble, or polished interior floor
        # Road asphalt is charcoal/dark gray (mean_v between 35 and 130).
        # Indoor tiled floors are typically bright (mean_v >= 170) with low saturation.
        if mean_v >= 170.0 and mean_s < 45.0:
            return {"surface_type": "indoor_flooring", "has_parking_lines": False}

        # 4c. Uniform smooth indoor surfaces with negligible aggregate texture
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        lap_var = float(laplacian.var())
        # Glossy indoor surface with high reflections and low granular roughness
        if lap_var < 10.0 and mean_v > 150.0:
            return {"surface_type": "indoor_flooring", "has_parking_lines": False}

        # 5. Authenticated Painted Parking Bay Lines on Outdoor Asphalt
        # True parking bay lines require:
        # a) Dark asphalt background (mean_v <= 140, mean_s < 55)
        # b) High-contrast bright painted stripes (white or yellow)
        # c) Longitudinal structural line geometry (significant length, not an orthogonal tile grid)
        has_parking_lines = False

        if mean_v <= 140.0 and mean_s < 55.0:
            white_lines_mask = (s_ch < 40) & (v_ch > 180)
            yellow_lines_mask = (h_ch >= 15) & (h_ch <= 38) & (s_ch > 80) & (v_ch > 140)
            lines_mask = cv2.bitwise_or(white_lines_mask.astype(np.uint8), yellow_lines_mask.astype(np.uint8)) * 255

            edges_line = cv2.Canny(lines_mask, 50, 150)
            min_len = int(ground_roi.shape[0] * 0.20)
            lines = cv2.HoughLinesP(edges_line, 1, np.pi / 180, threshold=30, minLineLength=min_len, maxLineGap=20)

            if lines is not None and len(lines) >= 2:
                # Analyze line angles to ensure they are longitudinal parking stall stripes
                angles = []
                for l in lines:
                    coords = l.ravel()
                    if len(coords) >= 4:
                        x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
                        dx = x2 - x1
                        dy = y2 - y1
                        angle_deg = abs(np.degrees(np.arctan2(dy, dx)))
                        angles.append(angle_deg)

                # Stall lines typically have slope between 20 deg and 90 deg (not all strictly flat horizontal)
                steep_lines = [a for a in angles if 20.0 <= a <= 90.0]
                if len(steep_lines) >= 2:
                    has_parking_lines = True

            # Require that candidate line pixels represent between 0.8% and 25% of surface (lines, not flood of white)
            line_pixels = float(np.count_nonzero(lines_mask)) / float(ground_roi.shape[0] * ground_roi.shape[1])
            if line_pixels > 0.25:
                # Too much bright area (likely bright floor or overexposure, not thin bay stripes)
                has_parking_lines = False

        # 6. Asphalt Roadway vs Marked Slot
        if mean_s < 55.0 and std_v > 10.0 and mean_v <= 140.0:
            if has_parking_lines:
                return {"surface_type": "asphalt_marked", "has_parking_lines": True}
            else:
                return {"surface_type": "road_lane", "has_parking_lines": False}

        return {"surface_type": "unconfirmed", "has_parking_lines": False}
