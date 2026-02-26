# import pandas as pd
# import geopandas as gpd
# from shapely import wkt
# import pydeck as pdk
# import json
# import os

# print("=== Building 3D Digital Twin ===")

# # 1. Load the CSV you just downloaded
# print("[->] Loading building data...")
# df = pd.read_csv("brussels_berlin_dc_buildings.csv")

# # 2. Clean the data (DROP missing geometry!)
# print("[->] Removing invalid map data...")
# df = df.dropna(subset=['geometry'])

# # 3. Convert the text 'POLYGON ((...))' into actual spatial math
# print("[->] Converting text to spatial geometry...")
# df['geometry'] = df['geometry'].apply(wkt.loads)
# gdf = gpd.GeoDataFrame(df, geometry='geometry')

# # 4. Calculate 3D Height (Assume 3 meters per floor. Default to 2 floors if missing)
# gdf['height'] = gdf['building_floor'].fillna(2) * 3

# # 5. Convert to GeoJSON format for the 3D renderer
# geojson_str = gdf.to_json()
# geojson_data = json.loads(geojson_str)

# # 6. Build the 3D PyDeck Layer
# print("[->] Rendering 3D Map Layer...")
# layer = pdk.Layer(
#     "GeoJsonLayer",
#     geojson_data,
#     opacity=0.8,
#     stroked=True,
#     filled=True,
#     extruded=True,
#     wireframe=True,
#     get_elevation="properties.height",
#     get_fill_color="[0, 150, 255, 200]",
#     get_line_color="[255, 255, 255]",
#     pickable=True
# )

# # 7. Center the camera automatically based on the data
# bounds = gdf.total_bounds # [minx, miny, maxx, maxy]
# center_lon = (bounds[0] + bounds[2]) / 2
# center_lat = (bounds[1] + bounds[3]) / 2

# view_state = pdk.ViewState(
#     latitude=center_lat,
#     longitude=center_lon,
#     zoom=11,
#     pitch=45, # Tilt the camera to see the 3D heights
#     bearing=0
# )

# # 8. Configure the popup tooltip when you hover/click
# tooltip = {
#     "html": "<b>Building Type:</b> {building_type_unified} <br/>"
#             "<b>Floors:</b> {building_floor} <br/>"
#             "<b>Linked Image:</b> {Image Name}",
#     "style": {"backgroundColor": "steelblue", "color": "white"}
# }

# # 9. Save to HTML
# print("[->] Exporting to browser...")
# r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
# output_file = "digital_twin.html"
# r.to_html(output_file)

# print(f"[+] Success! Open '{output_file}' in Google Chrome or Edge to see your map.")

import pandas as pd
import geopandas as gpd
from shapely import wkt
import folium

print("=== Building Satellite Street View Map ===")

print("[->] Loading data...")
df = pd.read_csv("brussels_berlin_dc_buildings.csv")
df = df.dropna(subset=['geometry'])

print("[->] Extracting 360 Panorama IDs...")
df['pid'] = df['Image Name'].str.extract(r'pid_(\d+)_')
df = df.dropna(subset=['pid'])

print("[->] Calculating spatial coordinates...")
df['geometry'] = df['geometry'].apply(wkt.loads)
gdf = gpd.GeoDataFrame(df, geometry='geometry')

gdf['lat'] = gdf.geometry.centroid.y
gdf['lon'] = gdf.geometry.centroid.x

print("[->] Rendering Satellite Map...")
center_lat, center_lon = gdf['lat'].mean(), gdf['lon'].mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=15)

folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Satellite',
    overlay=False,
    control=True
).add_to(m)

print("[->] Attaching interactive 360 viewers...")
for idx, row in gdf.head(300).iterrows():
    pid = row['pid']
    
    iframe_html = f'''
        <iframe width="600" height="450" 
            src="https://www.mapillary.com/embed?image_key={pid}&style=photo" 
            frameborder="0">
        </iframe>
    '''
    
    popup = folium.Popup(iframe_html, max_width=650)
    
    folium.CircleMarker(
        location=[row['lat'], row['lon']],
        radius=6,
        color="cyan",
        fill=True,
        fillColor="cyan",
        fillOpacity=0.7,
        popup=popup
    ).add_to(m)

output_file = "street_view_satellite.html"
m.save(output_file)
print(f"[+] Success!")