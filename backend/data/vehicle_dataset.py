"""
Comprehensive Real-World Vehicle Dimension Dataset
Contains official dimensions (Length, Width, Height, Clearance) for popular two-wheelers and vehicles.
Used for automatic specification lookup when users register by vehicle name.
"""

VEHICLE_DATASET = [
    # Royal Enfield
    {
        "name": "Royal Enfield Classic 350",
        "make": "Royal Enfield",
        "category": "Cruiser",
        "length_m": 2.14,
        "width_m": 0.84,
        "height_m": 1.09,
        "clearance_m": 0.20,
        "icon": "🏍️"
    },
    {
        "name": "Royal Enfield Hunter 350",
        "make": "Royal Enfield",
        "category": "Roadster",
        "length_m": 2.05,
        "width_m": 0.80,
        "height_m": 1.05,
        "clearance_m": 0.20,
        "icon": "🏍️"
    },
    {
        "name": "Royal Enfield Meteor 350",
        "make": "Royal Enfield",
        "category": "Cruiser",
        "length_m": 2.14,
        "width_m": 0.84,
        "height_m": 1.14,
        "clearance_m": 0.20,
        "icon": "🏍️"
    },
    {
        "name": "Royal Enfield Bullet 350",
        "make": "Royal Enfield",
        "category": "Cruiser",
        "length_m": 2.11,
        "width_m": 0.78,
        "height_m": 1.22,
        "clearance_m": 0.20,
        "icon": "🏍️"
    },
    {
        "name": "Royal Enfield Himalayan 450",
        "make": "Royal Enfield",
        "category": "Adventure",
        "length_m": 2.24,
        "width_m": 0.85,
        "height_m": 1.31,
        "clearance_m": 0.25,
        "icon": "🏍️"
    },
    {
        "name": "Royal Enfield Continental GT 650",
        "make": "Royal Enfield",
        "category": "Cafe Racer",
        "length_m": 2.12,
        "width_m": 0.74,
        "height_m": 1.02,
        "clearance_m": 0.20,
        "icon": "🏍️"
    },

    # Honda Scooters & Motorcycles
    {
        "name": "Honda Activa 6G",
        "make": "Honda",
        "category": "Scooter",
        "length_m": 1.83,
        "width_m": 0.69,
        "height_m": 1.15,
        "clearance_m": 0.15,
        "icon": "🛵"
    },
    {
        "name": "Honda Activa 125",
        "make": "Honda",
        "category": "Scooter",
        "length_m": 1.85,
        "width_m": 0.70,
        "height_m": 1.17,
        "clearance_m": 0.15,
        "icon": "🛵"
    },
    {
        "name": "Honda Dio",
        "make": "Honda",
        "category": "Scooter",
        "length_m": 1.80,
        "width_m": 0.70,
        "height_m": 1.15,
        "clearance_m": 0.15,
        "icon": "🛵"
    },
    {
        "name": "Honda Shine 125",
        "make": "Honda",
        "category": "Commuter",
        "length_m": 2.04,
        "width_m": 0.73,
        "height_m": 1.11,
        "clearance_m": 0.15,
        "icon": "🏍️"
    },
    {
        "name": "Honda SP 125",
        "make": "Honda",
        "category": "Commuter",
        "length_m": 2.02,
        "width_m": 0.78,
        "height_m": 1.08,
        "clearance_m": 0.15,
        "icon": "🏍️"
    },
    {
        "name": "Honda CD 110 Dream",
        "make": "Honda",
        "category": "Commuter",
        "length_m": 2.04,
        "width_m": 0.73,
        "height_m": 1.07,
        "clearance_m": 0.15,
        "icon": "🏍️"
    },
    {
        "name": "Honda Shine 100",
        "make": "Honda",
        "category": "Commuter",
        "length_m": 1.95,
        "width_m": 0.75,
        "height_m": 1.05,
        "clearance_m": 0.15,
        "icon": "🏍️"
    },
    {
        "name": "Honda Livo",
        "make": "Honda",
        "category": "Commuter",
        "length_m": 2.02,
        "width_m": 0.75,
        "height_m": 1.11,
        "clearance_m": 0.16,
        "icon": "🏍️"
    },
    {
        "name": "Honda Unicorn",
        "make": "Honda",
        "category": "Commuter",
        "length_m": 2.08,
        "width_m": 0.75,
        "height_m": 1.10,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },
    {
        "name": "Honda H'ness CB350",
        "make": "Honda",
        "category": "Cruiser",
        "length_m": 2.16,
        "width_m": 0.80,
        "height_m": 1.10,
        "clearance_m": 0.20,
        "icon": "🏍️"
    },

    # Hero MotoCorp
    {
        "name": "Hero Splendor Plus",
        "make": "Hero",
        "category": "Commuter",
        "length_m": 2.00,
        "width_m": 0.72,
        "height_m": 1.05,
        "clearance_m": 0.15,
        "icon": "🏍️"
    },
    {
        "name": "Hero HF Deluxe",
        "make": "Hero",
        "category": "Commuter",
        "length_m": 1.96,
        "width_m": 0.72,
        "height_m": 1.04,
        "clearance_m": 0.15,
        "icon": "🏍️"
    },
    {
        "name": "Hero Glamour",
        "make": "Hero",
        "category": "Commuter",
        "length_m": 2.05,
        "width_m": 0.74,
        "height_m": 1.07,
        "clearance_m": 0.15,
        "icon": "🏍️"
    },
    {
        "name": "Hero Xpulse 200 4V",
        "make": "Hero",
        "category": "Adventure",
        "length_m": 2.22,
        "width_m": 0.85,
        "height_m": 1.25,
        "clearance_m": 0.25,
        "icon": "🏍️"
    },

    # TVS Motor
    {
        "name": "TVS Jupiter",
        "make": "TVS",
        "category": "Scooter",
        "length_m": 1.83,
        "width_m": 0.67,
        "height_m": 1.15,
        "clearance_m": 0.15,
        "icon": "🛵"
    },
    {
        "name": "TVS Ntorq 125",
        "make": "TVS",
        "category": "Scooter",
        "length_m": 1.86,
        "width_m": 0.71,
        "height_m": 1.16,
        "clearance_m": 0.15,
        "icon": "🛵"
    },
    {
        "name": "TVS Apache RTR 160",
        "make": "TVS",
        "category": "Sports",
        "length_m": 2.08,
        "width_m": 0.73,
        "height_m": 1.10,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },
    {
        "name": "TVS Apache RTR 200 4V",
        "make": "TVS",
        "category": "Sports",
        "length_m": 2.05,
        "width_m": 0.79,
        "height_m": 1.10,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },
    {
        "name": "TVS Raider 125",
        "make": "TVS",
        "category": "Commuter",
        "length_m": 2.07,
        "width_m": 0.78,
        "height_m": 1.02,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },
    {
        "name": "TVS iQube Electric",
        "make": "TVS",
        "category": "Electric Scooter",
        "length_m": 1.80,
        "width_m": 0.64,
        "height_m": 1.14,
        "clearance_m": 0.15,
        "icon": "⚡"
    },

    # Bajaj Auto
    {
        "name": "Bajaj Pulsar 150",
        "make": "Bajaj",
        "category": "Commuter/Sports",
        "length_m": 2.05,
        "width_m": 0.76,
        "height_m": 1.06,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },
    {
        "name": "Bajaj Pulsar NS200",
        "make": "Bajaj",
        "category": "Sports",
        "length_m": 2.01,
        "width_m": 0.80,
        "height_m": 1.07,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },
    {
        "name": "Bajaj Platina 110",
        "make": "Bajaj",
        "category": "Commuter",
        "length_m": 2.00,
        "width_m": 0.71,
        "height_m": 1.10,
        "clearance_m": 0.15,
        "icon": "🏍️"
    },
    {
        "name": "Bajaj Chetak Electric",
        "make": "Bajaj",
        "category": "Electric Scooter",
        "length_m": 1.87,
        "width_m": 0.76,
        "height_m": 1.15,
        "clearance_m": 0.15,
        "icon": "⚡"
    },
    {
        "name": "Bajaj Dominar 400",
        "make": "Bajaj",
        "category": "Tourer",
        "length_m": 2.15,
        "width_m": 0.83,
        "height_m": 1.11,
        "clearance_m": 0.20,
        "icon": "🏍️"
    },

    # Yamaha
    {
        "name": "Yamaha YZF R15 V4",
        "make": "Yamaha",
        "category": "Sports",
        "length_m": 1.99,
        "width_m": 0.72,
        "height_m": 1.13,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },
    {
        "name": "Yamaha MT-15 V2",
        "make": "Yamaha",
        "category": "Naked Sports",
        "length_m": 2.01,
        "width_m": 0.80,
        "height_m": 1.07,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },
    {
        "name": "Yamaha FZ-S FI",
        "make": "Yamaha",
        "category": "Street",
        "length_m": 1.99,
        "width_m": 0.78,
        "height_m": 1.08,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },
    {
        "name": "Yamaha RayZR 125",
        "make": "Yamaha",
        "category": "Scooter",
        "length_m": 1.88,
        "width_m": 0.68,
        "height_m": 1.19,
        "clearance_m": 0.15,
        "icon": "🛵"
    },

    # KTM
    {
        "name": "KTM Duke 200",
        "make": "KTM",
        "category": "Naked Sports",
        "length_m": 2.07,
        "width_m": 0.83,
        "height_m": 1.10,
        "clearance_m": 0.20,
        "icon": "🏍️"
    },
    {
        "name": "KTM Duke 390",
        "make": "KTM",
        "category": "Naked Sports",
        "length_m": 2.07,
        "width_m": 0.83,
        "height_m": 1.10,
        "clearance_m": 0.20,
        "icon": "🏍️"
    },
    {
        "name": "KTM RC 200",
        "make": "KTM",
        "category": "Sports",
        "length_m": 1.97,
        "width_m": 0.70,
        "height_m": 1.09,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },

    # Suzuki
    {
        "name": "Suzuki Access 125",
        "make": "Suzuki",
        "category": "Scooter",
        "length_m": 1.87,
        "width_m": 0.69,
        "height_m": 1.16,
        "clearance_m": 0.15,
        "icon": "🛵"
    },
    {
        "name": "Suzuki Burgman Street",
        "make": "Suzuki",
        "category": "Maxi-Scooter",
        "length_m": 1.88,
        "width_m": 0.71,
        "height_m": 1.14,
        "clearance_m": 0.15,
        "icon": "🛵"
    },
    {
        "name": "Suzuki Gixxer 150",
        "make": "Suzuki",
        "category": "Street",
        "length_m": 2.02,
        "width_m": 0.80,
        "height_m": 1.03,
        "clearance_m": 0.18,
        "icon": "🏍️"
    },

    # Electric Two-Wheelers
    {
        "name": "Ather 450X",
        "make": "Ather",
        "category": "Electric Scooter",
        "length_m": 1.83,
        "width_m": 0.73,
        "height_m": 1.25,
        "clearance_m": 0.15,
        "icon": "⚡"
    },
    {
        "name": "Ola S1 Pro",
        "make": "Ola",
        "category": "Electric Scooter",
        "length_m": 1.85,
        "width_m": 0.70,
        "height_m": 1.16,
        "clearance_m": 0.15,
        "icon": "⚡"
    },
    {
        "name": "Ola S1 Air",
        "make": "Ola",
        "category": "Electric Scooter",
        "length_m": 1.86,
        "width_m": 0.71,
        "height_m": 1.16,
        "clearance_m": 0.15,
        "icon": "⚡"
    },
    {
        "name": "Revolt RV400",
        "make": "Revolt",
        "category": "Electric Bike",
        "length_m": 2.08,
        "width_m": 0.82,
        "height_m": 1.11,
        "clearance_m": 0.18,
        "icon": "⚡"
    },

    # Common Cars / 4-Wheelers
    {
        "name": "Maruti Suzuki Swift",
        "make": "Maruti Suzuki",
        "category": "Hatchback",
        "length_m": 3.86,
        "width_m": 1.73,
        "height_m": 1.53,
        "clearance_m": 0.25,
        "icon": "🚗"
    },
    {
        "name": "Hyundai Creta",
        "make": "Hyundai",
        "category": "Compact SUV",
        "length_m": 4.33,
        "width_m": 1.79,
        "height_m": 1.63,
        "clearance_m": 0.30,
        "icon": "🚙"
    },
    {
        "name": "Tata Nexon",
        "make": "Tata",
        "category": "Compact SUV",
        "length_m": 3.99,
        "width_m": 1.80,
        "height_m": 1.62,
        "clearance_m": 0.30,
        "icon": "🚙"
    },
    {
        "name": "Mahindra Thar",
        "make": "Mahindra",
        "category": "SUV / 4x4",
        "length_m": 3.98,
        "width_m": 1.82,
        "height_m": 1.84,
        "clearance_m": 0.35,
        "icon": "🚙"
    },
    {
        "name": "Toyota Fortuner",
        "make": "Toyota",
        "category": "Full SUV",
        "length_m": 4.79,
        "width_m": 1.85,
        "height_m": 1.83,
        "clearance_m": 0.35,
        "icon": "🚙"
    },
    {
        "name": "Honda City",
        "make": "Honda",
        "category": "Sedan",
        "length_m": 4.54,
        "width_m": 1.74,
        "height_m": 1.48,
        "clearance_m": 0.30,
        "icon": "🚗"
    }
]


def search_vehicles(query: str, limit: int = 15):
    """Search vehicles in the dataset matching the query string."""
    q = query.strip().lower()
    if not q:
        return VEHICLE_DATASET[:limit]
    
    matches = []
    seen = set()

    # 1. Exact or substring match on name, make, or category
    for v in VEHICLE_DATASET:
        v_name = v["name"].lower()
        v_make = v["make"].lower()
        v_cat = v["category"].lower()
        if q in v_name or q in v_make or q in v_cat:
            matches.append(v)
            seen.add(v["name"])
            if len(matches) >= limit:
                return matches

    # 2. Match each search token (e.g. "cd", "ho", "hon", "shine", "activa")
    tokens = [t for t in q.replace("-", " ").split() if len(t) >= 2]
    for token in tokens:
        for v in VEHICLE_DATASET:
            if v["name"] not in seen:
                v_name = v["name"].lower()
                v_make = v["make"].lower()
                if token in v_name or token in v_make:
                    matches.append(v)
                    seen.add(v["name"])
                    if len(matches) >= limit:
                        return matches

    # 3. Fallback: if query matches generic type (scooter, bike, car), provide suggestions
    if not matches:
        if any(k in q for k in ["scoot", "moped"]):
            matches = [v for v in VEHICLE_DATASET if v["category"] == "Scooter"][:limit]
        elif any(k in q for k in ["cruiser", "bullet", "classic"]):
            matches = [v for v in VEHICLE_DATASET if v["category"] == "Cruiser"][:limit]
        elif any(k in q for k in ["commuter", "splendor", "shine", "passion", "cd"]):
            matches = [v for v in VEHICLE_DATASET if v["category"] == "Commuter"][:limit]
        elif any(k in q for k in ["sports", "race", "r15", "duke"]):
            matches = [v for v in VEHICLE_DATASET if v["category"] == "Sports"][:limit]

    return matches


def lookup_vehicle(name: str):
    """Get exact, fuzzy, or category-inferred vehicle specifications by name."""
    if not name:
        return {
            "name": "Standard Two-Wheeler",
            "make": "Standard",
            "category": "Commuter",
            "length_m": 2.02,
            "width_m": 0.74,
            "height_m": 1.08,
            "clearance_m": 0.16,
            "icon": "🏍️"
        }
    clean_name = name.strip().lower()

    # 1. Exact name match
    for v in VEHICLE_DATASET:
        if v["name"].lower() == clean_name:
            return v

    # 2. Substring or prefix match
    for v in VEHICLE_DATASET:
        v_low = v["name"].lower()
        if v_low.startswith(clean_name) or clean_name in v_low:
            return v

    # 3. Token-level match (e.g. user typed "honda cd" or "bullet" or "activa")
    tokens = [t for t in clean_name.replace("-", " ").split() if len(t) >= 2]
    for t in tokens:
        for v in VEHICLE_DATASET:
            if t in v["name"].lower():
                return v

    # 4. Smart Category Heuristics
    # Scooters & Mopeds
    scooter_keywords = ["scoot", "activa", "dio", "jupiter", "access", "burgman", "destini", 
                        "pleasure", "aerox", "ray", "fascino", "ather", "ola", "chetak", "iqube", "vida", "pep"]
    if any(k in clean_name for k in scooter_keywords):
        return {
            "name": name.strip().title(),
            "make": "Scooter",
            "category": "Scooter",
            "length_m": 1.83,
            "width_m": 0.69,
            "height_m": 1.15,
            "clearance_m": 0.15,
            "icon": "🛵"
        }

    # Heavy Cruisers & Adventure
    cruiser_keywords = ["bullet", "classic", "meteor", "enfield", "himalayan", "harley", 
                        "interceptor", "super meteor", "shotgun", "avenger", "cruiser", "jawa", "yezdi"]
    if any(k in clean_name for k in cruiser_keywords):
        return {
            "name": name.strip().title(),
            "make": "Royal Enfield / Cruiser",
            "category": "Cruiser",
            "length_m": 2.14,
            "width_m": 0.84,
            "height_m": 1.12,
            "clearance_m": 0.20,
            "icon": "🏍️"
        }

    # Sports Bikes
    sports_keywords = ["r15", "duke", "rc", "ninja", "rr", "apache", "pulsar", "gixxer", "sport", "ktm", "speed"]
    if any(k in clean_name for k in sports_keywords):
        return {
            "name": name.strip().title(),
            "make": "Sports Bike",
            "category": "Sports",
            "length_m": 2.01,
            "width_m": 0.75,
            "height_m": 1.07,
            "clearance_m": 0.18,
            "icon": "🏍️"
        }

    # Cars
    car_keywords = ["car", "sedan", "suv", "hatchback", "swift", "creta", "baleno", "thar", "wagonr", "city", "brezza"]
    if any(k in clean_name for k in car_keywords):
        return {
            "name": name.strip().title(),
            "make": "Passenger Car",
            "category": "Car",
            "length_m": 4.10,
            "width_m": 1.76,
            "height_m": 1.55,
            "clearance_m": 0.30,
            "icon": "🚗"
        }

    # 5. Default Motorcycle
    return {
        "name": name.strip().title(),
        "make": "Two-Wheeler",
        "category": "Commuter",
        "length_m": 2.02,
        "width_m": 0.74,
        "height_m": 1.08,
        "clearance_m": 0.16,
        "icon": "🏍️"
    }
