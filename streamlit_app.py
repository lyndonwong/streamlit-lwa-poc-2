# LWA POC 2 2025-07-30
# Pursues code changes to connect my streamlit LWA POC app to real local planning commission data.

import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("Interactive Map of Menlo Park, CA")
st.write("Hover over the pins to see detailed information and a link for more information about each location.")
st.write("Get August to give me critique for this map!")

# Sample data for locations within Menlo Park, including a URL for more info
data = {
    'name': [
        'Meta HQ (Facebook)',
        'Menlo Park Library',
        'Sharon Heights Golf & Country Club',
        'Allied Arts Guild',
        'Draper University'
    ],
    'latitude': [
        37.4845,
        37.4526,
        37.4338,
        37.4475,
        37.4507
    ],
    'longitude': [
        -122.1477,
        -122.1837,
        -122.2152,
        -122.1932,
        -122.1818
    ],
    'description': [
        'The headquarters of Meta Platforms (formerly Facebook).',
        'A public library serving the community of Menlo Park.',
        'A private golf and country club offering various amenities.',
        'A historic complex of artisan shops, gardens, and a restaurant.',
        'An educational institution founded by venture capitalist Tim Draper.'
    ],
    'country': [
        'USA', 'USA', 'USA', 'USA', 'USA'
    ],
    'url': [
        'https://about.meta.com/',
        'https://www.menlopark.org/library',
        'https://www.sharonheights.org/',
        'https://alliedartsguild.org/',
        'https://www.draperuniversity.com/'
    ]
}
df = pd.DataFrame(data)

# Center the map specifically around Menlo Park, CA
# Approximate center of Menlo Park
map_center = [37.45, -122.18]

# Create a Folium map object
# Increased zoom_start for a closer view of Menlo Park
m = folium.Map(location=map_center, zoom_start=12, control_scale=True)

# Add markers for each location
for idx, row in df.iterrows():
    # Construct the tooltip text with detailed information and the URL link
    tooltip_html = f"""
    <h4>{row['name']}</h4>
    <b>Description:</b> {row['description']}<br>
    <b>Coordinates:</b> ({row['latitude']:.4f}, {row['longitude']:.4f})<br>
    <a href="{row['url']}" target="_blank">More Information</a>
    """

    # Add a marker with the tooltip
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        tooltip=folium.Tooltip(tooltip_html, sticky=True, max_width=300), # 'sticky=True' makes it follow the mouse
        popup=folium.Popup(f"<b>{row['name']}</b><br>{row['description']}<br><a href='{row['url']}' target='_blank'>Visit Website</a>"), # Optional: popup on click
        icon=folium.Icon(color='blue', icon='map-marker') # Changed icon color and type for variety
    ).add_to(m)

# Display the map in Streamlit
# Adjusted width for better viewing of a localized area
st_data = st_folium(m, width=900, height=600)

st.subheader("Selected Location (on click):")
if st_data and st_data.get("last_object_clicked_popup"):
    st.info(f"You clicked on: {st_data['last_object_clicked_popup']}")
else:
    st.write("Click on a marker to see its details here.")

st.markdown("""
---
**Note:**
- **Hover** over a pin to see its `tooltip` (rich information, including a link).
- **Click** on a pin to see its `popup` and update the "Selected Location" text below the map.
- The `streamlit-folium` component provides a lot more customization options than `st.map()`.
""")
