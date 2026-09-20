"""
Parking Regulations and Zone Compliance Engine
Validates whether a detected available parking space is legal and permitted
according to local traffic and municipal parking regulations.
"""

from typing import Dict, Any, List


class ParkingRules:
    REGISTERED = "registered"
    PUBLIC_PERMITTED = "public_permitted"
    NO_PARKING = "no_parking"
    PRIVATE_PROPERTY = "private_property"
    LOADING_ZONE = "loading_zone"


class RuleEngine:
    RULES_DATABASE = {
        "registered": {
            "name": "Registered Parking Lot",
            "badge": "Registered ✅",
            "status": "LEGAL",
            "is_permitted": True,
            "color": "#22c55e",
            "description": "Authorized commercial/municipal parking facility with demarcated spaces.",
            "enforcement": "Payment/Pass required. Maximum stay: 24 Hours.",
            "penalty_risk": "None"
        },
        "public_permitted": {
            "name": "Public Permitted Street Parking",
            "badge": "Public Permitted ✅",
            "status": "LEGAL",
            "is_permitted": True,
            "color": "#3b82f6",
            "description": "Standard public road bay. Parking allowed within marked lines.",
            "enforcement": "Time limit: 2 Hours (8:00 AM - 6:00 PM). Free overnight.",
            "penalty_risk": "Low (adhere to time limit)"
        },
        "no_parking": {
            "name": "Strict No-Parking / Tow-Away Zone",
            "badge": "No Parking ❌",
            "status": "ILLEGAL",
            "is_permitted": False,
            "color": "#ef4444",
            "description": "Fire hydrant, driveway access, or marked red curb / diagonal hazard zone.",
            "enforcement": "Immediate tow-away and fine enforced.",
            "penalty_risk": "Severe: Vehicle impoundment & citation"
        },
        "loading_zone": {
            "name": "Commercial Loading Zone",
            "badge": "Loading Only ❌",
            "status": "RESTRICTED",
            "is_permitted": False,
            "color": "#f97316",
            "description": "Active delivery vehicles only. Commercial license required.",
            "enforcement": "Max 15 min active loading.",
            "penalty_risk": "High"
        },
        "private_property": {
            "name": "Private Property / Unknown Permit",
            "badge": "Private / Unknown 🟡",
            "status": "CAUTION",
            "is_permitted": False,
            "color": "#eab308",
            "description": "Private residential or tenant reserved space. Unauthorized parking prohibited.",
            "enforcement": "Wheel clamping or towing at owner's discretion.",
            "penalty_risk": "Moderate"
        }
    }

    @classmethod
    def evaluate_rule(cls, rule_zone: str = "registered", custom_overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate a parking slot against legal rules.
        """
        zone_key = rule_zone.lower()
        rule = cls.RULES_DATABASE.get(zone_key, cls.RULES_DATABASE["public_permitted"]).copy()

        if custom_overrides:
            rule.update(custom_overrides)

        return rule

    @classmethod
    def verify_slot_legality(cls, slot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify if an available slot is legal to park in.
        """
        rule_zone = slot.get("rule_zone", "registered")
        rule_eval = cls.evaluate_rule(rule_zone)

        can_park = (slot.get("status") == "AVAILABLE") and rule_eval["is_permitted"]

        return {
            "can_park_legally": can_park,
            "rule_zone": rule_zone,
            "rule_name": rule_eval["name"],
            "rule_badge": rule_eval["badge"],
            "legal_status": rule_eval["status"],
            "enforcement_notice": rule_eval["enforcement"],
            "penalty_risk": rule_eval["penalty_risk"],
            "color": rule_eval["color"]
        }
