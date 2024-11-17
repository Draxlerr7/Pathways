import streamlit as st
import requests
import pandas as pd

# Streamlit App Title
st.title("Palmetto Pathways Interactive Emission Calculator")

# API Information
API_URL = "https://ei.palmetto.com/api/v0/bem/calculate"
API_KEY = "tA9gUl2XSW4b2MnGEQig6A4tBQzu0lDOTt5dKXe9ZCc"  # Replace with your actual API key

# Emissions Benchmarks
emission_benchmarks = {
    "2024–2029": 6.75,
    "2030–2034": 3.346640,
    "2035–2039": 2.692183,
    "2040–2049": 2.052731
}

# Input Parameters from the User
st.sidebar.header("Input Parameters")

# Location Inputs
latitude = st.sidebar.number_input("Latitude", value=40.7)
longitude = st.sidebar.number_input("Longitude", value=-74.0)

# Time Range Inputs
from_datetime = st.sidebar.text_input("From Datetime (YYYY-MM-DDTHH:MM:SS)", "2024-01-01T00:00:00")
to_datetime = st.sidebar.text_input("To Datetime (YYYY-MM-DDTHH:MM:SS)", "2029-12-31T23:59:59")

# Building Attributes
st.sidebar.subheader("Building Attributes")
building_type = st.sidebar.selectbox("Building Type", ["Multi-Family (5 to 9 units)", "Multi-Family (10 to 19 units)","Multi-Family (20 to 49 units)", "Multi-Family (50 or more units)"])
floor_area_m2 = st.sidebar.number_input("Floor Area per unit in m²", value=1000.0)  # Default: 1000 ft² ≈ 93 m²
floor_area_ft2 = floor_area_m2 * 10.764  # Convert m² to ft²
num_occupants = st.sidebar.number_input("Number of Occupants per unit", value=3)
num_stories = st.sidebar.number_input("Number of Stories", value=6)

# Lighting
lighting = st.sidebar.selectbox("Lighting Type", ["Incandescent", "LED", "CFL"])

# HVAC Attributes
hvac_heating_fuel = st.sidebar.selectbox("HVAC Heating Fuel", ["Fossil Fuel", "Electric"])
hvac_heating_setpoint = st.sidebar.number_input("HVAC Heating Setpoint (°C)", value=23)
hvac_cooling_setpoint = st.sidebar.number_input("HVAC Cooling Setpoint (°C)", value=18.4)

# Window Type Logic
window_question = st.sidebar.radio("Do you have double-pane high insulation windows?", ["Yes", "No"])
window_type = "Double" if window_question == "Yes" else "Single"

# Roof Insulation Logic
roof_insulation_question = st.sidebar.radio("Do you have a thermally insulated roof?", ["Yes", "No"])
roof_insulation = 30 if roof_insulation_question == "Yes" else 1

# Garage
garage = st.sidebar.selectbox("Garage", ["True", "False"])

# EV Charging
ev_charging = st.sidebar.radio("Do you have EV charging stations?", ["Yes", "No"])
ev_charging_value = True if ev_charging == "Yes" else False

# Washer, Dryer, and Cooking Range
clothes_dryer_fuel = st.sidebar.selectbox("Clothes Dryer Fuel", ["Gas", "Electric"])
clothes_dryer_efficiency = st.sidebar.selectbox("Clothes Dryer Efficiency", ["None","Standard", "EnergyStar"])
clothes_washer_efficiency = st.sidebar.selectbox("Clothes Washer Efficiency", ["None", "Standard", "EnergyStar"])
cooking_range = st.sidebar.selectbox("Cooking Range", ["Gas", "Electric Resistance", "Electric Induction"])

# Storage Attributes
st.sidebar.subheader("Storage Attributes")
storage_capacity_quantile = st.sidebar.number_input(" Battery Storage Capacity Recommendation Quantile (0 to 1)", value=0.3)

# Production Attributes
st.sidebar.subheader("Production Attributes")
production_capacity = st.sidebar.number_input("Production Capacity (kW)", value=0.0)

# Number of Units
num_units = st.sidebar.number_input("Number of Units in Building", value=50)

# Submit Button
if st.sidebar.button("Submit"):
    # Construct Payload
    payload = {
        "location": {"latitude": latitude, "longitude": longitude},
        "parameters": {
            "from_datetime": from_datetime,
            "to_datetime": to_datetime,
            "variables": [
                "emissions",
                "consumption.electricity",
                "consumption.fossil_fuel",
                "costs.fossil_fuel",
                "costs.electricity",
                "emissions.electricity",
                "emissions.fossil_fuel"
            ],
            "group_by": "year"
        },
        "consumption": {
            "attributes": {
                "baseline": [
                    {"name": "building_type", "value": building_type},
                    {"name": "floor_area", "value": floor_area_m2},
                    {"name": "num_occupants", "value": num_occupants},
                    {"name": "num_stories", "value": num_stories},
                    {"name": "lighting", "value": lighting},
                    {"name": "hvac_heating_fuel", "value": hvac_heating_fuel},
                    {"name": "hvac_heating_setpoint", "value": hvac_heating_setpoint},
                    {"name": "hvac_cooling_setpoint", "value": hvac_cooling_setpoint},
                    {"name": "roof_or_ceiling_insulation", "value": roof_insulation},
                    {"name": "window_panes", "value": window_type},
                    {"name": "garage", "value": garage},
                    {"name": "ev_charging", "value": ev_charging_value},
                    {"name": "clothes_dryer_fuel", "value": clothes_dryer_fuel},
                    {"name": "clothes_dryer_efficiency", "value": clothes_dryer_efficiency},
                    {"name": "clothes_washer_efficiency", "value": clothes_washer_efficiency},
                    {"name": "cooking_range", "value": cooking_range}
                ]
            }
        },
        "storage": {
            "attributes": {
                "baseline": [
                    {"name": "capacity_recommendation_quantile", "value": storage_capacity_quantile},
                ]
            }
        },
        "production": {
            "attributes": {
                "baseline": [
                    {"name": "capacity", "value": production_capacity}
                ]
            }
        },
        "costs": {
            "emission_rates": {
                "electricity": {"value": 0.2889, "units": "kgCO2/kWh"},
                "fossil_fuel": {"value": 0.059}
            },
            "utility_rates": {
                "electricity": {"value": 0.2521},
                "fossil_fuel": {"value": 0.0698}
            }
        }
    }

    # API Call
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        # Process Response
        data = response.json()

        # Extract Relevant Data
        intervals = pd.DataFrame(data["data"]["intervals"])
        total_emissions = intervals.query("variable == 'emissions'")["value"].iloc[0] * num_units
        per_sq_ft_emissions = total_emissions / (floor_area_ft2 * num_units)

        # Calculate Excess Emissions for All Benchmarks
        results = []
        for period, benchmark in emission_benchmarks.items():
            excess_emissions = max(0, per_sq_ft_emissions - benchmark) * floor_area_ft2 * num_units
            results.append({"Period": period, "Benchmark (kgCO2/ft²)": benchmark, "Excess Emissions (kgCO2)": excess_emissions})

        # Convert Results to DataFrame for Display
        results_df = pd.DataFrame(results)

        # Display Results
        st.subheader("Results")
        st.metric("Total Emissions (kgCO2)", f"{total_emissions:.2f}")
        st.metric("Per Sq Ft Emissions (kgCO2/ft²)", f"{per_sq_ft_emissions:.4f}")
        st.dataframe(results_df)

    else:
        st.error(f"API Call Failed: {response.status_code}")
        st.write(response.text)
