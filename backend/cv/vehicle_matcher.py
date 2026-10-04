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
        Evaluate if a parking space physically and safely fits the vehicle.
        Enforces realistic clearance margins for door swing, vehicle ingress/egress,
        and bumper maneuvering. Evaluates both perpendicular and parallel bay alignments.
        
        :param slot_dimensions: {'width_m': float, 'length_m': float}
        :param vehicle_specs: Dict with 'length_m', 'width_m', 'category', 'name', etc.
        :return: Assessment dict with strict suitability rating and clearance margins
        """
        slot_w = float(slot_dimensions.get("width_m", 2.5))
        slot_l = float(slot_dimensions.get("length_m", 5.0))

        veh_w = float(vehicle_specs.get("width_m", 0.8))
        veh_l = float(vehicle_specs.get("length_m", 2.0))
        cat = str(vehicle_specs.get("category", "bike")).lower()
        veh_name = vehicle_specs.get("name", "Vehicle")
        wheels = vehicle_specs.get("wheels", 2)

        # Determine category-specific minimum and ideal clearances (in meters)
        is_car = (
            cat in ("car", "suv", "sedan", "compact", "van")
            or "car" in veh_name.lower()
            or "suv" in veh_name.lower()
            or "sedan" in veh_name.lower()
            or wheels == 4
        )
        is_auto = (
            cat in ("auto", "erickshaw", "rickshaw")
            or "auto" in veh_name.lower()
            or "rickshaw" in veh_name.lower()
            or wheels == 3
        )

        if is_car:
            # 4-wheelers: driver/passenger door opening space is mandatory
            min_width_clearance = 0.50   # ~1.64 ft total width clearance
            min_length_clearance = 0.40  # ~1.31 ft total length buffer
            ideal_width_clearance = 0.80 # ~2.62 ft comfortable door opening
            ideal_length_clearance = 0.70
            category_label = "Car/SUV"
        elif is_auto:
            # 3-wheelers: passenger entry/exit clearance
            min_width_clearance = 0.35   # ~1.15 ft total width clearance
            min_length_clearance = 0.25  # ~0.82 ft length buffer
            ideal_width_clearance = 0.60
            ideal_length_clearance = 0.45
            category_label = "Auto Rickshaw"
        else:
            # 2-wheelers: side-stand deployment and rider dismount
            min_width_clearance = 0.25   # ~0.82 ft total width clearance
            min_length_clearance = 0.15  # ~0.49 ft length buffer
            ideal_width_clearance = 0.50
            ideal_length_clearance = 0.35
            category_label = "Two-Wheeler"

        # Check Orientation 1 (Standard: slot_w aligns with veh_w, slot_l with veh_l)
        w_margin_1 = round(slot_w - veh_w, 2)
        l_margin_1 = round(slot_l - veh_l, 2)
        fits_1 = (w_margin_1 >= min_width_clearance) and (l_margin_1 >= min_length_clearance)

        # Check Orientation 2 (Parallel / Transverse: slot_l aligns with veh_w, slot_w with veh_l)
        w_margin_2 = round(slot_l - veh_w, 2)
        l_margin_2 = round(slot_w - veh_l, 2)
        fits_2 = (w_margin_2 >= min_width_clearance) and (l_margin_2 >= min_length_clearance)

        if fits_1:
            active_w_margin = w_margin_1
            active_l_margin = l_margin_1
            is_suitable = True
        elif fits_2:
            active_w_margin = w_margin_2
            active_l_margin = l_margin_2
            is_suitable = True
        else:
            # Neither orientation fits safely
            is_suitable = False
            # Report the orientation with the smallest deficit
            deficit_1 = max(min_width_clearance - w_margin_1, 0) + max(min_length_clearance - l_margin_1, 0)
            deficit_2 = max(min_width_clearance - w_margin_2, 0) + max(min_length_clearance - l_margin_2, 0)
            if deficit_1 <= deficit_2:
                active_w_margin = w_margin_1
                active_l_margin = l_margin_1
            else:
                active_w_margin = w_margin_2
                active_l_margin = l_margin_2

        # Convert to imperial feet for clean user display
        slot_w_ft = round(slot_w * 3.28084, 1)
        slot_l_ft = round(slot_l * 3.28084, 1)
        veh_w_ft = round(veh_w * 3.28084, 1)
        veh_l_ft = round(veh_l * 3.28084, 1)
        width_margin_ft = round(active_w_margin * 3.28084, 1)
        length_margin_ft = round(active_l_margin * 3.28084, 1)
        min_w_ft = round((veh_w + min_width_clearance) * 3.28084, 1)
        min_l_ft = round((veh_l + min_length_clearance) * 3.28084, 1)

        if is_suitable:
            if active_w_margin >= ideal_width_clearance and active_l_margin >= ideal_length_clearance:
                fit_status = "OPTIMAL"
                fit_badge = "🟢 Optimal Fit"
                message = (
                    f"Space ({slot_l_ft} ft × {slot_w_ft} ft / {slot_l}m × {slot_w}m) comfortably fits your {veh_name} "
                    f"with +{width_margin_ft} ft (+{active_w_margin}m) clearance."
                )
            else:
                fit_status = "TIGHT"
                fit_badge = "🟡 Tight Fit"
                message = (
                    f"Space ({slot_l_ft} ft × {slot_w_ft} ft) fits your {veh_name}, but side clearance is tight "
                    f"(+{width_margin_ft} ft / +{active_w_margin}m). Maneuver carefully."
                )
        else:
            missing_reasons = []
            if active_w_margin < 0:
                missing_reasons.append(f"width is {abs(width_margin_ft):.1f} ft ({abs(active_w_margin):.2f}m) narrower than vehicle")
            elif active_w_margin < min_width_clearance:
                missing_reasons.append(f"side clearance is insufficient (only +{width_margin_ft} ft vs min {min_width_clearance*3.28084:.1f} ft needed for door/dismount)")

            if active_l_margin < 0:
                missing_reasons.append(f"length is {abs(length_margin_ft):.1f} ft ({abs(active_l_margin):.2f}m) shorter than vehicle")
            elif active_l_margin < min_length_clearance:
                missing_reasons.append(f"length buffer is insufficient (only +{length_margin_ft} ft)")

            reasons_text = "; ".join(missing_reasons) if missing_reasons else "insufficient clearance"
            fit_status = "TOO_SMALL"
            fit_badge = "❌ Too Narrow / Small"
            message = (
                f"Space ({slot_l_ft} ft × {slot_w_ft} ft) does NOT fit your {veh_name} ({reasons_text}). "
                f"Requires at least {min_l_ft} ft × {min_w_ft} ft. Do not park here."
            )

        return {
            "is_suitable": is_suitable,
            "fit_status": fit_status,
            "fit_badge": fit_badge,
            "category": category_label,
            "slot_width_m": slot_w,
            "slot_length_m": slot_l,
            "slot_width_ft": slot_w_ft,
            "slot_length_ft": slot_l_ft,
            "vehicle_width_m": veh_w,
            "vehicle_length_m": veh_l,
            "vehicle_width_ft": veh_w_ft,
            "vehicle_length_ft": veh_l_ft,
            "width_margin_m": active_w_margin,
            "length_margin_m": active_l_margin,
            "width_margin_ft": width_margin_ft,
            "length_margin_ft": length_margin_ft,
            "min_required_width_ft": min_w_ft,
            "min_required_length_ft": min_l_ft,
            "dims_ft_str": f"{slot_l_ft} ft (L) × {slot_w_ft} ft (W)",
            "vehicle_ft_str": f"{veh_l_ft} ft (L) × {veh_w_ft} ft (W)",
            "clearance_ft_str": f"{width_margin_ft:+.1f} ft",
            "message": message
        }
