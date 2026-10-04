"""
Parking Confidence Scorer & Decision Engine
===========================================
Computes the holistic parking decision using a multi-factor weighted confidence model
and classifies results into three distinct operational states:

    🟢 SUITABLE
    🟡 UNCERTAIN
    🔴 NOT SUITABLE

Enforces non-negotiable safety vetos:
- EMPTY SPACE != PARKING SPACE: If zone confidence is low or zone is invalid,
  the decision MUST be NOT SUITABLE or UNCERTAIN.
- Unverified permission cannot produce a SUITABLE result.
- Occupied, blocked, or undersized spaces immediately receive NOT SUITABLE.
"""

from enum import Enum
from typing import Dict, Any, Optional, Tuple


class DecisionState(str, Enum):
    SUITABLE = "SUITABLE"          # 🟢 All checks verified with high confidence
    UNCERTAIN = "UNCERTAIN"        # 🟡 Physically open but unverified zone/permission
    NOT_SUITABLE = "NOT_SUITABLE"  # 🔴 Invalid zone, occupied, blocked, or too small


class ParkingConfidenceScorer:
    """
    Computes documented weighted confidence and final decision status.

    Formula:
      C_final = (w_zone * C_zone) +
                (w_space * C_space) +
                (w_obstacle * C_obstacle) +
                (w_fit * C_fit) +
                (w_perm * C_perm) +
                (w_det * C_det)

    Weights:
      w_zone     = 0.25 (Plausibility of authentic parking zone)
      w_space    = 0.20 (Absence of overlapping parked vehicles)
      w_obstacle = 0.15 (Absence of pedestrians, bikes, gates, hazards)
      w_fit      = 0.15 (Sufficient physical metric length & width)
      w_perm     = 0.15 (Legality / municipal / database permission)
      w_det      = 0.10 (Mean neural detection / sensor clarity)
      Total      = 1.00
    """

    WEIGHTS = {
        "zone": 0.25,
        "space": 0.20,
        "obstacle": 0.15,
        "fit": 0.15,
        "perm": 0.15,
        "det": 0.10
    }

    # Threshold for 🟢 SUITABLE
    SUITABLE_THRESHOLD = 0.78
    # Threshold for 🟡 UNCERTAIN vs 🔴 NOT SUITABLE
    UNCERTAIN_THRESHOLD = 0.45

    @classmethod
    def evaluate(
        cls,
        zone_result: Dict[str, Any],
        occupancy_status: str,
        obstacle_detected: bool,
        vehicle_fit: Dict[str, Any],
        permission_info: Dict[str, Any],
        detection_confidence: float = 0.85,
        blocked_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate all pipeline factors to produce the final confidence score and 3-state decision.
        """
        # 1. Component Confidence Scores (0.0 to 1.0)
        c_zone = float(zone_result.get("confidence", 0.50))
        is_zone_valid = zone_result.get("is_valid", False)
        zone_status = zone_result.get("status", "UNKNOWN")
        raw_zc = zone_result.get("zone_class", "unknown_area")
        zc_str = raw_zc.value if hasattr(raw_zc, "value") else str(raw_zc)
        if "." in zc_str:
            zc_str = zc_str.split(".", 1)[-1]
        zone_class = zc_str.lower()
        zone_class_display = zc_str.replace("_", " ").title()

        # Space free confidence
        if occupancy_status == "AVAILABLE":
            c_space = 0.95
        elif occupancy_status == "BLOCKED":
            c_space = 0.20
        else:  # OCCUPIED
            c_space = 0.05

        # Obstacle-free confidence
        c_obstacle = 0.15 if obstacle_detected else 0.95

        # Vehicle-fit confidence
        is_fit_suitable = bool(vehicle_fit.get("is_suitable", False))
        fit_margin_m = float(vehicle_fit.get("width_margin_m", 0.0))
        if is_fit_suitable:
            # Bonus for healthy margin
            c_fit = min(1.0, 0.85 + max(0.0, fit_margin_m) * 0.15)
        else:
            c_fit = 0.20

        # Permission confidence
        can_park_legally = bool(permission_info.get("can_park_legally", False))
        is_permission_unknown = bool(permission_info.get("is_unknown", False))
        is_prohibited = bool(permission_info.get("is_prohibited", False))

        if can_park_legally and not is_permission_unknown:
            c_perm = 1.0
        elif is_permission_unknown:
            c_perm = 0.50
        elif is_prohibited:
            c_perm = 0.0
        else:
            c_perm = 0.40

        c_det = max(0.1, min(1.0, float(detection_confidence)))

        # 2. Weighted Sum Calculation
        w = cls.WEIGHTS
        raw_confidence = (
            w["zone"] * c_zone +
            w["space"] * c_space +
            w["obstacle"] * c_obstacle +
            w["fit"] * c_fit +
            w["perm"] * c_perm +
            w["det"] * c_det
        )
        final_confidence = round(max(0.0, min(1.0, raw_confidence)), 2)

        # -------------------------------------------------------------
        # 3. SAFETY VETO EVALUATION (Enforces Core Rules)
        # -------------------------------------------------------------
        veto_reasons = []

        # Veto 1: Invalid zones (Home floor, private house entrance, garden, field, footpath, active road lane)
        if zone_status == "INVALID":
            veto_reasons.append(f"Area identified as {zone_class_display} (Not a valid parking zone).")

        # Veto 2: Occupied by other vehicle
        if occupancy_status == "OCCUPIED":
            veto_reasons.append("Parking space is already occupied by a vehicle.")

        # Veto 3: Physical obstacle blocking space
        if obstacle_detected or occupancy_status == "BLOCKED":
            reason = blocked_reason or "Space is physically obstructed by an obstacle or hazard."
            veto_reasons.append(reason)

        # Veto 4: Vehicle does not fit
        if not is_fit_suitable:
            veto_reasons.append(vehicle_fit.get("message", "Vehicle dimensions exceed available space."))

        # Veto 5: Strict no-parking or prohibited zone
        if is_prohibited:
            veto_reasons.append("Parking is prohibited by municipal regulations at this location.")

        # -------------------------------------------------------------
        # 4. FINAL 3-STATE CLASSIFICATION
        # -------------------------------------------------------------
        if veto_reasons:
            decision = DecisionState.NOT_SUITABLE
            decision_color = "red"
            decision_icon = "🔴"
            headline = "NOT SUITABLE FOR PARKING"
            summary_reason = veto_reasons[0]
        elif not is_zone_valid or is_permission_unknown or zone_status == "UNKNOWN":
            # Physically clear, but zone or permission could not be verified
            decision = DecisionState.UNCERTAIN
            decision_color = "yellow"
            decision_icon = "🟡"
            headline = "PARKING STATUS UNCERTAIN"
            summary_reason = zone_result.get("reason") or "An empty area was detected, but a valid parking zone or permission could not be verified."
        elif final_confidence >= cls.SUITABLE_THRESHOLD and can_park_legally and is_fit_suitable:
            decision = DecisionState.SUITABLE
            decision_color = "green"
            decision_icon = "🟢"
            headline = "PARKING SPACE POTENTIALLY SUITABLE"
            summary_reason = "Designated parking space verified, currently unobstructed, and fits your vehicle."
        else:
            decision = DecisionState.UNCERTAIN
            decision_color = "yellow"
            decision_icon = "🟡"
            headline = "PARKING STATUS UNCERTAIN"
            summary_reason = "System confidence is insufficient to recommend this space safely."

        # 5. Build Comprehensive Checklist for UI Card
        checklist = {
            "zone": {
                "verified": is_zone_valid,
                "label": "Zone: Verified" if is_zone_valid else ("Zone: Invalid" if zone_status == "INVALID" else "Zone: Unverified"),
                "status_icon": "✓" if is_zone_valid else ("✗" if zone_status == "INVALID" else "?"),
                "class_name": zone_class
            },
            "space": {
                "verified": (occupancy_status == "AVAILABLE"),
                "label": "Space: Free" if occupancy_status == "AVAILABLE" else "Space: Occupied",
                "status_icon": "✓" if occupancy_status == "AVAILABLE" else "✗"
            },
            "obstacles": {
                "verified": (not obstacle_detected and occupancy_status != "BLOCKED"),
                "label": "Obstacles: None" if (not obstacle_detected and occupancy_status != "BLOCKED") else "Obstacles: Detected",
                "status_icon": "✓" if (not obstacle_detected and occupancy_status != "BLOCKED") else "⚠️"
            },
            "vehicle_fit": {
                "verified": is_fit_suitable,
                "label": f"Fit: Suitable (+{vehicle_fit.get('clearance_ft_str', '')})" if is_fit_suitable else "Fit: Too Narrow / Too Short",
                "status_icon": "✓" if is_fit_suitable else "✗"
            },
            "permission": {
                "verified": can_park_legally,
                "label": "Permission: Verified" if can_park_legally else ("Permission: Prohibited" if is_prohibited else "Permission: Unknown"),
                "status_icon": "✓" if can_park_legally else ("❌" if is_prohibited else "🟡")
            }
        }

        return {
            "decision": decision,
            "decision_color": decision_color,
            "decision_icon": decision_icon,
            "headline": headline,
            "reason": summary_reason,
            "confidence_score": final_confidence,
            "confidence_percent": int(final_confidence * 100),
            "breakdown": {
                "parking_zone": round(c_zone, 2),
                "space_free": round(c_space, 2),
                "obstacle_free": round(c_obstacle, 2),
                "vehicle_fit": round(c_fit, 2),
                "permission": round(c_perm, 2),
                "detection_clarity": round(c_det, 2)
            },
            "checklist": checklist,
            "can_recommend": (decision == DecisionState.SUITABLE)
        }
