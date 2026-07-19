"""Streamlit entry point for the Warehouse Layout Feasibility Tool."""

import pandas as pd
import streamlit as st

from assumptions import FACILITY_TYPES, PROCESSING_AREA_DEFAULTS, SUPPORT_AREA_DEFAULTS
from calculations import calculate_feasibility, generate_recommendations
from layout_generator import create_layout

st.set_page_config(page_title="Warehouse Feasibility", page_icon="🏭", layout="wide")
st.title("🏭 Warehouse Layout Feasibility Tool")
st.caption("Preliminary space planning for a rectangular facility — not an engineering or CAD design.")

with st.sidebar:
    st.header("1 · Facility profile")
    facility_type = st.selectbox("Facility type", FACILITY_TYPES)
    length = st.slider("Warehouse length (ft)", 50, 500, 250, 10)
    width = st.slider("Warehouse width (ft)", 50, 500, 200, 10)
    docks = st.slider("Number of docks", 1, 20, 6)
    st.header("2 · Operating profile")
    daily_volume = st.slider("Daily volume (units)", 1_000, 100_000, 20_000, 1_000)
    peak_factor = st.radio("Peak factor", [1.0, 1.2, 1.5, 2.0], horizontal=True)
    holding_period = st.select_slider("Holding period", ["Same day", "1 day", "2 days", "3 days"], value="1 day")
    shifts = st.radio("Number of shifts", [1, 2, 3], horizontal=True)
    st.header("3 · Storage profile")
    handling_unit = st.selectbox("Handling unit", ["Standard North American pallet", "Euro pallet", "Parcel cage", "Loose parcel"])
    storage_system = st.selectbox("Storage system", ["Floor storage", "Selective pallet racking", "Shelving"])
    quantity = st.slider("Average units per storage position", 1, 100, 20)
    aisle_width = st.slider("Minimum aisle width (ft)", 6, 16, 10)
    st.header("4 · Additional areas")
    area_names = ["Dock staging", "Sortation area", "Packing area", "Office", "Washrooms", "Utility room", "Forklift charging area"]
    selected_areas = {name for name in area_names if st.checkbox(name, value=name in {"Dock staging", "Office", "Washrooms"})}

inputs = dict(facility_type=facility_type, length=length, width=width, docks=docks,
              daily_volume=daily_volume, peak_factor=peak_factor, holding_period=holding_period,
              shifts=shifts, handling_unit=handling_unit, storage_system=storage_system,
              quantity_per_position=quantity, aisle_width=aisle_width, selected_areas=selected_areas)
result = calculate_feasibility(inputs)

status_color = {"Feasible": "green", "Feasible but constrained": "orange", "Not feasible": "red"}[result.status]
st.subheader("Feasibility result")
st.markdown(f"### :{status_color}[{result.status}]")
cols = st.columns(5)
cols[0].metric("Gross warehouse area", f"{result.gross_area:,.0f} ft²")
cols[1].metric("Total required area", f"{result.total_required_area:,.0f} ft²")
cols[2].metric("Remaining / shortfall", f"{result.remaining_area:,.0f} ft²")
cols[3].metric("Space utilization", f"{result.utilization:.1f}%")
cols[4].metric("Storage positions", f"{result.storage_positions:,}")

left, right = st.columns([1, 1.4])
with left:
    st.subheader("Area breakdown")
    table = pd.DataFrame(result.area_breakdown.items(), columns=["Area category", "Required area (ft²)"])
    table["Share of gross area"] = table["Required area (ft²)"] / result.gross_area
    st.dataframe(table.style.format({"Required area (ft²)": "{:,.0f}", "Share of gross area": "{:.1%}"}), hide_index=True, use_container_width=True)
    st.write(f"**Estimated peak daily volume:** {result.peak_daily_volume:,.0f} units")
    st.write(f"**Planning dock capacity:** {result.dock_capacity:,.0f} units/day")
    st.subheader("Recommendations")
    for recommendation in generate_recommendations(result, inputs):
        st.write(f"- {recommendation}")
with right:
    st.subheader("Conceptual 2D block layout")
    st.plotly_chart(create_layout(length, width, result.area_breakdown, docks), use_container_width=True)
    st.caption("Blocks are conceptual and proportional where possible; they are not engineered placements.")

with st.expander("View selected area assumptions"):
    st.write("Dock staging: **500 ft² per selected dock**.")
    for name, value in {**PROCESSING_AREA_DEFAULTS, **SUPPORT_AREA_DEFAULTS}.items():
        if name in selected_areas:
            qualifier = "minimum" if name in PROCESSING_AREA_DEFAULTS else "default"
            st.write(f"{name}: **{value:,.0f} ft² {qualifier}**.")
    st.write("Processing areas scale at 40 ft² per 1,000 peak units when that exceeds their minimum.")

st.warning("This preliminary planning and feasibility tool is not a replacement for CAD design, fire-code review, structural engineering, safety validation, or professional warehouse engineering. The layout is not operationally or legally approved.")
