"""
Perspective Transformation & Camera Geometry Module for Parking Analysis
Implements Homography Matrix estimation, Bird's-Eye View (BEV) warping,
and metric ground-plane calibration (pixels -> real-world meters).
"""

from typing import List, Tuple, Dict, Any, Optional
import cv2
import numpy as np


class ParkingGeometry:
    def __init__(
        self,
        src_points: Optional[List[List[float]]] = None,
        dst_points: Optional[List[List[float]]] = None,
        ground_size_meters: Tuple[float, float] = (15.0, 10.0),  # (width_m, height_m)
        bev_resolution: Tuple[int, int] = (600, 400)             # (width_px, height_px)
    ):
        """
        Initialize the geometry engine.
        :param src_points: 4 quadrilateral points in image coordinates [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                           Order: Top-Left, Top-Right, Bottom-Right, Bottom-Left
        :param dst_points: Corresponding points in the warped Bird's-Eye View
        :param ground_size_meters: Real-world metric dimensions (width_m, length_m) of the reference area
        :param bev_resolution: (width, height) in pixels for the generated BEV image
        """
        self.bev_width, self.bev_height = bev_resolution
        self.ground_width_m, self.ground_length_m = ground_size_meters

        self.src_pts = np.array(src_points, dtype=np.float32) if src_points else None
        if dst_points is not None:
            self.dst_pts = np.array(dst_points, dtype=np.float32)
        else:
            self.dst_pts = np.array([
                [0, 0],
                [self.bev_width - 1, 0],
                [self.bev_width - 1, self.bev_height - 1],
                [0, self.bev_height - 1]
            ], dtype=np.float32)

        self.H: Optional[np.ndarray] = None
        self.H_inv: Optional[np.ndarray] = None

        # Calibration ratio: meters per BEV pixel
        self.meters_per_px_x = self.ground_width_m / self.bev_width
        self.meters_per_px_y = self.ground_length_m / self.bev_height

        if self.src_pts is not None and len(self.src_pts) == 4:
            self.compute_homography()

    def set_reference_points(self, src_points: List[List[float]]):
        """Update source perspective points and recompute homography matrix."""
        self.src_pts = np.array(src_points, dtype=np.float32)
        self.compute_homography()

    def compute_homography(self):
        """Compute the 3x3 Projective Homography Matrix H using cv2.getPerspectiveTransform."""
        if self.src_pts is not None and len(self.src_pts) == 4:
            self.H = cv2.getPerspectiveTransform(self.src_pts, self.dst_pts)
            self.H_inv = np.linalg.inv(self.H)

    def warp_to_bird_eye_view(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Warp an input camera perspective image into an orthographic Bird's-Eye View (BEV).
        """
        if self.H is None:
            return None
        return cv2.warpPerspective(image, self.H, (self.bev_width, self.bev_height))

    def image_point_to_ground_metric(self, pt: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """
        Transform a single image point (x, y) into real-world ground coordinates (X_m, Y_m).
        """
        if self.H is None:
            return None
        px_arr = np.array([[[pt[0], pt[1]]]], dtype=np.float32)
        warped_pt = cv2.perspectiveTransform(px_arr, self.H)[0][0]
        x_m = float(warped_pt[0] * self.meters_per_px_x)
        y_m = float(warped_pt[1] * self.meters_per_px_y)
        return (round(x_m, 2), round(y_m, 2))

    def compute_slot_metric_dimensions(self, slot_polygon: List[List[float]]) -> Dict[str, float]:
        """
        Calculate the real-world width and length (in meters) of a slot polygon.
        If homography is available, transforms corners to metric ground space.
        Otherwise, uses standard default calibrated scale.
        """
        pts = np.array(slot_polygon, dtype=np.float32)
        if self.H is not None:
            warped_pts = cv2.perspectiveTransform(pts.reshape(-1, 1, 2), self.H).reshape(-1, 2)
            # Top-left to Top-right width
            w_top = np.linalg.norm(warped_pts[1] - warped_pts[0]) * self.meters_per_px_x
            w_bot = np.linalg.norm(warped_pts[2] - warped_pts[3]) * self.meters_per_px_x
            avg_width = float((w_top + w_bot) / 2.0)

            # Left and right side lengths
            l_left = np.linalg.norm(warped_pts[3] - warped_pts[0]) * self.meters_per_px_y
            l_right = np.linalg.norm(warped_pts[2] - warped_pts[1]) * self.meters_per_px_y
            avg_length = float((l_left + l_right) / 2.0)

            # Ensure width is the shorter dimension and length is the longer dimension
            width = min(avg_width, avg_length)
            length = max(avg_width, avg_length)
        else:
            # Fallback estimation using pixel distances with approximate scale
            w = np.linalg.norm(pts[1] - pts[0])
            l = np.linalg.norm(pts[3] - pts[0])
            scale = 0.015  # default approximate meters per pixel
            width = float(min(w, l) * scale)
            length = float(max(w, l) * scale)

        return {
            "width_m": round(max(width, 1.2), 2),
            "length_m": round(max(length, 2.5), 2),
            "area_sq_m": round(width * length, 2)
        }
