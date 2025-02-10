import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
import json

# Set up the Streamlit page configuration
st.set_page_config(layout="wide", page_title="Neighbor Heard: Crime Detection Map")

# Initialize session state for navigation and user profile
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'user_name' not in st.session_state:
    st.session_state.user_name = "John Doe"

# Helper function to load data from data.json
def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning("Data file not found. No incidents to display.")
        return []
    except json.JSONDecodeError:
        st.error("Error reading the data file. Please check its format.")
        return []

# Navigation function
def navigate(page):
    st.session_state.page = page

# Sidebar with navigation buttons
st.sidebar.title("Neighbor Heard Menu")
st.sidebar.button("Home", on_click=lambda: navigate("Home"))
st.sidebar.button("Analytics", on_click=lambda: navigate("Analytics"))
st.sidebar.button("Settings", on_click=lambda: navigate("Settings"))
st.sidebar.button("About", on_click=lambda: navigate("About"))

# Load the logo and display it centered at the top
st.markdown("""<style>
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: white;
        padding: 20px;
    }
</style>""", unsafe_allow_html=True)

st.image('/home/ubuntu/logo.jpeg', caption='', width=500)

# Display greeting on the homepage
def show_home():
    st.markdown(f"### Hi {st.session_state.user_name}, let's stay safe!")
    st.title("Neighbor Heard: Interactive Crime Detection Map")
    st.markdown(
        "### Your community's guardian against threats. Real-time insights at your fingertips."
    )

    # Load data from data.json
    incidents = load_data()
    if not incidents:
        st.info("No data to display.")
        return

    # Add theme switcher
    mode = st.radio("Select Map Theme:", ["Day Mode", "Night Mode"], horizontal=True)

    # Set map center and tiles
    map_center = [34.0284, -118.2849]
    tiles = "CartoDB positron" if mode == "Day Mode" else "CartoDB dark_matter"
    attribution = (
        "© OpenStreetMap contributors" if mode == "Day Mode" else "© CartoDB"
    )
    folium_map = folium.Map(location=map_center, zoom_start=18, tiles=tiles, attr=attribution)

    # Add markers to the map
    marker_cluster = MarkerCluster().add_to(folium_map)
    for incident in incidents:
        house_name = incident["House Name"]
        sound = incident["Sound"]
        probability = incident["Probability"]
        coords = incident["Coordinates"]
        popup_info = (
            f"<b>{house_name}</b>:<br>"
            f"- {sound}: {probability*100:.2f}%<br>"
        )

        folium.Marker(
            location=coords,
            popup=popup_info,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(marker_cluster)

    # Adjust layout for map
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col2:
        folium_static(folium_map, width=1000, height=700)

def show_analytics():
    st.subheader("Analytics Dashboard")
    
    # Load data from data.json
    incidents = load_data()
    if not incidents:
        st.info("No analytics data available.")
        return

    # Create a DataFrame from incidents
    df = pd.DataFrame(incidents)

    st.metric("Total Incidents Detected", len(df))

    # Display bar chart of detected sounds
    st.bar_chart(df["Sound"].value_counts())

def show_settings():
    st.subheader("Settings")
    new_name = st.text_input("Update User Name", st.session_state.user_name)
    if st.button("Save Name"):
        st.session_state.user_name = new_name
        st.success("Name updated successfully!")

def show_about():
    st.subheader("About Neighbor Heard")
    st.markdown(
        """Neighbor Heard is a community-focused safety system designed to detect and report real-time threats using cutting-edge technology."""
    )

# Page navigation logic
if st.session_state.page == "Home":
    show_home()
elif st.session_state.page == "Analytics":
    show_analytics()
elif st.session_state.page == "Settings":
    show_settings()
elif st.session_state.page == "About":
    show_about()

# Footer
st.markdown("""<style>
    .footer {
        text-align: center;
        font-size: 14px;
        color: #888;
        padding: 20px;
        border-top: 1px solid #ddd;
    }
</style>""", unsafe_allow_html=True)
st.markdown('<div class="footer">Neighbor Heard © 2024 - Making Neighborhoods Safer</div>', unsafe_allow_html=True)
