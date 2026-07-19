# Warehouse Layout Feasibility Tool

This Streamlit MVP helps a warehouse planner test whether basic storage, circulation, staging, processing, and support requirements can fit in a rectangular building. It is intended to make early planning conversations faster and assumptions visible.

## What the MVP does

- Collects facility, volume, inventory, storage, and optional-area inputs with guided controls.
- Reports gross and required area, utilization, remaining area or shortfall, and storage positions.
- Classifies a scenario as **Feasible** (≤85%), **Feasible but constrained** (>85% to 100%), or **Not feasible** (>100%).
- Shows an area table, conceptual 2D block layout, and rule-based recommendations.

## How calculations work

Peak volume is daily volume multiplied by the peak factor. Inventory units are peak volume multiplied by the holding-period factor. Storage positions are inventory units divided by average units per position and rounded up. Handling-unit footprint and storage-system density produce storage area; aisle area is a storage-system ratio adjusted relative to a 10-foot aisle. Selected staging, processing, and support areas are then added. Utilization is total required area divided by length × width.

All editable values are centralized in `assumptions.py`. Key assumptions include a 0.25-day buffer for same-day holding, 500 ft² of staging per dock, fixed support-area defaults, processing-area minimums that scale with peak volume, and 4,000 units of planning capacity per dock per shift.

## Install and run

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with:

```bash
pytest
```

## Important limitations

This is a **preliminary planning and feasibility tool**. Its assumptions are generic and must be validated for the specific operation. It is not a replacement for CAD design, detailed material-flow simulation, fire-code review, building-code review, structural engineering, safety validation, equipment-vendor design, or professional warehouse engineering. The conceptual layout is not operationally or legally approved.

## Future roadmap

- Save and compare multiple scenarios.
- Add configurable labor, dock-door, clear-height, and throughput assumptions.
- Represent columns, obstructions, egress, and fire-code constraints.
- Export planning reports and layout data.
- Add validated equipment templates and more detailed flow analysis.
