import random
from datetime import datetime


class VehicleTelematicsGenerator:
    def __init__(
        self,
        num_vehicles=50,
        min_lat=25.0,
        max_lat=48.0,
        min_lon=-123.0,
        max_lon=-71.0,
        categories=None,
        manufacturers=None,
        year_range=None,
    ):
        self.vehicle_ids = list(range(1, num_vehicles + 1))
        self.min_lat, self.max_lat = min_lat, max_lat
        self.min_lon, self.max_lon = min_lon, max_lon

        self.categories = categories or {
            "passenger": ["sedan", "suv", "hatchback", "minivan"],
            "commercial": ["truck", "van", "pickup"],
            "luxury": ["premium_sedan", "sports_car", "luxury_suv"],
        }

        self.manufacturers = manufacturers or [
            "Toyota",
            "Ford",
            "Honda",
            "BMW",
            "Tesla",
            "Mercedes",
        ]

        self.year_range = year_range or list(range(2018, 2025))
        self.vehicle_profiles = self._initialize_vehicles()

    def _initialize_vehicles(self):
        profiles = {}

        for vid in self.vehicle_ids:
            category = random.choice(list(self.categories.keys()))
            vehicle_type = random.choice(self.categories[category])

            profiles[f"VH{vid:03d}"] = {
                "manufacturer": random.choice(self.manufacturers),
                "year": random.choice(self.year_range),
                "category": category,
                "type": vehicle_type,
                "engine_type": random.choice(
                    ["gasoline", "diesel", "electric", "hybrid"]
                ),
                "total_mileage": random.randint(0, 100000),
            }
        return profiles

    def generate_telemetry(self):
        vehicle_id = f"VH{random.choice(self.vehicle_ids):03d}"
        profile = self.vehicle_profiles[vehicle_id]

        telemetry = {
            "timestamp": datetime.now().isoformat(),
            "vehicle_id": vehicle_id,
            "manufacturer": profile["manufacturer"],
            "year": profile["year"],
            "category": profile["category"],
            "type": profile["type"],
            "engine_type": profile["engine_type"],
            "location": {
                "latitude": round(random.uniform(self.min_lat, self.max_lat), 6),
                "longitude": round(random.uniform(self.min_lon, self.max_lon), 6),
            },
            "speed": round(random.uniform(0, 120), 1),
            "fuel_level": round(random.uniform(0, 100), 1),
            "engine_temp": round(random.uniform(75, 215), 1),
            "tire_pressure": {
                f"tire_{i}": round(random.uniform(28, 35), 1) for i in range(1, 5)
            },
            "battery_voltage": round(random.uniform(11.5, 14.5), 2),
            "engine_rpm": random.randint(700, 6500),
            "odometer": profile["total_mileage"] + round(random.uniform(0, 1000), 1),
            "diagnostic_codes": random.sample(
                ["P0123", "P0456", "P0789", "None"], k=random.randint(0, 2)
            ),
            "maintenance_status": random.choice(["good", "service_due", "warning"]),
            "driver_behavior": {
                "harsh_braking": random.random() < 0.1,
                "rapid_acceleration": random.random() < 0.15,
                "speeding": random.random() < 0.2,
            },
        }

        self.vehicle_profiles[vehicle_id]["total_mileage"] = telemetry["odometer"]
        return telemetry
