import streamlit as st
import requests
import pandas as pd

# Streamlit App Title
st.title("Energy Impact Dashboard")

# API Information
API_URL = "https://ei.palmetto.com/api/v0/bem/calculate"
API_KEY = "tA9gUl2XSW4b2MnGEQig6A4tBQzu0lDOTt5dKXe9ZCc"  # Replace with your actual API key

# Input Parameters from the User
st.sidebar.header("Building Details")

# Location Inputs
latitude = st.sidebar.number_input("Latitude", value=40.7)
longitude = st.sidebar.number_input("Longitude", value=-74.0)

# Time Range Inputs
from_datetime = st.sidebar.text_input("From Datetime (YYYY-MM-DDTHH:MM:SS)", "2023-01-01T00:00:00")
to_datetime = st.sidebar.text_input("To Datetime (YYYY-MM-DDTHH:MM:SS)", "2024-01-01T00:00:00")

# Building Attributes
st.sidebar.subheader("Building Attributes")
building_type = st.sidebar.selectbox("Building Type", ["a", "b", "c", "d"])
floor_area = st.sidebar.number_input("Floor Area (sq ft)", value=1000)
num_occupants = st.sidebar.number_input("Number of Occupants", value=3)
num_stories = st.sidebar.number_input("Number of Stories", value=6)
lighting = st.sidebar.selectbox("Lighting Type", ["a", "b", "c", "d"])
hvac_heating_fuel = st.sidebar.selectbox("HVAC Heating Fuel", ["a", "b", "c", "d"])

# Window Type Logic
window_question = st.sidebar.radio("Do you have double-pane high insulation windows?", ["Yes", "No"])
window_type = "Double" if window_question == "Yes" else "Single"

# Roof Insulation Logic
roof_insulation_question = st.sidebar.radio("Do you have a thermally insulated roof?", ["Yes", "No"])
roof_insulation = 30 if roof_insulation_question == "Yes" else 1

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
                    {"name": "floor_area", "value": floor_area},
                    {"name": "num_occupants", "value": num_occupants},
                    {"name": "num_stories", "value": num_stories},
                    {"name": "lighting", "value": lighting},
                    {"name": "hvac_heating_fuel", "value": hvac_heating_fuel},
                    {"name": "roof_or_ceiling_insulation", "value": roof_insulation},
                    {"name": "window_panes", "value": window_type}
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
        total_energy_consumption = intervals.query("variable == 'consumption.electricity'")["value"].iloc[0] * num_units
        total_emissions = intervals.query("variable == 'emissions'")["value"].iloc[0] * num_units

        # Display Results
        st.subheader("Results")
        st.metric("Total Energy Consumption (kWh)", f"{total_energy_consumption:.2f}")
        st.metric("Total Emissions (kgCO2)", f"{total_emissions:.2f}")
        st.dataframe(intervals)

    else:
        # Handle Errors
        st.error(f"API Call Failed: {response.status_code}")
        st.write(response.text)
