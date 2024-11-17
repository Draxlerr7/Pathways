import matplotlib.pyplot as plt
import streamlit as st
import requests
import pandas as pd
from geopy.geocoders import Nominatim

# Streamlit App Title
st.title("Palmetto Pathways Interactive Emission Calculator with Geocoding")

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
reduced_emission_factors = {
    2024: 0.2889,
    2025: 0.282544,
    2026: 0.276188,
    2027: 0.269832,
    2028: 0.263476,
    2029: 0.25712,
    2030: 0.250764,
    2031: 0.244408,
    2032: 0.238052,
    2033: 0.231696,
    2034: 0.22534,
    2035: 0.218984,
    2036: 0.212628,
    2037: 0.206272,
    2038: 0.199916,
    2039: 0.19356,
    2040: 0.187204,
    2041: 0.180848,
    2042: 0.174492,
    2043: 0.168136,
    2044: 0.16178,
    2045: 0.155424,
    2046: 0.149068,
    2047: 0.142712,
    2048: 0.136356,
    2049: 0.13,
}

# Convert benchmarks into a timeline
benchmark_timeline = []
for period, value in emission_benchmarks.items():
    start_year, end_year = map(int, period.split("–"))
    benchmark_timeline.extend([(year, value) for year in range(start_year, end_year + 1)])

# Geocoding Function
def geocode_address(address):
    geolocator = Nominatim(user_agent="emission_calculator")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        st.error("Address could not be geocoded. Please check the input.")
        return None, None

# Sidebar Input Parameters
st.sidebar.header("Input Parameters")

# Address Input for Geocoding
address = st.sidebar.text_input("Enter Address or City", value="New York, NY")

# Call Geocoding
latitude, longitude = None, None
if address:
    latitude, longitude = geocode_address(address)

if latitude and longitude:
    # Time Range Inputs
    year = st.sidebar.number_input("Year (e.g., 2024)", min_value=2024, max_value=2050, value=2024)
    from_datetime = f"{year}-01-01T00:00:00"
    to_datetime = f"{year}-12-31T23:59:59"

    # Building Attributes
    st.sidebar.subheader("Building Attributes")
    building_type = st.sidebar.selectbox(
        "Building Type",
        ["Multi-Family (5 to 9 units)", "Multi-Family (10 to 19 units)", "Multi-Family (20 to 49 units)", "Multi-Family (50 or more units)"]
    )
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
    water_heater = st.sidebar.selectbox("Water Heating Fuel", ["Fossil Fuel Standard", "Electric Standard"])

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
# Submit Button
if st.sidebar.button("Submit"):
    # Ensure latitude and longitude are valid
    if latitude is not None and longitude is not None:
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
                    "fossil_fuel": {"value": 0.12}
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
    # Process the response data
        data = response.json()

    # Extract location details
        location_info = data["data"]["location"]
        intervals = pd.DataFrame(data["data"]["intervals"])
    
    # Extract location details
        puma_fips = location_info.get("puma_fips", "N/A")
        county = location_info.get("county", "N/A")
        county_fips = location_info.get("county_fips", "N/A")
        state = location_info.get("state", "N/A")
        state_fips = location_info.get("state_fips", "N/A")
        climate_zone = location_info.get("climate_zone", "N/A")

    # Extract emissions and consumption data
        total_emissions = intervals.query("variable == 'emissions'")["value"].iloc[0] * num_units
        total_consumption = intervals.query("variable == 'consumption.electricity'")["value"].iloc[0] * num_units
        per_sq_ft_emissions = total_emissions / (floor_area_ft2 * num_units)

    # Display Location Info
        st.subheader("Location Information")
        st.write(f"**PUMA FIPS:** {puma_fips}")
        st.write(f"**County:** {county}")
        st.write(f"**County FIPS:** {county_fips}")
        st.write(f"**State:** {state}")
        st.write(f"**State FIPS:** {state_fips}")
        st.write(f"**Climate Zone:** {climate_zone}")

    # Display Emissions and Consumption Info
        st.subheader("Results")
        st.metric("Total Emissions (kgCO2)", f"{total_emissions:.2f}")
        st.metric("Total Energy Consumption (kWh)", f"{total_consumption:.2f}")
        st.metric("Per Sq Ft Emissions (kgCO2/ft²)", f"{per_sq_ft_emissions:.4f}")

    # Calculate Emissions vs Benchmarks
        results = []
        for period, benchmark in emission_benchmarks.items():
            excess_emissions = max(0, per_sq_ft_emissions - benchmark) * floor_area_ft2 * num_units
            results.append({
                "Period": period,
                "Benchmark Emissions (kgCO2/ft²)": benchmark,
                "Building Emissions (kgCO2/ft²)": per_sq_ft_emissions,
                "Excess Emissions (kgCO2)": excess_emissions
            })

    # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        st.dataframe(results_df)

    # Plot Benchmarks vs Building Emissions
        years = [year for year, _ in benchmark_timeline]
        benchmark_emissions = [value for _, value in benchmark_timeline]
        building_emissions = [per_sq_ft_emissions] * len(years)

        plt.figure(figsize=(10, 6))
        plt.plot(years, benchmark_emissions, label="Threshold Emissions (kgCO2/ft²)", color="blue", linestyle="--")
        plt.plot(years, building_emissions, label="Building Emissions (kgCO2/ft²)", color="red")
        plt.xlabel("Year")
        plt.ylabel("Emissions (kgCO2/ft²)")
        plt.title("Your Building Emissions vs Threshold Emissions")
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)

    # Calculate fines for non-compliance for each period
        fines = []
        for period, benchmark in emission_benchmarks.items():
            total_excess_emissions = max(0, (per_sq_ft_emissions - benchmark) * floor_area_ft2 * num_units)
            fine = total_excess_emissions * 0.269  # Fine calculation
            fines.append({
                "Period": period,
                "Threshold Emissions (kgCO2/ft²)": benchmark,
                "Excess Emissions (kgCO2)": total_excess_emissions,
                "Fine ($)": fine
            })

    # Convert fines data to DataFrame
        fines_df = pd.DataFrame(fines)
        st.subheader("BPS Compliance Fine Results")
        st.dataframe(fines_df)

    # Plot fines for each year
        plt.figure(figsize=(10, 6))
        plt.bar(fines_df["Period"], fines_df["Fine ($)"], color="red", alpha=0.7)
        plt.xlabel("Period")
        plt.ylabel("Fines ($/yr)")
        plt.title("Annual Fines Incurred Due to Non-Compliance")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        st.pyplot(plt)
    else:
        st.error(f"API Call Failed: {response.status_code}")
        st.write(response.text)
# Emission Factors for each year (2024–2049)
# Plot Benchmarks vs Building Emissions for Current and Reduced Emission Rates
years = [year for year, _ in benchmark_timeline]
benchmark_emissions = [value for _, value in benchmark_timeline]
building_emissions_current = [per_sq_ft_emissions] * len(years)

# Calculate building emissions with emission rate reduction

building_emissions_reduced = [
    per_sq_ft_emissions * emission_rate_reduction.get(year, 0.2889) / 0.2889
    for year in years
]

# First Plot: Benchmark vs Building Emissions (Current and Reduced Rates)
plt.figure(figsize=(10, 6))
plt.plot(years, benchmark_emissions, label="Threshold Emissions (kgCO2/ft²)", color="blue", linestyle="--")
plt.plot(years, building_emissions_current, label="Building Emissions (Current Rates)", color="red")
plt.plot(years, building_emissions_reduced, label="Building Emissions (Reduced Rates)", color="green", linestyle=":")
plt.xlabel("Year")
plt.ylabel("Emissions (kgCO2/ft²)")
plt.title("Your Building Emissions vs Threshold Emissions (Current and Reduced Rates)")
plt.legend()
plt.grid(True)
st.pyplot(plt)


fines_current = []
fines_reduced = []

for year, reduced_emission in zip(years, reduced_emissions):
    if year in emission_factors:
        # Benchmark emission for the current year
        benchmark_emission = emission_benchmarks.get(f"{year}–{year + 5}", benchmark_emissions[0])

        # Calculate fines for current rates
        excess_emissions_current = max(0, (per_sq_ft_emissions - benchmark_emission) * floor_area_ft2 * num_units)
        fine_current = excess_emissions_current * 0.269  # Fine calculation for current rates
        fines_current.append(fine_current)

        # Calculate fines for reduced rates
        excess_emissions_reduced = max(0, (reduced_emission - benchmark_emission) * floor_area_ft2 * num_units)
        fine_reduced = excess_emissions_reduced * 0.269  # Fine calculation for reduced rates
        fines_reduced.append(fine_reduced)
    else:
        st.error(f"Emission factor for year {year} is missing!")
        fines_current.append(0)
        fines_reduced.append(0)

# Second Plot: Fines for Current and Reduced Rates
if len(fines_current) != len(years) or len(fines_reduced) != len(years):
    st.error("Mismatched lengths in fines data. Ensure fines_current and fines_reduced align with years.")
else:
    plt.figure(figsize=(10, 6))
    width = 0.4  # Width of the bars
    x_positions = range(len(years))

    # Plot fines for current rates
    plt.bar(
        [x - width / 2 for x in x_positions],
        fines_current,
        width=width,
        color="red",
        alpha=0.7,
        label="Fines (Current Rates)",
    )
    # Plot fines for reduced rates
    plt.bar(
        [x + width / 2 for x in x_positions],
        fines_reduced,
        width=width,
        color="green",
        alpha=0.5,
        label="Fines (Reduced Rates)",
    )
    plt.xticks(x_positions, [str(year) for year in years], rotation=45)
    plt.xlabel("Year")
    plt.ylabel("Fines ($/yr)")
    plt.title("Annual Fines Incurred Due to Non-Compliance (Current vs Reduced Rates)")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    st.pyplot(plt)

