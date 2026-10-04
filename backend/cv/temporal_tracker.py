"""
Temporal Parking Stability Tracker
==================================
Implements multi-frame consistency analysis (Sections 14 & 15).
Prevents single-frame transient false positives by enforcing that a parking spot
must exhibit stable positive validation across multiple consecutive video frames
before granting a SUITABLE status.
"""

from collections import deque
from typing import Dict, Any, List, Optional
import time


class TemporalParkingTracker:
    """
    Tracks decision history across sequential camera frames to assess temporal stability.
    """

    def __init__(self, window_size: int = 5, min_consistent_ratio: float = 0.70):
        """
        :param window_size: Number of frames in the sliding history buffer
        :param min_consistent_ratio: Required proportion of matching frames for stability
        """
        self.window_size = window_size
        self.min_consistent_ratio = min_consistent_ratio
        self._history: deque = deque(maxlen=window_size)
        self._last_update_ts: float = 0.0

    def reset(self):
        """Clear temporal history (e.g. when camera moves or user switches locations)."""
        self._history.clear()
        self._last_update_ts = 0.0

    def add_frame_result(self, frame_decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a frame decision and compute the temporal-stabilized result.
        """
        now = time.time()
        # If camera was idle for > 8 seconds, reset buffer
        if self._last_update_ts > 0 and (now - self._last_update_ts) > 8.0:
            self._history.clear()

        self._last_update_ts = now
        decision = frame_decision.get("decision", "UNCERTAIN")
        conf = float(frame_decision.get("confidence_score", 0.50))

        self._history.append({
            "decision": decision,
            "confidence": conf,
            "timestamp": now,
            "raw_result": frame_decision
        })

        return self.evaluate_stability(frame_decision)

    def evaluate_stability(self, current_frame_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze consistency across buffered frames.
        """
        n_frames = len(self._history)
        if n_frames < 2:
            # First frame - keep as is, but mark temporal sample count
            res = dict(current_frame_result)
            res["temporal_samples"] = n_frames
            res["temporal_stable"] = True
            return res

        decisions = [item["decision"] for item in self._history]
        suitable_count = decisions.count("SUITABLE")
        not_suitable_count = decisions.count("NOT_SUITABLE")
        uncertain_count = decisions.count("UNCERTAIN")

        suitable_ratio = suitable_count / float(n_frames)
        not_suitable_ratio = not_suitable_count / float(n_frames)

        stabilized_result = dict(current_frame_result)
        stabilized_result["temporal_samples"] = n_frames

        # Check for flip-flop instability (e.g. Frame 1 SUITABLE, Frame 2 NOT_SUITABLE)
        has_conflict = (suitable_count > 0 and not_suitable_count > 0)

        if has_conflict:
            stabilized_result["temporal_stable"] = False
            stabilized_result["decision"] = "UNCERTAIN"
            stabilized_result["decision_color"] = "yellow"
            stabilized_result["decision_icon"] = "🟡"
            stabilized_result["headline"] = "PARKING STATUS UNCERTAIN (TEMPORAL INSTABILITY)"
            stabilized_result["reason"] = f"Conflicting readings across consecutive frames ({suitable_count} suitable, {not_suitable_count} not suitable). Re-aligning camera."
            stabilized_result["confidence_score"] = round(float(current_frame_result.get("confidence_score", 0.5)) * 0.85, 2)
            stabilized_result["confidence_percent"] = int(stabilized_result["confidence_score"] * 100)
            stabilized_result["can_recommend"] = False
            return stabilized_result

        # Consistent SUITABLE across required ratio
        if suitable_ratio >= self.min_consistent_ratio:
            stabilized_result["temporal_stable"] = True
            # Apply stability confidence boost (+5% to +10%)
            boosted_conf = min(0.99, float(current_frame_result.get("confidence_score", 0.8)) + 0.05)
            stabilized_result["confidence_score"] = round(boosted_conf, 2)
            stabilized_result["confidence_percent"] = int(boosted_conf * 100)
            return stabilized_result

        # Consistent NOT_SUITABLE
        if not_suitable_ratio >= self.min_consistent_ratio:
            stabilized_result["temporal_stable"] = True
            return stabilized_result

        # Ambiguous / fluctuating frames -> UNCERTAIN
        stabilized_result["temporal_stable"] = False
        stabilized_result["decision"] = "UNCERTAIN"
        stabilized_result["decision_color"] = "yellow"
        stabilized_result["decision_icon"] = "🟡"
        stabilized_result["headline"] = "PARKING STATUS UNCERTAIN"
        stabilized_result["reason"] = "Insufficient temporal consistency across frames. Hold camera steady to verify."
        stabilized_result["can_recommend"] = False
        return stabilized_result
