import matplotlib.pyplot as plt
import streamlit as st
import requests
import pandas as pd

# Streamlit App Title
st.title("Palmetto Pathways Interactive Emission Calculator")

# API Information
API_URL = "https://ei.palmetto.com/api/v0/bem/calculate"
API_KEY = "tA9gUl2XSW4b2MnGEQig6A4tBQzu0lDOTt5dKXe9ZCc"

# Emissions Benchmarks
emission_benchmarks = {
    "2024–2029": 6.75,
    "2030–2034": 3.346640,
    "2035–2039": 2.692183,
    "2040–2049": 2.052731
}

# Convert benchmarks into a timeline
benchmark_timeline = []
for period, value in emission_benchmarks.items():
    start_year, end_year = map(int, period.split("–"))
    benchmark_timeline.extend([(year, value) for year in range(start_year, end_year + 1)])

# Sidebar Input Parameters
st.sidebar.header("Input Parameters")

# Location Inputs
latitude = st.sidebar.number_input("Latitude", value=40.7)
longitude = st.sidebar.number_input("Longitude", value=-74.0)

# Time Range Inputs
year = st.sidebar.number_input("Year (e.g., 2024)", min_value=2024, max_value=2050, value=2024)
from_datetime = f"{year}-01-01T00:00:00"
to_datetime = f"{year}-12-31T23:59:59"

# Building Attributes
st.sidebar.subheader("Building Attributes")
building_type = st.sidebar.selectbox("Building Type", ["Multi-Family (5 to 9 units)", "Multi-Family (10 to 19 units)",
                                                       "Multi-Family (20 to 49 units)", "Multi-Family (50 or more units)"])
floor_area_m2 = st.sidebar.number_input("Floor Area per unit in m²", value=100.0)
floor_area_ft2 = floor_area_m2 * 10.764
num_units = st.sidebar.number_input("Number of Units in Building", value=50)
num_occupants = st.sidebar.number_input("Number of Occupants per unit", value=3)
num_stories = st.sidebar.number_input("Number of Stories", value=6)
vintage = st.sidebar.selectbox("Vintage", ["<1940", "1940s", "1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"])
wall_type = st.sidebar.selectbox("Wall Type", ["Concrete", "Wood Frame", "Brick", "Other"])

# HVAC Attributes
hvac_heating_fuel = st.sidebar.selectbox("HVAC Heating Fuel", ["Fossil Fuel", "Electric"])
hvac_heating_setpoint = st.sidebar.number_input("HVAC Heating Setpoint (°C)", value=23)
hvac_cooling_setpoint = st.sidebar.number_input("HVAC Cooling Setpoint (°C)", value=18.4)

# Water Heating
water_heater = st.sidebar.selectbox("Water Heating Fuel", ["Fossil Fuel Standard", "Electric", "Solar"])

# Lighting Inputs
lighting = st.sidebar.selectbox("Lighting Type", ["Incandescent", "LED", "CFL"])

# Window and Roof Attributes
window_question = st.sidebar.radio("Do you have double-pane high insulation windows?", ["Yes", "No"])
window_type = "Double" if window_question == "Yes" else "Single"
roof_insulation_question = st.sidebar.radio("Do you have a thermally insulated roof?", ["Yes", "No"])
roof_insulation = 30 if roof_insulation_question == "Yes" else 1

# EV Charging
ev_charging = st.sidebar.radio("Do you have EV charging stations?", ["Yes", "No"])
ev_charging_value = ev_charging == "Yes"

# Washer, Dryer, and Cooking Range
clothes_dryer_fuel = st.sidebar.selectbox("Clothes Dryer Fuel", ["Gas", "Electric"])
clothes_dryer_efficiency = st.sidebar.selectbox("Clothes Dryer Efficiency", ["None", "Standard", "EnergyStar"])
clothes_washer_efficiency = st.sidebar.selectbox("Clothes Washer Efficiency", ["None", "Standard", "EnergyStar"])
cooking_range = st.sidebar.selectbox("Cooking Range", ["Gas", "Electric Resistance", "Electric Induction"])

# Storage and Production
st.sidebar.subheader("Storage and Production Attributes")
storage_capacity_quantile = st.sidebar.number_input("Battery Storage Capacity Recommendation Quantile (0 to 1)", value=0.3)
production_capacity = st.sidebar.number_input("Production Capacity (kW)", value=0.0)

# Submit Button
if st.sidebar.button("Submit"):
    # Payload Construction
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
                    {"name": "water_heater", "value": water_heater},
                    {"name": "wall_type", "value": wall_type},
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
                    {"name": "capacity_recommendation_quantile", "value": storage_capacity_quantile}
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
        data = response.json()
        intervals = pd.DataFrame(data["data"]["intervals"])
        total_emissions = intervals.query("variable == 'emissions'")["value"].iloc[0] * num_units
        total_consumption = intervals.query("variable == 'consumption.electricity'")["value"].iloc[0] * num_units
        per_sq_ft_emissions = total_emissions / (floor_area_ft2 * num_units)

        # Display Results
        st.subheader("Results")
        st.metric("Total Emissions (kgCO2)", f"{total_emissions:.2f}")
        st.metric("Total Energy Consumption (kWh)", f"{total_consumption:.2f}")

        total_emissions = intervals.query("variable == 'emissions'")["value"].iloc[0] * num_units
        per_sq_ft_emissions = total_emissions / (floor_area_ft2 * num_units)

# Additional code for decarbonization scenario
       # Define decarbonization trajectory
start_year = 2024
end_year = 2050
initial_emission_factor = 0.2889  # kgCO2/kWh in 2024
final_emission_factor = 0.05  # kgCO2/kWh in 2050
years = list(range(start_year, end_year + 1))
decarbonization_factors = [
    initial_emission_factor + (final_emission_factor - initial_emission_factor) * (year - start_year) / (end_year - start_year)
    for year in years
]

# Define benchmark emissions for each year
benchmark_emissions = []
for year in years:
    for period, benchmark in emission_benchmarks.items():
        start_year, end_year = map(int, period.split("–"))
        if start_year <= year <= end_year:
             benchmark_emissions.append(benchmark)
             break
    
    # Calculate building emissions under decarbonized grid
decarbonized_emissions_per_sq_ft = []
for factor in decarbonization_factors:
    decarbonized_emissions = total_emissions * (factor / initial_emission_factor)
    decarbonized_emissions_per_sq_ft.append(decarbonized_emissions / (floor_area_ft2 * num_units))
    
    # Plot updated Benchmark vs Building Emissions
    plt.figure(figsize=(10, 6))
    plt.plot(years, benchmark_emissions, label="Benchmark Emissions (kgCO2/ft²)", color="blue", marker="o")
    plt.plot(years, [per_sq_ft_emissions] * len(years), label="Building Emissions (kgCO2/ft²)", color="red", linestyle="--")
    plt.plot(years, decarbonized_emissions_per_sq_ft, label="Decarbonized Grid (kgCO2/ft²)", color="green", linestyle=":")
    plt.xlabel("Year")
    plt.ylabel("Emissions (kgCO2/ft²)")
    plt.title("Building Emissions vs Benchmark Emissions (Including Decarbonized Grid)")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)
        
        # Calculate fines for the decarbonized grid scenario
decarbonized_fines = []
for year, factor, benchmark in zip(years, decarbonization_factors, benchmark_emissions):
    decarbonized_emissions = total_emissions * (factor / initial_emission_factor)
    decarbonized_per_sq_ft = decarbonized_emissions / (floor_area_ft2 * num_units)
    total_excess_emissions = max(0, (decarbonized_per_sq_ft - benchmark) * floor_area_ft2 * num_units)
    fine = total_excess_emissions * 269
    decarbonized_fines.append({
            "Year": year,
            "Decarbonized Grid Emissions (kgCO2/ft²)": decarbonized_per_sq_ft,
            "Excess Emissions (kgCO2)": total_excess_emissions,
            "Fine ($)": fine
        })
        
        # Convert decarbonized fines data to DataFrame
        decarbonized_fines_df = pd.DataFrame(decarbonized_fines)
        
        # Update Fine Plot
        plt.figure(figsize=(10, 6))
        plt.bar(fines_df["Period"], fines_df["Fine ($)"], color="red", alpha=0.7, label="Current Grid")
        plt.bar(decarbonized_fines_df["Year"], decarbonized_fines_df["Fine ($)"], color="green", alpha=0.5, label="Decarbonized Grid")
        plt.xlabel("Year")
        plt.ylabel("Fine ($)")
        plt.title("Building Emission Fines Due to Non-Compliance (Including Decarbonized Grid)")
        plt.legend()
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        st.pyplot(plt)
        
        # Display Decarbonized Fine Results
        st.subheader("BPS Compliance Fine Results (Decarbonized Grid)")
        st.dataframe(decarbonized_fines_df)
        #decarb end
        # Plot Benchmarks vs Building Emissions
        # Plot Benchmarks vs Building Emissions
        years = [year for year, _ in benchmark_timeline]
        benchmark_emissions = [value for _, value in benchmark_timeline]
        building_emissions = [per_sq_ft_emissions] * len(years)

        plt.figure(figsize=(10, 6))
        plt.plot(years, benchmark_emissions, label="Threshold Emissions (kgCO2/ft²)", color="blue", linestyle="--")
        plt.plot(years, building_emissions, label=" Your Building Emissions (kgCO2/ft²)", color="red")
        plt.xlabel("Year")
        plt.ylabel("Emissions (kgCO2/ft²)")
        plt.title("Your Building Emissions vs Threshold Emissions")
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)

        # ADDITIONAL CODE HERE
        # Calculate fines for non-compliance for each period
    fines = []
    for period, benchmark in emission_benchmarks.items():
        total_excess_emissions = max(0, (per_sq_ft_emissions - benchmark) * floor_area_ft2 * num_units)
        fine = total_excess_emissions * 0.269  # Fine calculation
        fines.append({
                "Period": period,
                "Benchmark Emissions (kgCO2/ft²)": benchmark,
                "Excess Emissions (kgCO2)": total_excess_emissions,
                "Fine ($)": fine
            })

        # Convert fines data to DataFrame
        fines_df = pd.DataFrame(fines)

        # Plot fines for each year
        plt.figure(figsize=(10, 6))
        plt.bar(fines_df["Period"], fines_df["Fine ($)"], color="red", alpha=0.7)
        plt.xlabel("Period")
        plt.ylabel("Fines ($/yr)")
        plt.title("Annual Fines you will incur due to Non-Compliance with BPS")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        st.pyplot(plt)

        # Display fine-related results
        st.subheader("BPS Compliance Fine Results")
        st.dataframe(fines_df)

    else:
        st.error(f"API Call Failed: {response.status_code}")
        st.write(response.text)

  
