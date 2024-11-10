import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import pydeck as pdk
import streamlit as st

#Merge Tables
table1 = pd.read_excel(r"C:\Projects\VGI Challenge\vgi_hackathon_2024\FLEXI_bus_stops.xls")
table2 = pd.read_excel(r"C:\Projects\VGI Challenge\vgi_hackathon_2024\FLEXI_trip_data.xls")

merged_data = table2.merge(table1, left_on="Pickup ID", right_on="index") \
                    .merge(table1, left_on="Dropoff ID", right_on="index", suffixes=('', '_dropoff')) \
                    .rename(columns={
                        "index": "pickup_index",
                        "name": "pickup_name",
                        "district": "pickup_district",
                        "latitude": "pickup_latitude",
                        "longitude": "pickup_longitude"
                    }) \
                    .drop(columns=["Pickup ID", "Dropoff ID"])

#Process Date and Time
merged_data['Actual Pickup Time'] = pd.to_datetime(merged_data['Actual Pickup Time'])
merged_data['Actual Dropoff Time'] = pd.to_datetime(merged_data['Actual Dropoff Time'])
merged_data['Pickup Hour'] = merged_data['Actual Pickup Time'].dt.hour
merged_data['Pickup Day'] = merged_data['Actual Pickup Time'].dt.dayofweek  # 0 = Monday, 1= Tuesday, 2 = Wednesday ... 

#Find most demanded pickup

pickup_demand_counts = (
                        merged_data.groupby(['pickup_index', 'pickup_latitude', 'pickup_longitude']) \
                        .size() \
                        .reset_index(name = "count"))

# most_common_dropoff = pickup_dropoff_counts.loc[
#             pickup_dropoff_counts.groupby('pickup_index')['count'].idxmax()
# ]

pickup_demand_counts

os.environ["MAPBOX_API_KEY"] = "pk.eyJ1Ijoiam5haXIiLCJhIjoiY20zYTh1bTRrMTdxbTJscjZyd2Jrbjk5aCJ9.4HXOmaBtz_1udpXKAAf9bA"


# Sidebar filters
st.sidebar.header("Filter Options")
min_demand = st.sidebar.slider("Minimum Demand", int(pickup_demand_counts['count'].min()), int(pickup_demand_counts['count'].max()), 0)
filtered_data = pickup_demand_counts[pickup_demand_counts['count'] >= min_demand]

# Define the 3D HexagonLayer
hex_layer = pdk.Layer(
    "HexagonLayer",
    data=filtered_data,
    get_position=["pickup_longitude", "pickup_latitude"],
    radius=200,
    elevation_scale=50,
    elevation_range=[0, 100],
    extruded=True,
    coverage=1,
)

# Define the view settings for the map
view_state = pdk.ViewState(
    latitude=filtered_data['pickup_latitude'].mean(),
    longitude=filtered_data['pickup_longitude'].mean(),
    zoom=10,
    pitch=45,
)

# Create the PyDeck map
deck_map = pdk.Deck(
    layers=[hex_layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/light-v9",
    #mapbox_key=os.getenv("MAPBOX_API_KEY")
)

# Display the map in Streamlit
st.title("VGI-Flexi Demand Dashboard")
st.write("### 3D Heatmap of Demand")
st.pydeck_chart(deck_map)