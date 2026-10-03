"""
Vehicle Specification and Parking Space Dimension Matcher
Validates whether a detected available parking space is physically suitable
for the user's specific vehicle type (SUV, Sedan, Compact, Bike) and clearance.
"""

from typing import Dict, Any, Optional


class VehicleProfiles:
    PROFILES = {
        "bike_cruiser": {
            "name": "Cruiser Bike (Royal Enfield / Hunter)",
            "category": "bike",
            "length_m": 2.15,
            "width_m": 0.85,
            "door_clearance_m": 0.20,
            "icon": "🏍️"
        },
        "bike_scooter": {
            "name": "Scooter / Moped (Activa / Jupiter)",
            "category": "bike",
            "length_m": 1.83,
            "width_m": 0.70,
            "door_clearance_m": 0.15,
            "icon": "🛵"
        },
        "bike_commuter": {
            "name": "Commuter Bike (Splendor / Shine)",
            "category": "bike",
            "length_m": 2.00,
            "width_m": 0.72,
            "door_clearance_m": 0.15,
            "icon": "🏍️"
        },
        "bike_sports": {
            "name": "Sports Bike (Yamaha R15 / KTM Duke)",
            "category": "bike",
            "length_m": 2.00,
            "width_m": 0.80,
            "door_clearance_m": 0.20,
            "icon": "🏍️"
        },
        "bike_ev": {
            "name": "Electric Scooter (Ather / Ola)",
            "category": "bike",
            "length_m": 1.83,
            "width_m": 0.73,
            "door_clearance_m": 0.15,
            "icon": "⚡"
        },
        "bike": {
            "name": "Motorcycle / Bike",
            "category": "bike",
            "length_m": 2.0,
            "width_m": 0.8,
            "door_clearance_m": 0.20,
            "icon": "🏍️"
        },
        "suv": {
            "name": "SUV / 4x4",
            "category": "car",
            "length_m": 4.6,
            "width_m": 1.9,
            "door_clearance_m": 0.30,
            "icon": "🚙"
        },
        "sedan": {
            "name": "Sedan",
            "category": "car",
            "length_m": 4.4,
            "width_m": 1.8,
            "door_clearance_m": 0.25,
            "icon": "🚗"
        },
        "compact": {
            "name": "Hatchback / Compact",
            "category": "car",
            "length_m": 3.8,
            "width_m": 1.7,
            "door_clearance_m": 0.20,
            "icon": "🚘"
        },
        "van": {
            "name": "Van / Commercial",
            "category": "car",
            "length_m": 5.2,
            "width_m": 2.1,
            "door_clearance_m": 0.35,
            "icon": "🚐"
        },
        "auto": {
            "name": "Auto Rickshaw (3-Wheeler)",
            "category": "auto",
            "length_m": 2.65,
            "width_m": 1.30,
            "door_clearance_m": 0.18,
            "icon": "🛺"
        },
        "erickshaw": {
            "name": "Electric Rickshaw (3-Wheeler)",
            "category": "auto",
            "length_m": 2.78,
            "width_m": 1.00,
            "door_clearance_m": 0.15,
            "icon": "🛺"
        }
    }


class VehicleMatcher:
    def __init__(self, default_vehicle: str = "suv"):
        self.default_vehicle = default_vehicle.lower()

    def get_vehicle_specs(
        self,
        vehicle_type: str = "suv",
        custom_length: Optional[float] = None,
        custom_width: Optional[float] = None,
        custom_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Retrieve vehicle dimensions and clearances."""
        v_key = vehicle_type.lower()
        base = VehicleProfiles.PROFILES.get(v_key, VehicleProfiles.PROFILES["bike"]).copy()

        if custom_length is not None and custom_length > 0:
            base["length_m"] = round(custom_length, 2)
        if custom_width is not None and custom_width > 0:
            base["width_m"] = round(custom_width, 2)
        if custom_name and custom_name.strip():
            base["name"] = custom_name.strip()

        return base

    def evaluate_fit(
        self,
        slot_dimensions: Dict[str, float],
        vehicle_specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate if slot fits the vehicle.
        :param slot_dimensions: {'width_m': float, 'length_m': float}
        :param vehicle_specs: Dict with 'length_m', 'width_m', 'door_clearance_m'
        :return: Assessment dict with suitability rating and clearance margins
        """
        slot_w = slot_dimensions.get("width_m", 2.5)
        slot_l = slot_dimensions.get("length_m", 5.0)

        veh_w = vehicle_specs.get("width_m", 0.8)
        veh_l = vehicle_specs.get("length_m", 2.0)
        clearance = vehicle_specs.get("door_clearance_m", 0.15)
        is_bike = vehicle_specs.get("category") == "bike" or "bike" in vehicle_specs.get("name", "").lower()

        width_margin = round(slot_w - veh_w, 2)
        length_margin = round(slot_l - veh_l, 2)

        # Real-world imperial measurements in FEET
        slot_w_ft = round(slot_w * 3.28084, 1)
        slot_l_ft = round(slot_l * 3.28084, 1)
        veh_w_ft = round(veh_w * 3.28084, 1)
        veh_l_ft = round(veh_l * 3.28084, 1)
        width_margin_ft = round(width_margin * 3.28084, 1)
        length_margin_ft = round(length_margin * 3.28084, 1)

        # Clearance needed on both sides (left + right)
        ideal_width_margin = round(clearance * 2.0, 2)
        veh_name = vehicle_specs.get("name", "Vehicle")

        if width_margin >= ideal_width_margin and length_margin >= clearance:
            fit_status = "OPTIMAL"
            fit_badge = "🟢 Optimal Fit"
            is_suitable = True
            if is_bike:
                message = f"Space ({slot_l_ft} ft × {slot_w_ft} ft / {slot_l}m × {slot_w}m) fits your {veh_name} with +{width_margin_ft} ft (+{width_margin}m) clearance."
            else:
                message = f"Space ({slot_l_ft} ft × {slot_w_ft} ft / {slot_l}m × {slot_w}m) comfortably fits your {veh_name} with +{width_margin_ft} ft (+{width_margin}m) width clearance."
        elif width_margin >= 0.08 and length_margin >= 0.08:
            fit_status = "TIGHT"
            fit_badge = "🟡 Tight Fit"
            is_suitable = True
            message = f"Space fits your {veh_name}, but side clearance is tight (+{width_margin_ft} ft / +{width_margin}m)."
        else:
            fit_status = "TOO_SMALL"
            fit_badge = "❌ Too Small / Narrow"
            is_suitable = False
            missing = []
            if width_margin < 0:
                missing.append(f"width is {abs(width_margin_ft):.1f} ft ({abs(width_margin):.2f}m) short")
            if length_margin < 0:
                missing.append(f"length is {abs(length_margin_ft):.1f} ft ({abs(length_margin):.2f}m) short")
            message = f"Space ({slot_l_ft} ft × {slot_w_ft} ft) is too small for {veh_name} ({', '.join(missing)})."

        return {
            "is_suitable": is_suitable,
            "fit_status": fit_status,
            "fit_badge": fit_badge,
            "slot_width_m": slot_w,
            "slot_length_m": slot_l,
            "slot_width_ft": slot_w_ft,
            "slot_length_ft": slot_l_ft,
            "vehicle_width_m": veh_w,
            "vehicle_length_m": veh_l,
            "vehicle_width_ft": veh_w_ft,
            "vehicle_length_ft": veh_l_ft,
            "width_margin_m": width_margin,
            "length_margin_m": length_margin,
            "width_margin_ft": width_margin_ft,
            "length_margin_ft": length_margin_ft,
            "ideal_width_margin_m": ideal_width_margin,
            "dims_ft_str": f"{slot_l_ft} ft (L) × {slot_w_ft} ft (W)",
            "vehicle_ft_str": f"{veh_l_ft} ft (L) × {veh_w_ft} ft (W)",
            "clearance_ft_str": f"{width_margin_ft:+.1f} ft",
            "message": message
        }
