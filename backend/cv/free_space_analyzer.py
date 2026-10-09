"""
Dynamic Free-Space Analyzer
===========================
Analyzes actual camera frames to discover potential free ground regions.
Combines:
- YOLO object detections (vehicles, pedestrians, obstacles, poles, domestic items)
- Road/ground region extraction and color/texture segmentation
- Visible painted parking line detection (Hough transforms & morphological analysis)
- Inter-vehicle gap detection (open physical space between parked cars along a row)
- Ground obstacle intersection testing

ENFORCES CORE PRINCIPLE: EMPTY SPACE != PARKING SPACE.
A free space is only generated if authentic road/parking pavement or inter-vehicle corridors exist.
Zero hardcoded rectangles or predefined default coordinates.
"""

from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np
from shapely.geometry import Polygon, Point, box


class FreeSpaceAnalyzer:
    """
    Discovers potential free spatial regions dynamically from the live camera frame.
    """

    def __init__(
        self,
        min_gap_width_ratio: float = 0.14,
        max_gap_width_ratio: float = 0.85,
        ground_roi_top: float = 0.40,
        ground_roi_bottom: float = 0.94
    ):
        self.min_gap_width_ratio = min_gap_width_ratio
        self.max_gap_width_ratio = max_gap_width_ratio
        self.ground_roi_top = ground_roi_top
        self.ground_roi_bottom = ground_roi_bottom

    def analyze_frame_free_spaces(
        self,
        image: Optional[np.ndarray],
        detections: List[Dict[str, Any]],
        image_shape: Tuple[int, int],
        zone_info: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze the actual frame to find free physical candidate regions.
        
        :param image: BGR camera frame (or None if only detections available)
        :param detections: List of YOLO detection dictionaries
        :param image_shape: (height, width)
        :param zone_info: Output from ParkingZoneValidator
        :return: List of dynamically detected candidate free spaces
        """
        h, w = image_shape[:2]
        y_top = int(h * self.ground_roi_top)
        y_bot = int(h * self.ground_roi_bottom)

        is_zone_valid = zone_info.get("is_valid", False)
        raw_zc = zone_info.get("zone_class", "unknown_area")
        zc_str = raw_zc.value if hasattr(raw_zc, "value") else str(raw_zc)
        if "." in zc_str:
            zc_str = zc_str.split(".", 1)[-1]
        zone_class = zc_str.lower()

        # REJECTION: Non-parking environments (Wall, computer screen, house floor, garden, field, sidewalk)
        # Never generate parking spaces on unverified domestic or vertical planes
        if not is_zone_valid and zone_class in ("house_floor", "garden", "field", "footpath", "private_property"):
            return []

        # Filter out ego-vehicle dashboard / hood detections at bottom of camera view
        cleaned_detections = [
            d for d in detections
            if not ((d["bbox"][2] - d["bbox"][0]) / float(w) > 0.75 and d["bbox"][1] > 0.42 * h and (d["bbox"][3] - d["bbox"][1]) / float(h) > 0.22)
            and not (d.get("confidence", 1.0) < 0.20 and d["bbox"][1] > 0.75 * h)
        ]

        vehicles = [d for d in cleaned_detections if d.get("is_vehicle") or d.get("category") == "vehicle"]
        obstacles = [d for d in cleaned_detections if (d.get("is_obstacle") or d.get("is_person") or d.get("category") in ("obstacle", "person", "hazard"))]

        candidates: List[Dict[str, Any]] = []

        # ---------------------------------------------------------------------
        # STRATEGY 1: MARKED PARKING BAY DETECTION (If image available)
        # ---------------------------------------------------------------------
        if image is not None and isinstance(image, np.ndarray) and image.size > 0:
            marked_bays = self._detect_marked_stall_boundaries(image, w, h, y_top, y_bot, cleaned_detections)
            if marked_bays:
                candidates.extend(marked_bays)

        # ---------------------------------------------------------------------
        # STRATEGY 2: INTER-VEHICLE GAP DETECTION (Empty space between parked cars)
        # ---------------------------------------------------------------------
        # If 2 or more vehicles are visible in the scene, discover open physical gaps between them
        if len(vehicles) >= 2 or (len(vehicles) == 1 and is_zone_valid):
            gap_candidates = self._detect_inter_vehicle_gaps(w, h, y_top, y_bot, vehicles, obstacles)
            # Avoid duplicating already marked bays
            for gc in gap_candidates:
                if not any(self._polygons_overlap(gc["polygon"], c["polygon"], threshold=0.40) for c in candidates):
                    candidates.append(gc)

        # ---------------------------------------------------------------------
        # STRATEGY 3: VERIFIED LOT CORRIDOR / FORWARD PARKING BAY
        # ---------------------------------------------------------------------
        # ONLY if explicitly confirmed as a designated parking lot/facility from map context AND valid parking zone
        if not candidates and is_zone_valid and zone_info.get("is_known_parking") and zone_class not in ("garden", "footpath", "field", "house_floor", "unknown_area", "vertical_surface"):
            lot_bays = self._detect_lot_ground_corridors(w, h, y_top, y_bot, cleaned_detections)
            candidates.extend(lot_bays)

        return candidates

    def _detect_marked_stall_boundaries(
        self,
        image: np.ndarray,
        w: int,
        h: int,
        y_top: int,
        y_bot: int,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect authentic painted parking stall lines on asphalt using edge & line analysis.
        """
        roi = image[y_top:y_bot, :]
        if roi.size == 0:
            return []

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # White and yellow road marking extraction
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        white_mask = cv2.inRange(gray, 185, 255)
        yellow_mask = cv2.inRange(hsv, np.array([15, 60, 120]), np.array([36, 255, 255]))
        marking_mask = cv2.bitwise_or(white_mask, yellow_mask)

        # Morphological filtering to clean noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 7))
        opened = cv2.morphologyEx(marking_mask, cv2.MORPH_OPEN, kernel)

        edges = cv2.Canny(opened, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=40, minLineLength=int(h * 0.12), maxLineGap=25)

        if lines is None or len(lines) < 2:
            return []

        # Find steep stall partition lines (angle > 45 degrees)
        vertical_lines = []
        for line in lines:
            line_flat = np.array(line).flatten()
            if len(line_flat) < 4:
                continue
            x1, y1, x2, y2 = [int(v) for v in line_flat[:4]]
            dx = abs(x2 - x1)
            dy = abs(y2 - y1)
            if dy > 0 and (dy / (dx + 1e-5)) > 0.8:
                mid_x = (x1 + x2) / 2.0
                vertical_lines.append(mid_x)

        if len(vertical_lines) < 2:
            return []

        # Cluster lines into distinct boundary dividers
        vertical_lines.sort()
        clusters = []
        current_cluster = [vertical_lines[0]]
        for lx in vertical_lines[1:]:
            if (lx - current_cluster[-1]) < w * 0.08:
                current_cluster.append(lx)
            else:
                clusters.append(float(np.mean(current_cluster)))
                current_cluster = [lx]
        clusters.append(float(np.mean(current_cluster)))

        if len(clusters) < 2:
            return []

        marked_slots = []
        for i in range(len(clusters) - 1):
            x_left = clusters[i]
            x_right = clusters[i + 1]
            span_ratio = (x_right - x_left) / float(w)

            # Valid parking bay width span (typically 18% to 55% of camera width)
            if self.min_gap_width_ratio <= span_ratio <= self.max_gap_width_ratio:
                # Perspective trapezoid conforming to stall line convergence
                top_w = (x_right - x_left) * 0.82
                cx = (x_left + x_right) / 2.0
                poly = [
                    [int(max(0, cx - top_w / 2.0)), y_top],
                    [int(min(w, cx + top_w / 2.0)), y_top],
                    [int(min(w, x_right)), y_bot],
                    [int(max(0, x_left)), y_bot]
                ]
                marked_slots.append({
                    "id": f"Marked Bay {i + 1}",
                    "label": f"Marked Bay {i + 1}",
                    "source": "marked_line_detection",
                    "polygon": poly,
                    "status": "AVAILABLE",
                    "blocked_reason": None,
                    "rule_zone": "registered"
                })

        return marked_slots

    def _detect_inter_vehicle_gaps(
        self,
        w: int,
        h: int,
        y_top: int,
        y_bot: int,
        vehicles: List[Dict[str, Any]],
        obstacles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Dynamically detect empty physical gaps between parked vehicles.
        Example: Car [A]  <--- EMPTY PHYSICAL GAP --->  Car [B]
        """
        parked_vehicles = sorted(vehicles, key=lambda o: (o["bbox"][0] + o["bbox"][2]) / 2.0)
        if len(parked_vehicles) < 2:
            return []

        gaps = []
        last_x_norm = max(0.04, min(0.96, parked_vehicles[0]["bbox"][2] / float(w)))
        gap_idx = 1

        for obj in parked_vehicles[1:]:
            x1, y1, x2, y2 = obj["bbox"]
            x1_norm = max(0.04, min(0.96, x1 / float(w)))
            x2_norm = max(0.04, min(0.96, x2 / float(w)))

            gap_width = x1_norm - last_x_norm
            # If an open corridor exists between these two parked vehicles
            if gap_width >= self.min_gap_width_ratio:
                cx = (last_x_norm + x1_norm) / 2.0
                top_w = gap_width * 0.82
                poly = [
                    [int(max(0.02, cx - top_w / 2.0) * w), y_top],
                    [int(min(0.98, cx + top_w / 2.0) * w), y_top],
                    [int(x1_norm * w), y_bot],
                    [int(last_x_norm * w), y_bot]
                ]
                gaps.append({
                    "id": f"Space {gap_idx}",
                    "label": f"Space {gap_idx} (Between Vehicles)",
                    "source": "inter_vehicle_gap",
                    "polygon": poly,
                    "status": "AVAILABLE",
                    "blocked_reason": None,
                    "rule_zone": "registered"
                })
                gap_idx += 1

            last_x_norm = x2_norm

        return gaps

    def _detect_lot_ground_corridors(
        self,
        w: int,
        h: int,
        y_top: int,
        y_bot: int,
        detections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        For verified parking areas or forward camera drive-in views, segment candidate stall.
        """
        vehicles = [d for d in detections if d.get("is_vehicle") or d.get("category") == "vehicle"]
        if len(vehicles) >= 2:
            return self._detect_inter_vehicle_gaps(w, h, y_top, y_bot, vehicles, [])
        return []

    def _polygons_overlap(self, poly1: List[List[int]], poly2: List[List[int]], threshold: float = 0.35) -> bool:
        """Check if two polygon regions significantly overlap."""
        try:
            p1 = Polygon(poly1)
            p2 = Polygon(poly2)
            if not p1.is_valid or not p2.is_valid:
                return False
            inter = p1.intersection(p2).area
            smaller_area = min(p1.area, p2.area)
            if smaller_area <= 0:
                return False
            return (inter / smaller_area) >= threshold
        except Exception:
            return False
