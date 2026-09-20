"""
Visualizer Module for Computer Vision Parking Detection
Renders polished, high-contrast visual overlays, semi-transparent polygons,
status badges, bounding boxes, metric dimensions, and HUD dashboard banner.
"""

from typing import List, Dict, Any, Optional
import cv2
import numpy as np


class ParkingVisualizer:
    @staticmethod
    def annotate_frame(
        image: np.ndarray,
        analyzed_slots: List[Dict[str, Any]],
        detections: List[Dict[str, Any]],
        vehicle_name: str = "SUV",
        selected_slot_id: Optional[str] = None
    ) -> np.ndarray:
        """
        Draw rich computer vision annotations onto the parking image.
        """
        annotated = image.copy()
        overlay = image.copy()
        h, w = annotated.shape[:2]

        # 1. Draw semi-transparent polygons for each parking slot
        for slot in analyzed_slots:
            poly_pts = np.array(slot["polygon"], dtype=np.int32).reshape((-1, 1, 2))
            color = slot["color_bgr"]
            status = slot["status"]

            # Fill slot with color
            alpha = 0.35 if status == "AVAILABLE" else (0.25 if status == "OCCUPIED" else 0.30)
            cv2.fillPoly(overlay, [poly_pts], color)

            # Draw crisp boundary
            cv2.polylines(annotated, [poly_pts], isClosed=True, color=color, thickness=3)

            # Compute slot center for labeling
            M = cv2.moments(poly_pts)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = int(poly_pts[0][0][0]), int(poly_pts[0][0][1])

            # Slot ID badge
            label = f"BAY {slot['id']}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            (tw, th), _ = cv2.getTextSize(label, font, 0.6, 2)
            cv2.rectangle(annotated, (cx - tw // 2 - 6, cy - th - 6), (cx + tw // 2 + 6, cy + 6), (20, 20, 20), -1)
            cv2.putText(annotated, label, (cx - tw // 2, cy), font, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

            # Status subtext
            status_text = slot["status"]
            if slot.get("blocked_reason"):
                status_text = "BLOCKED"
            elif slot["status"] == "AVAILABLE" and "metrics" in slot:
                m = slot["metrics"]
                status_text = f"FREE ({m['width_m']}x{m['length_m']}m)"

            (sw, sh), _ = cv2.getTextSize(status_text, font, 0.45, 1)
            cv2.rectangle(annotated, (cx - sw // 2 - 4, cy + 12), (cx + sw // 2 + 4, cy + 28), color, -1)
            text_color = (0, 0, 0) if status != "OCCUPIED" else (255, 255, 255)
            cv2.putText(annotated, status_text, (cx - sw // 2, cy + 24), font, 0.45, text_color, 1, cv2.LINE_AA)

        # Blend semi-transparent polygons
        cv2.addWeighted(overlay, 0.35, annotated, 0.65, 0, annotated)

        # 2. Draw YOLO Bounding Boxes for detected objects
        for det in detections:
            x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
            cls_name = det["class_name"]
            conf = det["confidence"]
            cat = det["category"]

            box_color = (0, 140, 255) if cat == "vehicle" else ((0, 215, 255) if cat == "obstacle" else (180, 180, 180))
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 2)

            tag = f"{cls_name} {int(conf*100)}%"
            (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(annotated, (x1, y1 - th - 6), (x1 + tw + 6, y1), box_color, -1)
            cv2.putText(annotated, tag, (x1 + 3, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

        # 3. Draw Top HUD Dashboard Banner
        hud_h = 55
        hud_bg = annotated[:hud_h, :].copy()
        cv2.rectangle(hud_bg, (0, 0), (w, hud_h), (18, 22, 30), -1)
        cv2.addWeighted(hud_bg, 0.85, annotated[:hud_h, :], 0.15, 0, annotated[:hud_h, :])
        cv2.line(annotated, (0, hud_h), (w, hud_h), (50, 60, 80), 1)

        # Counts
        total_slots = len(analyzed_slots)
        avail_count = sum(1 for s in analyzed_slots if s["status"] == "AVAILABLE")
        occ_count = sum(1 for s in analyzed_slots if s["status"] == "OCCUPIED")
        block_count = sum(1 for s in analyzed_slots if s["status"] == "BLOCKED")

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(annotated, "SMART PARKING CV", (20, 34), font, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

        # Badges in HUD
        offset_x = 320
        # Available badge
        cv2.circle(annotated, (offset_x, 28), 7, (94, 197, 34), -1)
        cv2.putText(annotated, f"Available: {avail_count}", (offset_x + 15, 34), font, 0.55, (220, 255, 220), 2, cv2.LINE_AA)

        # Occupied badge
        offset_x += 160
        cv2.circle(annotated, (offset_x, 28), 7, (68, 68, 239), -1)
        cv2.putText(annotated, f"Occupied: {occ_count}", (offset_x + 15, 34), font, 0.55, (220, 220, 255), 2, cv2.LINE_AA)

        # Blocked badge
        offset_x += 160
        cv2.circle(annotated, (offset_x, 28), 7, (8, 179, 234), -1)
        cv2.putText(annotated, f"Blocked: {block_count}", (offset_x + 15, 34), font, 0.55, (220, 250, 255), 2, cv2.LINE_AA)

        # Vehicle filter
        offset_x += 160
        if offset_x + 220 < w:
            cv2.putText(annotated, f"Target: {vehicle_name.upper()}", (offset_x, 34), font, 0.55, (160, 210, 255), 2, cv2.LINE_AA)

        return annotated
