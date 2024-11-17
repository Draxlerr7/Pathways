# Emission Factors for each year (2024–2049)
emission_factors = {
    2024: 0.2889, 2025: 0.279344, 2026: 0.269788, 2027: 0.260232,
    2028: 0.250676, 2029: 0.24112, 2030: 0.231564, 2031: 0.222008,
    2032: 0.212452, 2033: 0.202896, 2034: 0.19334, 2035: 0.183784,
    2036: 0.174228, 2037: 0.164672, 2038: 0.155116, 2039: 0.14556,
    2040: 0.136004, 2041: 0.126448, 2042: 0.116892, 2043: 0.107336,
    2044: 0.09778, 2045: 0.088224, 2046: 0.078668, 2047: 0.069112,
    2048: 0.059556, 2049: 0.05
}

# Yearly Results Storage
yearly_results = []

# Loop Through Each Year
for year, emission_factor in emission_factors.items():
    from_datetime = f"{year}-01-01T00:00:00"
    to_datetime = f"{year}-12-31T23:59:59"

    # Update Payload Emission Rate
    payload["parameters"]["from_datetime"] = from_datetime
    payload["parameters"]["to_datetime"] = to_datetime
    payload["costs"]["emission_rates"]["electricity"]["value"] = emission_factor

    # Make API Call for Each Year
    response = requests.post(API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        # Process Yearly API Response
        data = response.json()
        intervals = pd.DataFrame(data["data"]["intervals"])
        total_emissions = intervals.query("variable == 'emissions'")["value"].iloc[0] * num_units
        total_consumption = intervals.query("variable == 'consumption.electricity'")["value"].iloc[0] * num_units
        per_sq_ft_emissions = total_emissions / (floor_area_ft2 * num_units)

        # Append Yearly Results
        yearly_results.append({
            "Year": year,
            "Emission Factor (kgCO2/kWh)": emission_factor,
            "Total Emissions (kgCO2)": total_emissions,
            "Total Energy Consumption (kWh)": total_consumption,
            "Per Sq Ft Emissions (kgCO2/ft²)": per_sq_ft_emissions
        })
    else:
        st.error(f"API Call Failed for Year {year}: {response.status_code}")
        st.write(response.text)

# Convert Yearly Results to DataFrame
yearly_df = pd.DataFrame(yearly_results)

# Display Yearly Results
st.subheader("Yearly Emission and Energy Consumption Results")
st.dataframe(yearly_df)

# Plot Yearly Total Emissions and Per Sq Ft Emissions
plt.figure(figsize=(10, 6))
plt.plot(yearly_df["Year"], yearly_df["Total Emissions (kgCO2)"], label="Total Emissions (kgCO2)", marker="o", color="blue")
plt.plot(yearly_df["Year"], yearly_df["Per Sq Ft Emissions (kgCO2/ft²)"], label="Per Sq Ft Emissions (kgCO2/ft²)", linestyle="--", color="red")
plt.xlabel("Year")
plt.ylabel("Emissions")
plt.title("Yearly Emissions Trends")
plt.legend()
plt.grid(True)
st.pyplot(plt)

# Plot Yearly Total Energy Consumption
plt.figure(figsize=(10, 6))
plt.plot(yearly_df["Year"], yearly_df["Total Energy Consumption (kWh)"], label="Total Energy Consumption (kWh)", color="green", marker="o")
plt.xlabel("Year")
plt.ylabel("Energy Consumption (kWh)")
plt.title("Yearly Energy Consumption Trends")
plt.legend()
plt.grid(True)
st.pyplot(plt)
