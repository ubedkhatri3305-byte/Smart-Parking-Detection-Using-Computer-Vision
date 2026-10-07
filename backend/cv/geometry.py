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

    def calibrate_from_camera_and_detections(
        self,
        image_shape: Tuple[int, int],
        detections: List[Dict[str, Any]],
        camera_height_m: float = 1.35,
        camera_pitch_deg: float = 30.0
    ):
        """
        Dynamically computes the projective homography matrix H and metric ground scale
        using real camera pinhole optics and reference physical objects (persons, cars, bikes, chairs).
        Enforces physically-grounded real dimensions in feet and meters.
        """
        h, w = image_shape[:2]
        f = 0.95 * float(h)
        cx = float(w) / 2.0
        cy = float(h) / 2.0

        # Photogrammetry calibration: Extract ground scale samples from detected reference entities
        scale_samples: List[float] = []
        for d in detections:
            bbox = d.get("bbox", [])
            if len(bbox) != 4:
                continue
            x1, y1, x2, y2 = bbox
            bw = float(x2 - x1)
            bh = float(y2 - y1)
            if bw <= 0 or bh <= 0:
                continue

            cname = str(d.get("class_name", "")).lower()
            # Standard ISO / real-world metric dimensions
            if cname == "person" or d.get("is_person", False):
                # Standard human adult height: 1.70 meters (5.58 ft)
                scale_samples.append(1.70 / bh)
            elif cname in ("car", "truck", "bus") or d.get("is_vehicle", False):
                # Standard vehicle width: 1.78 meters (5.84 ft)
                scale_samples.append(1.78 / bw)
            elif cname in ("motorcycle", "bicycle"):
                # Standard two-wheeler length: 2.05 meters (6.72 ft)
                scale_samples.append(2.05 / bw)
            elif cname in ("chair", "couch"):
                # Standard chair height: 0.85 meters (2.79 ft)
                scale_samples.append(0.85 / bh)

        pitch_rad = np.radians(camera_pitch_deg)

        # Ground control trapezoid in normalized image space
        y_near = float(h) * 0.92
        y_far = float(h) * 0.46
        x_near_l = float(w) * 0.10
        x_near_r = float(w) * 0.90
        x_far_l = float(w) * 0.25
        x_far_r = float(w) * 0.75

        src_pts = np.array([
            [x_far_l, y_far],
            [x_far_r, y_far],
            [x_near_r, y_near],
            [x_near_l, y_near]
        ], dtype=np.float32)

        # Physical distance Z using pinhole projection
        phi_near = np.arctan((y_near - cy) / f)
        z_near = camera_height_m / np.tan(pitch_rad + phi_near)
        phi_far = np.arctan((y_far - cy) / f)
        z_far = camera_height_m / np.tan(pitch_rad + phi_far)

        if scale_samples:
            ref_factor = float(np.median(scale_samples))
            ground_w_near = (x_near_r - x_near_l) * ref_factor
            ground_w_far = (x_far_r - x_far_l) * ref_factor
            ground_len = max(float(z_far - z_near), 2.60)
        else:
            ground_w_near = ((x_near_r - x_near_l) / f) * z_near
            ground_w_far = ((x_far_r - x_far_l) / f) * z_far
            ground_len = float(z_far - z_near)

        ground_width_avg = max(1.35, float((ground_w_near + ground_w_far) / 2.0))
        ground_length_val = max(2.50, float(ground_len))

        dst_pts = np.array([
            [0, 0],
            [self.bev_width - 1, 0],
            [self.bev_width - 1, self.bev_height - 1],
            [0, self.bev_height - 1]
        ], dtype=np.float32)

        self.src_pts = src_pts
        self.dst_pts = dst_pts
        self.ground_width_m = ground_width_avg
        self.ground_length_m = ground_length_val
        self.meters_per_px_x = self.ground_width_m / float(self.bev_width)
        self.meters_per_px_y = self.ground_length_m / float(self.bev_height)
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

        final_w = round(max(width, 0.40), 2)
        final_l = round(max(length, 0.80), 2)
        final_area = round(final_w * final_l, 2)
        
        # Real-world imperial dimensions in FEET
        width_ft = round(final_w * 3.28084, 1)
        length_ft = round(final_l * 3.28084, 1)
        area_sq_ft = round(final_area * 10.7639, 1)

        return {
            "width_m": final_w,
            "length_m": final_l,
            "width_ft": width_ft,
            "length_ft": length_ft,
            "area_sq_m": final_area,
            "area_sq_ft": area_sq_ft,
            "dims_ft": f"{length_ft} ft (L) × {width_ft} ft (W)",
            "dims_m": f"{final_l}m (L) × {final_w}m (W)"
        }
