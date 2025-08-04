# LWA POC 2 2025-07-30
# Pursues code changes to connect my streamlit LWA POC app to real local planning commission data.

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
# add audio stream support
import io
# Bypass streamlit_folium component, which has bug that causes empty space at bottom of map
import streamlit.components.v1 as components

st.set_page_config(layout="wide")
st.logo("LWA-v2-square.png", size="large")    
st.image("LWA-demo-lab-bar.png", use_container_width=True )
st.title("Your Tracker: San Carlos Planning Commission")

# Podcast player
st.subheader("Deep Dive - July 2025 Podcast")
st.write("Your 5 minute podcast on the big themes and impacts of San Carlos planning commission actions in 1H 2025")
try:
    with open("SCPT_podcast_1H2025.m4a", "rb") as audio_file:
        audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/m4a")
except FileNotFoundError:
    st.error("Error: The audio file 'SCPT_podcast_1H2025.m4a' was not found. Please ensure the file is in the correct directory.")  

st.markdown('''
            ##### Overview of Commission meetings 1H 2025: 
            Key discussions during this 6 month period from January through June include the **2045 General Plan Reset**, a comprehensive update addressing housing projections, land use designations, and environmental impacts like air quality and transportation. The **Pulgus Creek Watershed Plan** is also presented, outlining strategies for flood protection, sea level rise, groundwater management, and community education on watershed preservation. Additionally, the **Northeast Area Specific Plan** is explored, detailing a 20-year framework for guiding development, improving connectivity, addressing environmental resilience, and managing parking within a 145-acre district. Finally, the **Downtown Streetscape Master Plan** and **Transportation Demand Management Plan** are presented, aiming to enhance the pedestrian experience, balance transportation modes, and implement sustainable parking strategies, alongside a discussion of objective design standards for new multi-family and mixed-use developments and the **Alexandria Life Science Research and Development Campus** project.     
            ''')
# Add interactive map of projects presented to the Planning Commmission

st.subheader("Key Projects Map")
st.write("Hover over the pins to see detailed project information. Click on a pin for a popup and to see the project name below.")

# Load the data from the uploaded CSV file
# Ensure the CSV file 'SCPT_projects_list_1H2025_v6_scrubbed_for_map - SCPT_projects_list_1H2025_v6.csv' is available in the environment.
try:
    # Using the exact filename provided by the user
    df = pd.read_csv("SCPT_projects_list_1H2025_v6_scrubbed_for_map - SCPT_projects_list_1H2025_v6.csv")
except FileNotFoundError:
    st.error("Error: The CSV file 'SCPT_projects_list_1H2025_v6_scrubbed_for_map - SCPT_projects_list_1H2025_v6.csv' was not found.")
    st.stop()

# --- Data Preprocessing and Handling Missing Values ---

# Rename columns for easier access (optional, but good practice)
df.rename(columns={
    'Project Name': 'name',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'Street Address': 'address',
    'City': 'city',
    'Project Description': 'description',
    'Public URL': 'url',
    'Date of Earliest Mention': 'earliest_mention_date', # Renamed
    'Date of Latest Mention': 'latest_mention_date'    # Renamed
}, inplace=True)

# Convert latitude and longitude to numeric, coercing errors to NaN
df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

# Filter out rows where latitude or longitude are missing, as these cannot be plotted
initial_rows = len(df)
df.dropna(subset=['latitude', 'longitude'], inplace=True)
if len(df) < initial_rows:
    st.warning(f"Removed {initial_rows - len(df)} rows due to missing Latitude or Longitude data.")

# Further filter to ensure only San Carlos projects are shown (if 'City' column exists and is needed)
if 'city' in df.columns:
    df = df[df['city'].astype(str).str.contains('San Carlos', case=False, na=False)]
    if df.empty:
        st.warning("No projects found for San Carlos after filtering.")
        st.stop()
else:
    st.warning("The 'City' column was not found in the CSV. Displaying all projects with valid coordinates.")

# Center the map around San Carlos, CA
# Using the mean of the available San Carlos coordinates for a more accurate center
if not df.empty:
    map_center = [df['latitude'].mean(), df['longitude'].mean()]
else:
    # Fallback to a default San Carlos center if no valid data points
    map_center = [37.5025, -122.2605] # Approximate center of San Carlos

# Create a Folium map object
map_height = 500  # Set the height of the map
m = folium.Map(location=map_center, zoom_start=13, height=map_height, control_scale=True)

# Add markers for each location
for idx, row in df.iterrows():
    project_name = row.get('name', 'N/A')
    project_description = row.get('description', 'No description available.')
    street_address = row.get('address', 'N/A')
    public_url = row.get('url')
    earliest_date = row.get('earliest_mention_date', 'N/A') # Get earliest date
    latest_date = row.get('latest_mention_date', 'N/A')   # Get latest date

    # Handle missing URL gracefully
    url_link = ""
    if pd.notna(public_url) and public_url.strip() != '' and public_url.strip().lower() != 'n/a':
        # Ensure URL starts with http:// or https:// for proper linking
        if not public_url.startswith(('http://', 'https://')):
            public_url = 'https://' + public_url # Prepend https if missing
        url_link = f"<br><a href='{public_url}' target='_blank'>More Information</a>"
    else:
        url_link = "<br>No public URL available."

    # Format dates for display, handling potential NaN or 'N/A'
    formatted_earliest_date = str(earliest_date) if pd.notna(earliest_date) and str(earliest_date).strip().lower() != 'n/a' else 'N/A'
    formatted_latest_date = str(latest_date) if pd.notna(latest_date) and str(latest_date).strip().lower() != 'n/a' else 'N/A'

    # Construct the tooltip text with detailed information and the URL link
    # [DEPRECATED] <b>Description:</b> {project_description}<br>
    # [DEPRECATED] {url_link}
    tooltip_html = f"""
    <h4>{project_name}</h4>
    <b>Address:</b> {street_address}<br>
    <b>Earliest Mention:</b> {formatted_earliest_date}<br>
    <b>Latest Mention:</b> {formatted_latest_date}<br>
    <b>Coordinates:</b> ({row['latitude']:.4f}, {row['longitude']:.4f})<br>
    <p><small>Click for more info</small></p>
    """

    # Construct the popup text (appears on click)
    popup_html = f"""
    <b>{project_name}</b><br>
    {project_description}<br>
    <b>Earliest Mention:</b> {formatted_earliest_date}<br>
    <b>Latest Mention:</b> {formatted_latest_date}<br>
    {url_link.replace('<br>', '')}
    """

    # Add a marker with the tooltip and popup
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        tooltip=folium.Tooltip(tooltip_html, sticky=True, max_width=400),
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color='green', icon='info-sign') # Changed icon color and type for San Carlos projects
    ).add_to(m)

# Display the map in Streamlit
# Add st.container and key to st_folium to control rendering
# --- DEPRECATED 8/1/2025 to eliminate empty space bug ---
# with st.container():
#     st_data = st_folium(m, width=900, height=600, key="san_carlos_map")

# --- DEPRECATED 8/1/2025 to simplify functionality of app ---
# st.subheader("Selected Project (on click):")
# if st_data and st_data.get("last_object_clicked_popup"):
#     # Extract the project name from the popup HTML for display
#     clicked_popup_content = st_data['last_object_clicked_popup']
#     # A simple way to get the bolded project name from the popup HTML
#     import re
#     match = re.search(r'<b>(.*?)</b>', clicked_popup_content)
#     if match:
#         st.info(f"You clicked on: {match.group(1)}")
#     else:
#         st.info(f"You clicked on: {clicked_popup_content.split('<br>')[0]}")
# else:
#     st.write("Click on a marker to see its project name here.")

# --- RENDER MAP USING st.components.v1.html ---
# This is a workaround to avoid the empty space issue at the bottom of the map
# Get raw HTML from the Folium map
map_html = m._repr_html_()
# Render the map HTML with st.components.v1.html
components.html(map_html, height=map_height + 2)

# Instructions to use interactive map
st.markdown("""
---
#### Map Usage Note: 
- **Hover** over a pin to see its `tooltip` information.
- **Click** on a pin to see `popup` with more details, including a public URL link when available.
- Rows with missing Latitude or Longitude values are automatically excluded from the map.
- If a Public URL or Date information is missing or 'N/A', the relevant field will indicate that.
""")

st.subheader("Table of Key Projects")
st.dataframe(df)

# Meeting Metrics for 1H 2025
st.subheader("Meeting Metrics for 1H 2025")
chart_df = pd.read_csv('SCPT_meeting_metrics_1H2025.csv')
chart_df["Meeting Date"] = pd.to_datetime(chart_df["Meeting Date"])
chart_df["Meeting length in minutes"] = pd.to_numeric(chart_df["Meeting length in minutes"], errors='coerce')
st.bar_chart(chart_df, x="Meeting Date", y="Meeting length in minutes", use_container_width=True) 

# Planning Commission detailed activity highlights
st.subheader("Fine Print")
st.write("Click the checkbox to dig deeper.")       
# Get markdown content for the Planning Commission highlights
def read_markdown_file(file_path):
    """Reads the content of a markdown file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

markdown_content = read_markdown_file("SCPT_1H2025_Milestones.md")

# Display the markdown content in Streamlit, with user control to show/hide
if st.checkbox("See Planning Commission 1H 2025 Activity Details"):
    st.markdown(markdown_content)

