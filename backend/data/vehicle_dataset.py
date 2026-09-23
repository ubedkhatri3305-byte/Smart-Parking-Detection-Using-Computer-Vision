"""
Comprehensive Real-World Vehicle Dimension Dataset — All Types
Covers: Two-Wheelers (Bikes, Scooters, EVs), Three-Wheelers (Auto, E-Rickshaw, Cargo),
        Four-Wheelers (Hatchbacks, Sedans, SUVs, MPVs, Luxury, Commercial)
Used for automatic specification lookup when users register by vehicle name only.
All dimensions in meters (length × width × height, ground clearance).
"""

VEHICLE_DATASET = [

    # =========================================================
    # TWO-WHEELERS — Scooters
    # =========================================================
    {"name": "Honda Activa 6G",         "make": "Honda",          "category": "Scooter",         "wheels": 2, "length_m": 1.83, "width_m": 0.69, "height_m": 1.15, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Honda Activa 125",         "make": "Honda",          "category": "Scooter",         "wheels": 2, "length_m": 1.85, "width_m": 0.70, "height_m": 1.17, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Honda Activa EV",          "make": "Honda",          "category": "Electric Scooter","wheels": 2, "length_m": 1.84, "width_m": 0.70, "height_m": 1.16, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "Honda Dio",                "make": "Honda",          "category": "Scooter",         "wheels": 2, "length_m": 1.80, "width_m": 0.70, "height_m": 1.15, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Honda Grazia 125",         "make": "Honda",          "category": "Scooter",         "wheels": 2, "length_m": 1.84, "width_m": 0.70, "height_m": 1.17, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Honda Cliq",               "make": "Honda",          "category": "Scooter",         "wheels": 2, "length_m": 1.73, "width_m": 0.65, "height_m": 1.06, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "TVS Jupiter",              "make": "TVS",            "category": "Scooter",         "wheels": 2, "length_m": 1.83, "width_m": 0.67, "height_m": 1.15, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "TVS Jupiter 125",          "make": "TVS",            "category": "Scooter",         "wheels": 2, "length_m": 1.83, "width_m": 0.67, "height_m": 1.17, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "TVS Ntorq 125",            "make": "TVS",            "category": "Scooter",         "wheels": 2, "length_m": 1.86, "width_m": 0.71, "height_m": 1.16, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "TVS Wego",                 "make": "TVS",            "category": "Scooter",         "wheels": 2, "length_m": 1.79, "width_m": 0.67, "height_m": 1.14, "clearance_m": 0.14, "icon": "🛵"},
    {"name": "TVS Scooty Pep+",          "make": "TVS",            "category": "Scooter",         "wheels": 2, "length_m": 1.73, "width_m": 0.64, "height_m": 1.10, "clearance_m": 0.14, "icon": "🛵"},
    {"name": "TVS Scooty Zest 110",      "make": "TVS",            "category": "Scooter",         "wheels": 2, "length_m": 1.79, "width_m": 0.65, "height_m": 1.14, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Suzuki Access 125",        "make": "Suzuki",         "category": "Scooter",         "wheels": 2, "length_m": 1.87, "width_m": 0.69, "height_m": 1.16, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Suzuki Burgman Street",    "make": "Suzuki",         "category": "Maxi-Scooter",    "wheels": 2, "length_m": 1.88, "width_m": 0.71, "height_m": 1.14, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Yamaha RayZR 125",         "make": "Yamaha",         "category": "Scooter",         "wheels": 2, "length_m": 1.88, "width_m": 0.68, "height_m": 1.19, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Yamaha Fascino 125",       "make": "Yamaha",         "category": "Scooter",         "wheels": 2, "length_m": 1.84, "width_m": 0.68, "height_m": 1.15, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Yamaha Aerox 155",         "make": "Yamaha",         "category": "Maxi-Scooter",    "wheels": 2, "length_m": 1.93, "width_m": 0.74, "height_m": 1.19, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Hero Destini 125",         "make": "Hero",           "category": "Scooter",         "wheels": 2, "length_m": 1.84, "width_m": 0.69, "height_m": 1.13, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Hero Pleasure Plus 110",   "make": "Hero",           "category": "Scooter",         "wheels": 2, "length_m": 1.82, "width_m": 0.68, "height_m": 1.12, "clearance_m": 0.14, "icon": "🛵"},
    {"name": "Hero Maestro Edge 125",    "make": "Hero",           "category": "Scooter",         "wheels": 2, "length_m": 1.86, "width_m": 0.72, "height_m": 1.13, "clearance_m": 0.15, "icon": "🛵"},
    {"name": "Vespa SXL 150",            "make": "Vespa",          "category": "Premium Scooter", "wheels": 2, "length_m": 1.86, "width_m": 0.73, "height_m": 1.19, "clearance_m": 0.14, "icon": "🛵"},
    {"name": "Vespa VXL 150",            "make": "Vespa",          "category": "Premium Scooter", "wheels": 2, "length_m": 1.86, "width_m": 0.73, "height_m": 1.19, "clearance_m": 0.14, "icon": "🛵"},

    # =========================================================
    # TWO-WHEELERS — Commuter Motorcycles
    # =========================================================
    {"name": "Honda CD 110 Dream",       "make": "Honda",          "category": "Commuter",        "wheels": 2, "length_m": 2.04, "width_m": 0.73, "height_m": 1.07, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "Honda Shine 100",          "make": "Honda",          "category": "Commuter",        "wheels": 2, "length_m": 1.95, "width_m": 0.75, "height_m": 1.05, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "Honda Shine 125",          "make": "Honda",          "category": "Commuter",        "wheels": 2, "length_m": 2.04, "width_m": 0.73, "height_m": 1.11, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "Honda SP 125",             "make": "Honda",          "category": "Commuter",        "wheels": 2, "length_m": 2.02, "width_m": 0.78, "height_m": 1.08, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "Honda Livo",               "make": "Honda",          "category": "Commuter",        "wheels": 2, "length_m": 2.02, "width_m": 0.75, "height_m": 1.11, "clearance_m": 0.16, "icon": "🏍️"},
    {"name": "Honda Unicorn",            "make": "Honda",          "category": "Commuter",        "wheels": 2, "length_m": 2.08, "width_m": 0.75, "height_m": 1.10, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Hero Splendor Plus",       "make": "Hero",           "category": "Commuter",        "wheels": 2, "length_m": 2.00, "width_m": 0.72, "height_m": 1.05, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "Hero HF Deluxe",           "make": "Hero",           "category": "Commuter",        "wheels": 2, "length_m": 1.96, "width_m": 0.72, "height_m": 1.04, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "Hero HF 100",              "make": "Hero",           "category": "Commuter",        "wheels": 2, "length_m": 1.92, "width_m": 0.71, "height_m": 1.03, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "Hero Glamour",             "make": "Hero",           "category": "Commuter",        "wheels": 2, "length_m": 2.05, "width_m": 0.74, "height_m": 1.07, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "Hero Passion Plus",        "make": "Hero",           "category": "Commuter",        "wheels": 2, "length_m": 2.02, "width_m": 0.73, "height_m": 1.06, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "Hero Super Splendor",      "make": "Hero",           "category": "Commuter",        "wheels": 2, "length_m": 2.07, "width_m": 0.73, "height_m": 1.10, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Bajaj Platina 110",        "make": "Bajaj",          "category": "Commuter",        "wheels": 2, "length_m": 2.00, "width_m": 0.71, "height_m": 1.10, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "Bajaj CT100",              "make": "Bajaj",          "category": "Commuter",        "wheels": 2, "length_m": 1.97, "width_m": 0.72, "height_m": 1.07, "clearance_m": 0.15, "icon": "🏍️"},
    {"name": "TVS Raider 125",           "make": "TVS",            "category": "Commuter",        "wheels": 2, "length_m": 2.07, "width_m": 0.78, "height_m": 1.02, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "TVS Sport",                "make": "TVS",            "category": "Commuter",        "wheels": 2, "length_m": 1.98, "width_m": 0.73, "height_m": 1.07, "clearance_m": 0.16, "icon": "🏍️"},
    {"name": "Yamaha FZ-S FI",           "make": "Yamaha",         "category": "Street",          "wheels": 2, "length_m": 1.99, "width_m": 0.78, "height_m": 1.08, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Yamaha FZ-X",              "make": "Yamaha",         "category": "Street",          "wheels": 2, "length_m": 2.02, "width_m": 0.80, "height_m": 1.11, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Yamaha Saluto 125",        "make": "Yamaha",         "category": "Commuter",        "wheels": 2, "length_m": 1.98, "width_m": 0.73, "height_m": 1.07, "clearance_m": 0.16, "icon": "🏍️"},

    # =========================================================
    # TWO-WHEELERS — Sports & Performance
    # =========================================================
    {"name": "Yamaha YZF R15 V4",        "make": "Yamaha",         "category": "Sports",          "wheels": 2, "length_m": 1.99, "width_m": 0.72, "height_m": 1.13, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Yamaha YZF R15M",          "make": "Yamaha",         "category": "Sports",          "wheels": 2, "length_m": 1.99, "width_m": 0.72, "height_m": 1.13, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Yamaha MT-15 V2",          "make": "Yamaha",         "category": "Naked Sports",    "wheels": 2, "length_m": 2.01, "width_m": 0.80, "height_m": 1.07, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Yamaha MT-09",             "make": "Yamaha",         "category": "Naked Sports",    "wheels": 2, "length_m": 2.09, "width_m": 0.82, "height_m": 1.12, "clearance_m": 0.13, "icon": "🏍️"},
    {"name": "KTM Duke 200",             "make": "KTM",            "category": "Naked Sports",    "wheels": 2, "length_m": 2.07, "width_m": 0.83, "height_m": 1.10, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "KTM Duke 390",             "make": "KTM",            "category": "Naked Sports",    "wheels": 2, "length_m": 2.07, "width_m": 0.83, "height_m": 1.10, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "KTM Duke 125",             "make": "KTM",            "category": "Naked Sports",    "wheels": 2, "length_m": 2.01, "width_m": 0.71, "height_m": 1.12, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "KTM RC 200",               "make": "KTM",            "category": "Sports",          "wheels": 2, "length_m": 1.97, "width_m": 0.70, "height_m": 1.09, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "KTM RC 390",               "make": "KTM",            "category": "Sports",          "wheels": 2, "length_m": 2.01, "width_m": 0.72, "height_m": 1.10, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "KTM Adventure 390",        "make": "KTM",            "category": "Adventure",       "wheels": 2, "length_m": 2.17, "width_m": 0.87, "height_m": 1.37, "clearance_m": 0.23, "icon": "🏍️"},
    {"name": "Bajaj Pulsar 150",         "make": "Bajaj",          "category": "Sports",          "wheels": 2, "length_m": 2.05, "width_m": 0.76, "height_m": 1.06, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Bajaj Pulsar NS200",       "make": "Bajaj",          "category": "Sports",          "wheels": 2, "length_m": 2.01, "width_m": 0.80, "height_m": 1.07, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Bajaj Pulsar RS200",       "make": "Bajaj",          "category": "Sports",          "wheels": 2, "length_m": 2.01, "width_m": 0.73, "height_m": 1.12, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Bajaj Pulsar 220F",        "make": "Bajaj",          "category": "Sports",          "wheels": 2, "length_m": 2.06, "width_m": 0.76, "height_m": 1.13, "clearance_m": 0.17, "icon": "🏍️"},
    {"name": "Bajaj Dominar 400",        "make": "Bajaj",          "category": "Tourer",          "wheels": 2, "length_m": 2.15, "width_m": 0.83, "height_m": 1.11, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Bajaj Dominar 250",        "make": "Bajaj",          "category": "Tourer",          "wheels": 2, "length_m": 2.15, "width_m": 0.83, "height_m": 1.11, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "TVS Apache RTR 160",       "make": "TVS",            "category": "Sports",          "wheels": 2, "length_m": 2.08, "width_m": 0.73, "height_m": 1.10, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "TVS Apache RTR 200 4V",    "make": "TVS",            "category": "Sports",          "wheels": 2, "length_m": 2.05, "width_m": 0.79, "height_m": 1.10, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "TVS Apache RR 310",        "make": "TVS",            "category": "Sports",          "wheels": 2, "length_m": 2.05, "width_m": 0.73, "height_m": 1.14, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Suzuki Gixxer 150",        "make": "Suzuki",         "category": "Street",          "wheels": 2, "length_m": 2.02, "width_m": 0.80, "height_m": 1.03, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Suzuki Gixxer SF 250",     "make": "Suzuki",         "category": "Sports",          "wheels": 2, "length_m": 2.02, "width_m": 0.75, "height_m": 1.13, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Kawasaki Ninja 300",       "make": "Kawasaki",       "category": "Sports",          "wheels": 2, "length_m": 2.10, "width_m": 0.74, "height_m": 1.10, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Kawasaki Ninja 400",       "make": "Kawasaki",       "category": "Sports",          "wheels": 2, "length_m": 2.06, "width_m": 0.74, "height_m": 1.14, "clearance_m": 0.13, "icon": "🏍️"},
    {"name": "Kawasaki Z400",            "make": "Kawasaki",       "category": "Naked Sports",    "wheels": 2, "length_m": 2.02, "width_m": 0.75, "height_m": 1.04, "clearance_m": 0.13, "icon": "🏍️"},

    # =========================================================
    # TWO-WHEELERS — Cruisers & Adventure
    # =========================================================
    {"name": "Royal Enfield Classic 350","make": "Royal Enfield",  "category": "Cruiser",         "wheels": 2, "length_m": 2.14, "width_m": 0.84, "height_m": 1.09, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Royal Enfield Bullet 350", "make": "Royal Enfield",  "category": "Cruiser",         "wheels": 2, "length_m": 2.11, "width_m": 0.78, "height_m": 1.22, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Royal Enfield Hunter 350", "make": "Royal Enfield",  "category": "Roadster",        "wheels": 2, "length_m": 2.05, "width_m": 0.80, "height_m": 1.05, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Royal Enfield Meteor 350", "make": "Royal Enfield",  "category": "Cruiser",         "wheels": 2, "length_m": 2.14, "width_m": 0.84, "height_m": 1.14, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Royal Enfield Super Meteor 650","make":"Royal Enfield","category":"Cruiser",         "wheels": 2, "length_m": 2.22, "width_m": 0.85, "height_m": 1.14, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Royal Enfield Continental GT 650","make":"Royal Enfield","category":"Cafe Racer",   "wheels": 2, "length_m": 2.12, "width_m": 0.74, "height_m": 1.02, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Royal Enfield Himalayan 450","make":"Royal Enfield",  "category": "Adventure",       "wheels": 2, "length_m": 2.24, "width_m": 0.85, "height_m": 1.31, "clearance_m": 0.25, "icon": "🏍️"},
    {"name": "Royal Enfield Shotgun 650","make": "Royal Enfield",  "category": "Cruiser",         "wheels": 2, "length_m": 2.24, "width_m": 0.89, "height_m": 1.15, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Honda H'ness CB350",        "make": "Honda",          "category": "Cruiser",         "wheels": 2, "length_m": 2.16, "width_m": 0.80, "height_m": 1.10, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Honda CB350RS",            "make": "Honda",          "category": "Roadster",        "wheels": 2, "length_m": 2.13, "width_m": 0.79, "height_m": 1.09, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Bajaj Avenger Street 160", "make": "Bajaj",          "category": "Cruiser",         "wheels": 2, "length_m": 2.17, "width_m": 0.82, "height_m": 1.07, "clearance_m": 0.17, "icon": "🏍️"},
    {"name": "Bajaj Avenger Cruise 220", "make": "Bajaj",          "category": "Cruiser",         "wheels": 2, "length_m": 2.22, "width_m": 0.84, "height_m": 1.09, "clearance_m": 0.17, "icon": "🏍️"},
    {"name": "Jawa 42",                  "make": "Jawa",           "category": "Cruiser",         "wheels": 2, "length_m": 2.05, "width_m": 0.80, "height_m": 1.09, "clearance_m": 0.19, "icon": "🏍️"},
    {"name": "Jawa Perak",               "make": "Jawa",           "category": "Cruiser",         "wheels": 2, "length_m": 2.10, "width_m": 0.84, "height_m": 1.06, "clearance_m": 0.19, "icon": "🏍️"},
    {"name": "Yezdi Roadster",           "make": "Yezdi",          "category": "Cruiser",         "wheels": 2, "length_m": 2.11, "width_m": 0.82, "height_m": 1.09, "clearance_m": 0.20, "icon": "🏍️"},
    {"name": "Yezdi Adventure",          "make": "Yezdi",          "category": "Adventure",       "wheels": 2, "length_m": 2.17, "width_m": 0.85, "height_m": 1.33, "clearance_m": 0.25, "icon": "🏍️"},
    {"name": "Hero Xpulse 200 4V",       "make": "Hero",           "category": "Adventure",       "wheels": 2, "length_m": 2.22, "width_m": 0.85, "height_m": 1.25, "clearance_m": 0.25, "icon": "🏍️"},
    {"name": "BMW G 310 GS",             "make": "BMW",            "category": "Adventure",       "wheels": 2, "length_m": 2.17, "width_m": 0.83, "height_m": 1.35, "clearance_m": 0.24, "icon": "🏍️"},
    {"name": "BMW G 310 R",              "make": "BMW",            "category": "Naked Sports",    "wheels": 2, "length_m": 2.00, "width_m": 0.80, "height_m": 1.09, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Triumph Speed 400",        "make": "Triumph",        "category": "Roadster",        "wheels": 2, "length_m": 2.11, "width_m": 0.80, "height_m": 1.09, "clearance_m": 0.18, "icon": "🏍️"},
    {"name": "Triumph Tiger 400",        "make": "Triumph",        "category": "Adventure",       "wheels": 2, "length_m": 2.18, "width_m": 0.84, "height_m": 1.33, "clearance_m": 0.22, "icon": "🏍️"},

    # =========================================================
    # TWO-WHEELERS — Electric
    # =========================================================
    {"name": "Ather 450X",               "make": "Ather",          "category": "Electric Scooter","wheels": 2, "length_m": 1.83, "width_m": 0.73, "height_m": 1.25, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "Ather 450S",               "make": "Ather",          "category": "Electric Scooter","wheels": 2, "length_m": 1.83, "width_m": 0.73, "height_m": 1.25, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "Ola S1 Pro",               "make": "Ola",            "category": "Electric Scooter","wheels": 2, "length_m": 1.85, "width_m": 0.70, "height_m": 1.16, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "Ola S1 Air",               "make": "Ola",            "category": "Electric Scooter","wheels": 2, "length_m": 1.86, "width_m": 0.71, "height_m": 1.16, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "Ola S1 X",                 "make": "Ola",            "category": "Electric Scooter","wheels": 2, "length_m": 1.84, "width_m": 0.70, "height_m": 1.15, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "Bajaj Chetak Electric",    "make": "Bajaj",          "category": "Electric Scooter","wheels": 2, "length_m": 1.87, "width_m": 0.76, "height_m": 1.15, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "TVS iQube Electric",       "make": "TVS",            "category": "Electric Scooter","wheels": 2, "length_m": 1.80, "width_m": 0.64, "height_m": 1.14, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "Revolt RV400",             "make": "Revolt",         "category": "Electric Bike",   "wheels": 2, "length_m": 2.08, "width_m": 0.82, "height_m": 1.11, "clearance_m": 0.18, "icon": "⚡"},
    {"name": "Hero Vida V1",             "make": "Hero",           "category": "Electric Scooter","wheels": 2, "length_m": 1.88, "width_m": 0.72, "height_m": 1.18, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "Simple One",               "make": "Simple Energy",  "category": "Electric Scooter","wheels": 2, "length_m": 1.86, "width_m": 0.68, "height_m": 1.18, "clearance_m": 0.16, "icon": "⚡"},
    {"name": "Ultraviolette F77",        "make": "Ultraviolette",  "category": "Electric Bike",   "wheels": 2, "length_m": 2.00, "width_m": 0.78, "height_m": 1.12, "clearance_m": 0.19, "icon": "⚡"},
    {"name": "Okinawa Praise Pro",       "make": "Okinawa",        "category": "Electric Scooter","wheels": 2, "length_m": 1.80, "width_m": 0.67, "height_m": 1.14, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "Ampere Magnus EX",         "make": "Ampere",         "category": "Electric Scooter","wheels": 2, "length_m": 1.78, "width_m": 0.65, "height_m": 1.12, "clearance_m": 0.15, "icon": "⚡"},
    {"name": "Honda Activa EV (2025)",   "make": "Honda",          "category": "Electric Scooter","wheels": 2, "length_m": 1.84, "width_m": 0.70, "height_m": 1.16, "clearance_m": 0.15, "icon": "⚡"},

    # =========================================================
    # THREE-WHEELERS — Auto Rickshaws (Petrol / CNG)
    # =========================================================
    {"name": "Bajaj RE Auto Rickshaw",   "make": "Bajaj",          "category": "Auto Rickshaw",   "wheels": 3, "length_m": 2.63, "width_m": 1.30, "height_m": 1.70, "clearance_m": 0.18, "icon": "🛺"},
    {"name": "Bajaj Compact RE",         "make": "Bajaj",          "category": "Auto Rickshaw",   "wheels": 3, "length_m": 2.63, "width_m": 1.30, "height_m": 1.70, "clearance_m": 0.18, "icon": "🛺"},
    {"name": "Bajaj Maxima Z",           "make": "Bajaj",          "category": "Auto Rickshaw",   "wheels": 3, "length_m": 2.82, "width_m": 1.35, "height_m": 1.78, "clearance_m": 0.18, "icon": "🛺"},
    {"name": "Bajaj Maxima C (Cargo)",   "make": "Bajaj",          "category": "Cargo 3-Wheeler", "wheels": 3, "length_m": 3.23, "width_m": 1.49, "height_m": 1.81, "clearance_m": 0.19, "icon": "🛺"},
    {"name": "Piaggio Ape City",         "make": "Piaggio",        "category": "Auto Rickshaw",   "wheels": 3, "length_m": 2.70, "width_m": 1.37, "height_m": 1.72, "clearance_m": 0.17, "icon": "🛺"},
    {"name": "Piaggio Ape Auto DX",      "make": "Piaggio",        "category": "Auto Rickshaw",   "wheels": 3, "length_m": 2.94, "width_m": 1.47, "height_m": 1.84, "clearance_m": 0.18, "icon": "🛺"},
    {"name": "Piaggio Ape Xtra LDX (Cargo)","make":"Piaggio",      "category": "Cargo 3-Wheeler", "wheels": 3, "length_m": 3.15, "width_m": 1.49, "height_m": 1.77, "clearance_m": 0.18, "icon": "🛺"},
    {"name": "TVS King Deluxe",          "make": "TVS",            "category": "Auto Rickshaw",   "wheels": 3, "length_m": 2.65, "width_m": 1.33, "height_m": 1.74, "clearance_m": 0.17, "icon": "🛺"},
    {"name": "TVS King Duramax",         "make": "TVS",            "category": "Auto Rickshaw",   "wheels": 3, "length_m": 2.65, "width_m": 1.33, "height_m": 1.75, "clearance_m": 0.18, "icon": "🛺"},
    {"name": "TVS King Kargo",           "make": "TVS",            "category": "Cargo 3-Wheeler", "wheels": 3, "length_m": 3.01, "width_m": 1.35, "height_m": 1.72, "clearance_m": 0.18, "icon": "🛺"},
    {"name": "Mahindra Alfa Dx",         "make": "Mahindra",       "category": "Auto Rickshaw",   "wheels": 3, "length_m": 2.98, "width_m": 1.46, "height_m": 1.88, "clearance_m": 0.18, "icon": "🛺"},
    {"name": "Mahindra Alfa Plus (Cargo)","make": "Mahindra",      "category": "Cargo 3-Wheeler", "wheels": 3, "length_m": 3.17, "width_m": 1.46, "height_m": 1.78, "clearance_m": 0.20, "icon": "🛺"},
    {"name": "Atul Gemini",              "make": "Atul",           "category": "Auto Rickshaw",   "wheels": 3, "length_m": 2.75, "width_m": 1.35, "height_m": 1.75, "clearance_m": 0.17, "icon": "🛺"},
    {"name": "Atul Shakti (Cargo)",      "make": "Atul",           "category": "Cargo 3-Wheeler", "wheels": 3, "length_m": 3.18, "width_m": 1.44, "height_m": 1.80, "clearance_m": 0.18, "icon": "🛺"},
    {"name": "Lohia Humsafar",           "make": "Lohia",          "category": "Auto Rickshaw",   "wheels": 3, "length_m": 2.95, "width_m": 1.38, "height_m": 1.75, "clearance_m": 0.17, "icon": "🛺"},

    # =========================================================
    # THREE-WHEELERS — Electric Rickshaws / E-Autos
    # =========================================================
    {"name": "Bajaj RE EV Compact",      "make": "Bajaj",          "category": "Electric Rickshaw","wheels": 3, "length_m": 2.63, "width_m": 1.30, "height_m": 1.70, "clearance_m": 0.18, "icon": "⚡"},
    {"name": "Mahindra Treo",            "make": "Mahindra",       "category": "Electric Rickshaw","wheels": 3, "length_m": 2.77, "width_m": 1.35, "height_m": 1.75, "clearance_m": 0.18, "icon": "⚡"},
    {"name": "Mahindra Treo Yaari",      "make": "Mahindra",       "category": "Electric Rickshaw","wheels": 3, "length_m": 2.77, "width_m": 1.00, "height_m": 1.75, "clearance_m": 0.17, "icon": "⚡"},
    {"name": "Piaggio Ape E-City",       "make": "Piaggio",        "category": "Electric Rickshaw","wheels": 3, "length_m": 2.70, "width_m": 1.37, "height_m": 1.70, "clearance_m": 0.17, "icon": "⚡"},
    {"name": "TVS King EV",              "make": "TVS",            "category": "Electric Rickshaw","wheels": 3, "length_m": 2.65, "width_m": 1.33, "height_m": 1.74, "clearance_m": 0.17, "icon": "⚡"},
    {"name": "Greaves Eltra",            "make": "Greaves",        "category": "Electric Rickshaw","wheels": 3, "length_m": 3.15, "width_m": 1.40, "height_m": 1.75, "clearance_m": 0.17, "icon": "⚡"},
    {"name": "Euler HiLoad EV",          "make": "Euler",          "category": "Electric Cargo 3W","wheels": 3, "length_m": 3.40, "width_m": 1.46, "height_m": 1.95, "clearance_m": 0.19, "icon": "⚡"},
    {"name": "Atul Elite",               "make": "Atul",           "category": "Electric Rickshaw","wheels": 3, "length_m": 2.78, "width_m": 1.00, "height_m": 1.78, "clearance_m": 0.17, "icon": "⚡"},
    {"name": "OSM Rage+",                "make": "OSM",            "category": "Electric Cargo 3W","wheels": 3, "length_m": 3.20, "width_m": 1.44, "height_m": 1.78, "clearance_m": 0.18, "icon": "⚡"},
    {"name": "Standard E-Rickshaw",      "make": "Generic",        "category": "Electric Rickshaw","wheels": 3, "length_m": 2.79, "width_m": 0.99, "height_m": 1.80, "clearance_m": 0.16, "icon": "⚡"},

    # =========================================================
    # FOUR-WHEELERS — Hatchbacks
    # =========================================================
    {"name": "Maruti Suzuki Swift",      "make": "Maruti Suzuki",  "category": "Hatchback",       "wheels": 4, "length_m": 3.86, "width_m": 1.73, "height_m": 1.53, "clearance_m": 0.16, "icon": "🚗"},
    {"name": "Maruti Suzuki Baleno",     "make": "Maruti Suzuki",  "category": "Premium Hatchback","wheels": 4, "length_m": 3.99, "width_m": 1.74, "height_m": 1.50, "clearance_m": 0.17, "icon": "🚗"},
    {"name": "Maruti Suzuki WagonR",     "make": "Maruti Suzuki",  "category": "Hatchback",       "wheels": 4, "length_m": 3.65, "width_m": 1.62, "height_m": 1.67, "clearance_m": 0.18, "icon": "🚗"},
    {"name": "Maruti Suzuki Alto K10",   "make": "Maruti Suzuki",  "category": "Hatchback",       "wheels": 4, "length_m": 3.53, "width_m": 1.53, "height_m": 1.50, "clearance_m": 0.16, "icon": "🚗"},
    {"name": "Maruti Suzuki Celerio",    "make": "Maruti Suzuki",  "category": "Hatchback",       "wheels": 4, "length_m": 3.70, "width_m": 1.60, "height_m": 1.56, "clearance_m": 0.17, "icon": "🚗"},
    {"name": "Maruti Suzuki Ignis",      "make": "Maruti Suzuki",  "category": "Hatchback",       "wheels": 4, "length_m": 3.70, "width_m": 1.69, "height_m": 1.59, "clearance_m": 0.18, "icon": "🚗"},
    {"name": "Hyundai i20",              "make": "Hyundai",        "category": "Premium Hatchback","wheels": 4, "length_m": 4.04, "width_m": 1.78, "height_m": 1.50, "clearance_m": 0.17, "icon": "🚗"},
    {"name": "Hyundai Grand i10 Nios",   "make": "Hyundai",        "category": "Hatchback",       "wheels": 4, "length_m": 3.81, "width_m": 1.68, "height_m": 1.52, "clearance_m": 0.17, "icon": "🚗"},
    {"name": "Tata Tiago",               "make": "Tata",           "category": "Hatchback",       "wheels": 4, "length_m": 3.77, "width_m": 1.65, "height_m": 1.53, "clearance_m": 0.17, "icon": "🚗"},
    {"name": "Tata Tiago EV",            "make": "Tata",           "category": "Electric Hatchback","wheels": 4, "length_m": 3.77, "width_m": 1.65, "height_m": 1.53, "clearance_m": 0.17, "icon": "⚡"},
    {"name": "Tata Punch",               "make": "Tata",           "category": "Micro SUV",       "wheels": 4, "length_m": 3.83, "width_m": 1.74, "height_m": 1.62, "clearance_m": 0.19, "icon": "🚗"},
    {"name": "Tata Altroz",              "make": "Tata",           "category": "Premium Hatchback","wheels": 4, "length_m": 3.99, "width_m": 1.76, "height_m": 1.52, "clearance_m": 0.16, "icon": "🚗"},
    {"name": "Renault Kwid",             "make": "Renault",        "category": "Hatchback",       "wheels": 4, "length_m": 3.68, "width_m": 1.58, "height_m": 1.47, "clearance_m": 0.18, "icon": "🚗"},
    {"name": "Volkswagen Polo",          "make": "Volkswagen",     "category": "Premium Hatchback","wheels": 4, "length_m": 4.07, "width_m": 1.75, "height_m": 1.47, "clearance_m": 0.16, "icon": "🚗"},

    # =========================================================
    # FOUR-WHEELERS — Sedans
    # =========================================================
    {"name": "Honda City",               "make": "Honda",          "category": "Sedan",           "wheels": 4, "length_m": 4.54, "width_m": 1.74, "height_m": 1.48, "clearance_m": 0.16, "icon": "🚗"},
    {"name": "Honda Amaze",              "make": "Honda",          "category": "Compact Sedan",   "wheels": 4, "length_m": 3.99, "width_m": 1.69, "height_m": 1.50, "clearance_m": 0.16, "icon": "🚗"},
    {"name": "Maruti Suzuki Dzire",      "make": "Maruti Suzuki",  "category": "Compact Sedan",   "wheels": 4, "length_m": 3.99, "width_m": 1.73, "height_m": 1.52, "clearance_m": 0.16, "icon": "🚗"},
    {"name": "Hyundai Verna",            "make": "Hyundai",        "category": "Sedan",           "wheels": 4, "length_m": 4.53, "width_m": 1.79, "height_m": 1.47, "clearance_m": 0.16, "icon": "🚗"},
    {"name": "Tata Tigor",               "make": "Tata",           "category": "Compact Sedan",   "wheels": 4, "length_m": 3.99, "width_m": 1.68, "height_m": 1.53, "clearance_m": 0.17, "icon": "🚗"},
    {"name": "Volkswagen Vento",         "make": "Volkswagen",     "category": "Sedan",           "wheels": 4, "length_m": 4.39, "width_m": 1.70, "height_m": 1.47, "clearance_m": 0.16, "icon": "🚗"},
    {"name": "Skoda Slavia",             "make": "Skoda",          "category": "Sedan",           "wheels": 4, "length_m": 4.54, "width_m": 1.75, "height_m": 1.48, "clearance_m": 0.18, "icon": "🚗"},
    {"name": "Toyota Yaris",             "make": "Toyota",         "category": "Sedan",           "wheels": 4, "length_m": 4.42, "width_m": 1.73, "height_m": 1.49, "clearance_m": 0.17, "icon": "🚗"},
    {"name": "Renault Triber",           "make": "Renault",        "category": "Compact MPV",     "wheels": 4, "length_m": 3.99, "width_m": 1.74, "height_m": 1.64, "clearance_m": 0.18, "icon": "🚗"},
    {"name": "Toyota Camry",             "make": "Toyota",         "category": "Sedan",           "wheels": 4, "length_m": 4.88, "width_m": 1.84, "height_m": 1.44, "clearance_m": 0.14, "icon": "🚗"},
    {"name": "Honda Accord",             "make": "Honda",          "category": "Sedan",           "wheels": 4, "length_m": 4.89, "width_m": 1.86, "height_m": 1.45, "clearance_m": 0.14, "icon": "🚗"},

    # =========================================================
    # FOUR-WHEELERS — Compact SUVs
    # =========================================================
    {"name": "Hyundai Creta",            "make": "Hyundai",        "category": "Compact SUV",     "wheels": 4, "length_m": 4.33, "width_m": 1.79, "height_m": 1.63, "clearance_m": 0.19, "icon": "🚙"},
    {"name": "Tata Nexon",               "make": "Tata",           "category": "Compact SUV",     "wheels": 4, "length_m": 3.99, "width_m": 1.80, "height_m": 1.62, "clearance_m": 0.20, "icon": "🚙"},
    {"name": "Tata Nexon EV",            "make": "Tata",           "category": "Electric SUV",    "wheels": 4, "length_m": 3.99, "width_m": 1.80, "height_m": 1.62, "clearance_m": 0.20, "icon": "⚡"},
    {"name": "Maruti Suzuki Brezza",     "make": "Maruti Suzuki",  "category": "Compact SUV",     "wheels": 4, "length_m": 3.99, "width_m": 1.79, "height_m": 1.64, "clearance_m": 0.19, "icon": "🚙"},
    {"name": "Kia Sonet",                "make": "Kia",            "category": "Compact SUV",     "wheels": 4, "length_m": 3.99, "width_m": 1.79, "height_m": 1.64, "clearance_m": 0.21, "icon": "🚙"},
    {"name": "Kia Seltos",               "make": "Kia",            "category": "Compact SUV",     "wheels": 4, "length_m": 4.37, "width_m": 1.80, "height_m": 1.64, "clearance_m": 0.19, "icon": "🚙"},
    {"name": "Volkswagen Taigun",        "make": "Volkswagen",     "category": "Compact SUV",     "wheels": 4, "length_m": 4.22, "width_m": 1.76, "height_m": 1.61, "clearance_m": 0.19, "icon": "🚙"},
    {"name": "Skoda Kushaq",             "make": "Skoda",          "category": "Compact SUV",     "wheels": 4, "length_m": 4.22, "width_m": 1.76, "height_m": 1.61, "clearance_m": 0.18, "icon": "🚙"},
    {"name": "Renault Duster",           "make": "Renault",        "category": "Compact SUV",     "wheels": 4, "length_m": 4.34, "width_m": 1.82, "height_m": 1.69, "clearance_m": 0.21, "icon": "🚙"},
    {"name": "Nissan Magnite",           "make": "Nissan",         "category": "Compact SUV",     "wheels": 4, "length_m": 3.99, "width_m": 1.76, "height_m": 1.57, "clearance_m": 0.20, "icon": "🚙"},
    {"name": "Citroen C3",               "make": "Citroen",        "category": "Hatchback/SUV",   "wheels": 4, "length_m": 3.98, "width_m": 1.74, "height_m": 1.59, "clearance_m": 0.17, "icon": "🚗"},
    {"name": "Toyota Urban Cruiser Hyryder","make":"Toyota",        "category": "Compact SUV",     "wheels": 4, "length_m": 4.37, "width_m": 1.80, "height_m": 1.64, "clearance_m": 0.20, "icon": "🚙"},
    {"name": "Honda Elevate",            "make": "Honda",          "category": "Compact SUV",     "wheels": 4, "length_m": 4.31, "width_m": 1.79, "height_m": 1.65, "clearance_m": 0.22, "icon": "🚙"},
    {"name": "Hyundai Venue",            "make": "Hyundai",        "category": "Compact SUV",     "wheels": 4, "length_m": 3.99, "width_m": 1.77, "height_m": 1.59, "clearance_m": 0.19, "icon": "🚙"},

    # =========================================================
    # FOUR-WHEELERS — Full-Size SUVs & MUVs
    # =========================================================
    {"name": "Mahindra Thar",            "make": "Mahindra",       "category": "SUV/4x4",         "wheels": 4, "length_m": 3.98, "width_m": 1.82, "height_m": 1.84, "clearance_m": 0.22, "icon": "🚙"},
    {"name": "Mahindra Scorpio-N",       "make": "Mahindra",       "category": "Full-Size SUV",   "wheels": 4, "length_m": 4.66, "width_m": 1.92, "height_m": 1.86, "clearance_m": 0.22, "icon": "🚙"},
    {"name": "Mahindra XUV700",          "make": "Mahindra",       "category": "Full-Size SUV",   "wheels": 4, "length_m": 4.70, "width_m": 1.89, "height_m": 1.76, "clearance_m": 0.20, "icon": "🚙"},
    {"name": "Mahindra XUV300",          "make": "Mahindra",       "category": "Compact SUV",     "wheels": 4, "length_m": 3.99, "width_m": 1.82, "height_m": 1.63, "clearance_m": 0.20, "icon": "🚙"},
    {"name": "Mahindra Bolero",          "make": "Mahindra",       "category": "MUV",             "wheels": 4, "length_m": 4.16, "width_m": 1.74, "height_m": 1.92, "clearance_m": 0.18, "icon": "🚙"},
    {"name": "Toyota Fortuner",          "make": "Toyota",         "category": "Full-Size SUV",   "wheels": 4, "length_m": 4.79, "width_m": 1.85, "height_m": 1.83, "clearance_m": 0.22, "icon": "🚙"},
    {"name": "Toyota Innova Crysta",     "make": "Toyota",         "category": "MUV",             "wheels": 4, "length_m": 4.74, "width_m": 1.83, "height_m": 1.79, "clearance_m": 0.17, "icon": "🚙"},
    {"name": "Toyota Innova Hycross",    "make": "Toyota",         "category": "MPV",             "wheels": 4, "length_m": 4.75, "width_m": 1.85, "height_m": 1.80, "clearance_m": 0.18, "icon": "🚙"},
    {"name": "Hyundai Alcazar",          "make": "Hyundai",        "category": "3-Row SUV",       "wheels": 4, "length_m": 4.50, "width_m": 1.79, "height_m": 1.68, "clearance_m": 0.20, "icon": "🚙"},
    {"name": "Kia Carens",               "make": "Kia",            "category": "MPV",             "wheels": 4, "length_m": 4.54, "width_m": 1.80, "height_m": 1.71, "clearance_m": 0.19, "icon": "🚙"},
    {"name": "Tata Safari",              "make": "Tata",           "category": "Full-Size SUV",   "wheels": 4, "length_m": 4.66, "width_m": 1.89, "height_m": 1.79, "clearance_m": 0.20, "icon": "🚙"},
    {"name": "Tata Harrier",             "make": "Tata",           "category": "Compact SUV",     "wheels": 4, "length_m": 4.60, "width_m": 1.89, "height_m": 1.71, "clearance_m": 0.20, "icon": "🚙"},
    {"name": "Maruti Suzuki Ertiga",     "make": "Maruti Suzuki",  "category": "MPV",             "wheels": 4, "length_m": 4.40, "width_m": 1.74, "height_m": 1.69, "clearance_m": 0.18, "icon": "🚙"},
    {"name": "Maruti Suzuki XL6",        "make": "Maruti Suzuki",  "category": "MPV",             "wheels": 4, "length_m": 4.45, "width_m": 1.77, "height_m": 1.71, "clearance_m": 0.18, "icon": "🚙"},
    {"name": "Honda WR-V",               "make": "Honda",          "category": "Compact SUV",     "wheels": 4, "length_m": 4.07, "width_m": 1.73, "height_m": 1.60, "clearance_m": 0.19, "icon": "🚙"},
    {"name": "Ford Endeavour",           "make": "Ford",           "category": "Full-Size SUV",   "wheels": 4, "length_m": 4.93, "width_m": 1.86, "height_m": 1.84, "clearance_m": 0.22, "icon": "🚙"},
    {"name": "Jeep Compass",             "make": "Jeep",           "category": "Compact SUV",     "wheels": 4, "length_m": 4.40, "width_m": 1.86, "height_m": 1.64, "clearance_m": 0.20, "icon": "🚙"},
    {"name": "Jeep Meridian",            "make": "Jeep",           "category": "Full-Size SUV",   "wheels": 4, "length_m": 4.77, "width_m": 1.86, "height_m": 1.74, "clearance_m": 0.20, "icon": "🚙"},

    # =========================================================
    # FOUR-WHEELERS — Luxury
    # =========================================================
    {"name": "BMW 3 Series",             "make": "BMW",            "category": "Luxury Sedan",    "wheels": 4, "length_m": 4.71, "width_m": 1.83, "height_m": 1.44, "clearance_m": 0.14, "icon": "🚘"},
    {"name": "BMW 5 Series",             "make": "BMW",            "category": "Luxury Sedan",    "wheels": 4, "length_m": 4.94, "width_m": 1.87, "height_m": 1.47, "clearance_m": 0.14, "icon": "🚘"},
    {"name": "BMW X1",                   "make": "BMW",            "category": "Luxury SUV",      "wheels": 4, "length_m": 4.50, "width_m": 1.82, "height_m": 1.62, "clearance_m": 0.19, "icon": "🚘"},
    {"name": "BMW X5",                   "make": "BMW",            "category": "Luxury SUV",      "wheels": 4, "length_m": 4.92, "width_m": 2.00, "height_m": 1.75, "clearance_m": 0.22, "icon": "🚘"},
    {"name": "Mercedes-Benz C-Class",    "make": "Mercedes-Benz",  "category": "Luxury Sedan",    "wheels": 4, "length_m": 4.75, "width_m": 1.82, "height_m": 1.44, "clearance_m": 0.14, "icon": "🚘"},
    {"name": "Mercedes-Benz E-Class",    "make": "Mercedes-Benz",  "category": "Luxury Sedan",    "wheels": 4, "length_m": 4.95, "width_m": 1.85, "height_m": 1.47, "clearance_m": 0.14, "icon": "🚘"},
    {"name": "Mercedes-Benz GLC",        "make": "Mercedes-Benz",  "category": "Luxury SUV",      "wheels": 4, "length_m": 4.72, "width_m": 1.89, "height_m": 1.64, "clearance_m": 0.20, "icon": "🚘"},
    {"name": "Audi A4",                  "make": "Audi",           "category": "Luxury Sedan",    "wheels": 4, "length_m": 4.73, "width_m": 1.84, "height_m": 1.43, "clearance_m": 0.13, "icon": "🚘"},
    {"name": "Audi Q3",                  "make": "Audi",           "category": "Luxury SUV",      "wheels": 4, "length_m": 4.48, "width_m": 1.85, "height_m": 1.61, "clearance_m": 0.18, "icon": "🚘"},
    {"name": "Audi Q5",                  "make": "Audi",           "category": "Luxury SUV",      "wheels": 4, "length_m": 4.67, "width_m": 1.89, "height_m": 1.66, "clearance_m": 0.20, "icon": "🚘"},
    {"name": "Volvo XC40",               "make": "Volvo",          "category": "Luxury SUV",      "wheels": 4, "length_m": 4.43, "width_m": 1.86, "height_m": 1.65, "clearance_m": 0.21, "icon": "🚘"},
    {"name": "Lexus ES 300h",            "make": "Lexus",          "category": "Luxury Sedan",    "wheels": 4, "length_m": 4.97, "width_m": 1.87, "height_m": 1.45, "clearance_m": 0.14, "icon": "🚘"},
    {"name": "Land Rover Defender",      "make": "Land Rover",     "category": "Luxury 4x4",      "wheels": 4, "length_m": 4.55, "width_m": 2.00, "height_m": 1.97, "clearance_m": 0.26, "icon": "🚘"},
    {"name": "Range Rover Evoque",       "make": "Land Rover",     "category": "Luxury SUV",      "wheels": 4, "length_m": 4.37, "width_m": 1.90, "height_m": 1.64, "clearance_m": 0.21, "icon": "🚘"},
    {"name": "Porsche Cayenne",          "make": "Porsche",        "category": "Luxury SUV",      "wheels": 4, "length_m": 4.92, "width_m": 1.98, "height_m": 1.70, "clearance_m": 0.21, "icon": "🚘"},

    # =========================================================
    # FOUR-WHEELERS — Electric (4W)
    # =========================================================
    {"name": "Tata Nexon EV Max",        "make": "Tata",           "category": "Electric SUV",    "wheels": 4, "length_m": 3.99, "width_m": 1.80, "height_m": 1.62, "clearance_m": 0.20, "icon": "⚡"},
    {"name": "Tata Curvv EV",            "make": "Tata",           "category": "Electric SUV",    "wheels": 4, "length_m": 4.31, "width_m": 1.81, "height_m": 1.64, "clearance_m": 0.19, "icon": "⚡"},
    {"name": "Tata Avinya EV",           "make": "Tata",           "category": "Electric SUV",    "wheels": 4, "length_m": 4.55, "width_m": 1.90, "height_m": 1.65, "clearance_m": 0.20, "icon": "⚡"},
    {"name": "MG ZS EV",                 "make": "MG",             "category": "Electric SUV",    "wheels": 4, "length_m": 4.31, "width_m": 1.81, "height_m": 1.63, "clearance_m": 0.16, "icon": "⚡"},
    {"name": "Hyundai Ioniq 5",          "make": "Hyundai",        "category": "Electric SUV",    "wheels": 4, "length_m": 4.64, "width_m": 1.89, "height_m": 1.60, "clearance_m": 0.16, "icon": "⚡"},
    {"name": "Kia EV6",                  "make": "Kia",            "category": "Electric SUV",    "wheels": 4, "length_m": 4.70, "width_m": 1.88, "height_m": 1.55, "clearance_m": 0.17, "icon": "⚡"},
    {"name": "BMW iX",                   "make": "BMW",            "category": "Electric SUV",    "wheels": 4, "length_m": 4.95, "width_m": 1.97, "height_m": 1.70, "clearance_m": 0.19, "icon": "⚡"},
    {"name": "Mercedes EQS",             "make": "Mercedes-Benz",  "category": "Electric Sedan",  "wheels": 4, "length_m": 5.22, "width_m": 1.93, "height_m": 1.51, "clearance_m": 0.13, "icon": "⚡"},
    {"name": "Volvo C40 Recharge",       "make": "Volvo",          "category": "Electric SUV",    "wheels": 4, "length_m": 4.44, "width_m": 1.87, "height_m": 1.59, "clearance_m": 0.18, "icon": "⚡"},
]


def search_vehicles(query: str = "", limit: int = 15, wheels=None, category=None):
    """
    Search vehicles in the dataset matching the query string.
    Supports partial name, make, category, or wheel-type searches.
    Can be filtered by wheels (2, 3, 4) and/or category.
    Returns best matches sorted by relevance.
    """
    q = query.strip().lower()

    # Filter dataset by wheels and category first if provided
    dataset = VEHICLE_DATASET
    if wheels is not None and str(wheels).isdigit() and int(wheels) > 0:
        w_val = int(wheels)
        dataset = [v for v in dataset if v.get("wheels") == w_val]
    if category and str(category).strip() and str(category).lower() != "all":
        cat_lower = str(category).strip().lower()
        dataset = [v for v in dataset if cat_lower in v.get("category", "").lower()]

    if not q:
        return dataset[:limit]

    matches = []
    seen = set()

    # 1. Exact name match (highest priority)
    for v in dataset:
        if v["name"].lower() == q and v["name"] not in seen:
            matches.append(v)
            seen.add(v["name"])

    # 2. Name starts with query
    for v in dataset:
        if v["name"] not in seen and v["name"].lower().startswith(q):
            matches.append(v)
            seen.add(v["name"])
            if len(matches) >= limit:
                return matches

    # 3. Query is a substring of name, make, or category
    for v in dataset:
        if v["name"] not in seen:
            if q in v["name"].lower() or q in v["make"].lower() or q in v["category"].lower():
                matches.append(v)
                seen.add(v["name"])
                if len(matches) >= limit:
                    return matches

    # 4. Token-level matching (e.g. "honda cd", "re classic", "swift car", "bajaj auto")
    tokens = [t for t in q.replace("-", " ").split() if len(t) >= 2]
    for token in tokens:
        for v in dataset:
            if v["name"] not in seen:
                if token in v["name"].lower() or token in v["make"].lower() or token in v["category"].lower():
                    matches.append(v)
                    seen.add(v["name"])
                    if len(matches) >= limit:
                        return matches

    # 5. Wheel-count keyword fallback (if not already filtered)
    if not matches and (wheels is None or not str(wheels).isdigit() or int(wheels) <= 0):
        if any(k in q for k in ["auto", "rickshaw", "three", "tuk", "e-rick", "erick"]):
            matches = [v for v in VEHICLE_DATASET if v["wheels"] == 3][:limit]
        elif any(k in q for k in ["car", "four wheel", "4w", "suv", "sedan", "hatch"]):
            matches = [v for v in VEHICLE_DATASET if v["wheels"] == 4][:limit]
        elif any(k in q for k in ["bike", "two wheel", "scooter", "motorcycle", "moped"]):
            matches = [v for v in VEHICLE_DATASET if v["wheels"] == 2][:limit]

    return matches[:limit]


def lookup_vehicle(name: str):
    """
    Get vehicle dimensions by name only.
    Returns exact match → fuzzy match → category heuristic → default fallback.
    Works for ANY vehicle name across 2-wheelers, 3-wheelers, and 4-wheelers.
    """
    if not name:
        return {
            "name": "Standard Two-Wheeler", "make": "Generic",
            "category": "Commuter", "wheels": 2,
            "length_m": 2.02, "width_m": 0.74, "height_m": 1.08,
            "clearance_m": 0.16, "icon": "🏍️"
        }
    clean = name.strip().lower()

    # 1. Exact match
    for v in VEHICLE_DATASET:
        if v["name"].lower() == clean:
            return v

    # 2. Prefix or substring match on name
    for v in VEHICLE_DATASET:
        n = v["name"].lower()
        if n.startswith(clean) or clean in n:
            return v

    # 3. Token-level match
    tokens = [t for t in clean.replace("-", " ").split() if len(t) >= 2]
    for t in tokens:
        for v in VEHICLE_DATASET:
            if t in v["name"].lower() or t in v["make"].lower():
                return v

    # 4. Smart heuristics by keyword — 3-Wheelers first (most distinctive)
    three_w_keywords = [
        "auto", "rickshaw", "tuk", "ape", "piaggio", "atul", "re auto",
        "bajaj re", "tvs king", "mahindra alfa", "e-rickshaw", "erickshaw",
        "e rickshaw", "euler", "osm rage", "greaves", "treo", "lohia"
    ]
    if any(k in clean for k in three_w_keywords):
        return {
            "name": name.strip().title(), "make": "Auto Rickshaw",
            "category": "Auto Rickshaw", "wheels": 3,
            "length_m": 3.30, "width_m": 1.40, "height_m": 1.75,
            "clearance_m": 0.17, "icon": "🛺"
        }

    # Luxury 4-Wheelers
    luxury_keywords = [
        "bmw", "mercedes", "audi", "volvo", "lexus", "porsche", "bentley",
        "jaguar", "land rover", "range rover", "lamborghini", "ferrari", "rolls"
    ]
    if any(k in clean for k in luxury_keywords):
        return {
            "name": name.strip().title(), "make": "Luxury",
            "category": "Luxury Car", "wheels": 4,
            "length_m": 4.80, "width_m": 1.88, "height_m": 1.50,
            "clearance_m": 0.15, "icon": "🚘"
        }

    # Full-Size SUV / MUV
    suv_full_keywords = [
        "fortuner", "endeavour", "pajero", "prado", "land cruiser", "innova",
        "crysta", "hycross", "scorpio", "thar", "xuv700", "safari", "harrier",
        "bolero", "compass", "meridian", "defender", "evoque", "cayenne",
        "escalade", "suburban"
    ]
    if any(k in clean for k in suv_full_keywords):
        return {
            "name": name.strip().title(), "make": "SUV",
            "category": "Full-Size SUV", "wheels": 4,
            "length_m": 4.70, "width_m": 1.88, "height_m": 1.80,
            "clearance_m": 0.22, "icon": "🚙"
        }

    # Compact SUV
    compact_suv_keywords = [
        "creta", "nexon", "brezza", "sonet", "seltos", "taigun", "kushaq",
        "duster", "magnite", "venue", "elevate", "alcazar", "wr-v", "carens",
        "hyryder", "urban cruiser", "c3", "punch", "triber"
    ]
    if any(k in clean for k in compact_suv_keywords):
        return {
            "name": name.strip().title(), "make": "SUV",
            "category": "Compact SUV", "wheels": 4,
            "length_m": 4.20, "width_m": 1.80, "height_m": 1.63,
            "clearance_m": 0.20, "icon": "🚙"
        }

    # Sedans
    sedan_keywords = [
        "city", "accord", "verna", "dzire", "amaze", "slavia", "vento",
        "tigor", "yaris", "camry", "civic", "jetta", "octavia", "superb",
        "a4", "c class", "e class", "3 series", "5 series", "corolla"
    ]
    if any(k in clean for k in sedan_keywords):
        return {
            "name": name.strip().title(), "make": "Car",
            "category": "Sedan", "wheels": 4,
            "length_m": 4.50, "width_m": 1.76, "height_m": 1.48,
            "clearance_m": 0.16, "icon": "🚗"
        }

    # Hatchbacks / Small Cars
    hatch_keywords = [
        "swift", "baleno", "wagonr", "alto", "celerio", "ignis", "i20",
        "i10", "tiago", "altroz", "kwid", "polo", "vw up", "fabia",
        "liva", "etios", "glanza"
    ]
    if any(k in clean for k in hatch_keywords):
        return {
            "name": name.strip().title(), "make": "Car",
            "category": "Hatchback", "wheels": 4,
            "length_m": 3.85, "width_m": 1.70, "height_m": 1.52,
            "clearance_m": 0.17, "icon": "🚗"
        }

    # Electric Vehicles (generic)
    ev_keywords = [
        "ev", "electric", "ather", "ola s1", "chetak", "iqube", "nexon ev",
        "mg zs", "ioniq", "kia ev", "tata ev", "curvv", "revolt", "ultraviolette",
        "okinawa", "ampere", "simple one", "vida", "bmw ix", "eqs", "c40"
    ]
    if any(k in clean for k in ev_keywords):
        # Determine if it's a 2W or 4W EV
        if any(k in clean for k in ["scooter", "bike", "ather", "ola", "iqube", "revolt", "okinawa", "ampere", "vida", "ultraviolette", "simple"]):
            return {
                "name": name.strip().title(), "make": "Electric",
                "category": "Electric Scooter", "wheels": 2,
                "length_m": 1.84, "width_m": 0.70, "height_m": 1.15,
                "clearance_m": 0.15, "icon": "⚡"
            }
        return {
            "name": name.strip().title(), "make": "Electric",
            "category": "Electric Vehicle", "wheels": 4,
            "length_m": 4.20, "width_m": 1.80, "height_m": 1.60,
            "clearance_m": 0.18, "icon": "⚡"
        }

    # Scooters
    scooter_keywords = [
        "scoot", "activa", "dio", "jupiter", "access", "burgman", "destini",
        "pleasure", "aerox", "ray", "fascino", "wego", "pep", "scooty",
        "moped", "vespa", "grazia", "cliq"
    ]
    if any(k in clean for k in scooter_keywords):
        return {
            "name": name.strip().title(), "make": "Scooter",
            "category": "Scooter", "wheels": 2,
            "length_m": 1.83, "width_m": 0.69, "height_m": 1.15,
            "clearance_m": 0.15, "icon": "🛵"
        }

    # Cruisers
    cruiser_keywords = [
        "bullet", "classic", "meteor", "enfield", "himalayan", "hunter",
        "harley", "interceptor", "super meteor", "shotgun", "avenger",
        "cruiser", "jawa", "yezdi", "dominar", "cb350"
    ]
    if any(k in clean for k in cruiser_keywords):
        return {
            "name": name.strip().title(), "make": "Royal Enfield",
            "category": "Cruiser", "wheels": 2,
            "length_m": 2.14, "width_m": 0.84, "height_m": 1.12,
            "clearance_m": 0.20, "icon": "🏍️"
        }

    # Sports Bikes
    sports_keywords = [
        "r15", "duke", "rc", "ninja", "rr", "apache", "pulsar", "gixxer",
        "sport", "ktm", "speed", "mt-", "triumph", "kawasaki", "cbr",
        "yzf", "xpulse"
    ]
    if any(k in clean for k in sports_keywords):
        return {
            "name": name.strip().title(), "make": "Sports",
            "category": "Sports", "wheels": 2,
            "length_m": 2.02, "width_m": 0.76, "height_m": 1.10,
            "clearance_m": 0.18, "icon": "🏍️"
        }

    # Generic Car (if user typed "car", "4-wheeler", etc.)
    if any(k in clean for k in ["car", "four wheel", "4w", "vehicle", "auto car"]):
        return {
            "name": name.strip().title(), "make": "Car",
            "category": "Car", "wheels": 4,
            "length_m": 4.10, "width_m": 1.76, "height_m": 1.55,
            "clearance_m": 0.18, "icon": "🚗"
        }

    # 5. Default — treat as commuter bike
    return {
        "name": name.strip().title(), "make": "Two-Wheeler",
        "category": "Commuter", "wheels": 2,
        "length_m": 2.02, "width_m": 0.74, "height_m": 1.08,
        "clearance_m": 0.16, "icon": "🏍️"
    }
