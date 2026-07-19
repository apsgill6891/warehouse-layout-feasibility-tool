"""Editable planning assumptions for the warehouse feasibility MVP."""

FACILITY_TYPES = [
    "Distribution centre",
    "Sort centre",
    "Fulfilment centre",
    "Cross-dock",
]

HOLDING_DAYS = {"Same day": 0.25, "1 day": 1.0, "2 days": 2.0, "3 days": 3.0}

# Gross floor footprint occupied by one handling unit before storage-system effects.
HANDLING_UNIT_AREA_SQFT = {
    "Standard North American pallet": 13.3,
    "Euro pallet": 10.3,
    "Parcel cage": 10.0,
    "Loose parcel": 2.0,
}

# A smaller factor represents denser storage or vertical use of the building.
STORAGE_SYSTEMS = {
    "Floor storage": {"footprint_factor": 1.00, "base_aisle_ratio": 0.35},
    "Selective pallet racking": {"footprint_factor": 0.55, "base_aisle_ratio": 0.45},
    "Shelving": {"footprint_factor": 0.65, "base_aisle_ratio": 0.30},
}

SUPPORT_AREA_DEFAULTS = {
    "Office": 1_000,
    "Washrooms": 400,
    "Utility room": 300,
    "Forklift charging area": 600,
}

PROCESSING_AREA_DEFAULTS = {
    "Sortation area": 2_000,
    "Packing area": 1_500,
}

DOCK_STAGING_SQFT_PER_DOCK = 500
PROCESSING_SQFT_PER_1000_PEAK_UNITS = 40
DOCK_CAPACITY_UNITS_PER_SHIFT = 4_000
