"""
Parking Space Analyzer
======================
Analyzes dynamic candidate parking regions from live camera input.
Evaluates:
- Whether parking boundaries exist dynamically (Marked line stalls or inter-vehicle corridors)
- Physical occupancy and obstacle/pedestrian blockers via Shapely
- Realistic metric dimension estimation (length & width) via camera perspective homography
- Usable free clearance for the user's specific vehicle profile

STRICT RULE: NO DEFAULT OR PREDEFINED HARDCODED PARKING RECTANGLES.
Candidate regions are discovered dynamically from camera analysis.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from shapely.geometry import Polygon, Point, box
from backend.cv.geometry import ParkingGeometry
from backend.cv.occupancy import ParkingOccupancyAnalyzer, SlotStatus
from backend.cv.vehicle_matcher import VehicleMatcher
from backend.cv.candidate_detector import ParkingCandidateDetector
from backend.cv.free_space_analyzer import FreeSpaceAnalyzer


class ParkingSpaceAnalyzer:
    """
    Evaluates candidate spatial regions, marks boundaries, checks physical occupancy,
    and calculates metric fit against user vehicle specs.
    """

    def __init__(
        self,
        geometry: Optional[ParkingGeometry] = None,
        occupancy_analyzer: Optional[ParkingOccupancyAnalyzer] = None,
        vehicle_matcher: Optional[VehicleMatcher] = None,
        candidate_detector: Optional[ParkingCandidateDetector] = None
    ):
        self.geom = geometry or ParkingGeometry()
        self.occupancy_analyzer = occupancy_analyzer or ParkingOccupancyAnalyzer()
        self.vehicle_matcher = vehicle_matcher or VehicleMatcher()
        self.candidate_detector = candidate_detector or ParkingCandidateDetector(
            free_space_analyzer=FreeSpaceAnalyzer(),
            geometry=self.geom,
            occupancy_analyzer=self.occupancy_analyzer,
            vehicle_matcher=self.vehicle_matcher
        )

    def analyze_spaces(
        self,
        image_shape: Tuple[int, int],
        detections: List[Dict[str, Any]],
        zone_info: Dict[str, Any],
        predefined_slots: Optional[List[Dict[str, Any]]] = None,
        vehicle_specs: Optional[Dict[str, Any]] = None,
        parking_mode: str = "auto",
        image: Optional[np.ndarray] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze all candidate spaces in view dynamically from camera frames.
        
        :param image_shape: (height, width) of camera frame
        :param detections: List of YOLO detection dictionaries
        :param zone_info: Output from ParkingZoneValidator
        :param predefined_slots: Slots defined in scenario or parking lot database
        :param vehicle_specs: Target vehicle dimensions and tolerances
        :param parking_mode: 'marked', 'unmarked', or 'auto'
        :param image: Optional BGR camera frame for visual line & ground extraction
        :return: List of evaluated space dictionaries
        """
        veh_specs = vehicle_specs or self.vehicle_matcher.get_vehicle_specs("bike_cruiser")

        # Discover and evaluate candidate regions dynamically (zero default rectangles)
        evaluated_slots = self.candidate_detector.detect_candidates(
            image=image,
            detections=detections,
            image_shape=image_shape,
            zone_info=zone_info,
            predefined_slots=predefined_slots,
            user_vehicle_specs=veh_specs
        )

        return evaluated_slots
