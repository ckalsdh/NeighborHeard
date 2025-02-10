import streamlit as st
import folium
from folium.plugins import HeatMap
import pandas as pd
import os
from streamlit_folium import folium_static


df = get_data(10, 29, dur=48)

# Calculate average pressure for each location (latitude, longitude)
avg_pressure_df = df.groupby(['latitude', 'longitude'])['BMP280 Barometer'].mean().reset_index()

# Create the heatmap data
heatmap_data = avg_pressure_df[['latitude', 'longitude', 'BMP280 Barometer']].values.tolist()

# Create a Folium map centered on the average latitude and longitude
center_lat = df['latitude'].mean()
center_lon = df['longitude'].mean()
folium_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)

# Add a heatmap layer to the map
HeatMap(heatmap_data, radius=10, max_zoom=13).add_to(folium_map)

# Display the map in the Streamlit app
st.title("Crime Detection Heatmap")
st.subheader("This heatmap displays crime detection data based on pressure sensor readings.")
st.markdown("Below is the interactive heatmap showing data over time.")
folium_static(folium_map)  # Use streamlit_folium to render Folium maps
