import folium
from folium.features import GeoJsonTooltip
import geopandas as gpd
import pandas as pd
import branca.colormap as cm
import lookupCountyns
import os

hasValues = True
data = {'Alachua, FL': 201.3, 'Baker, FL': 270.7,
        'Bay, FL': 297.1, 'Bradford, FL': 190.5,
        'Brevard, FL': 133.9, 'Broward, FL': 121.2,
        'Calhoun, FL': 211.8, 'Charlotte, FL': 66.8,
        'Citrus, FL': 99.5, 'Clay, FL': 88.2,
        'Collier, FL': 55.3, 'Columbia, FL': 230.0,
        'Miami-Dade, FL': 188.1, 'DeSoto, FL': 243.4,
        'Dixie, FL': 225.2, 'Duval, FL': 204.7,
        'Escambia, FL': 247.6, 'Flagler, FL': 81.2,
        'Franklin, FL': 184.0, 'Gadsden, FL': 205.0,
        'Gilchrist, FL': 157.3, 'Glades, FL': 205.5,
        'Gulf, FL': 119.8, 'Hamilton, FL': 281.1,
        'Hardee, FL': 110.9, 'Hendry, FL': 207.9,
        'Hernando, FL': 100.8, 'Highlands, FL': 203.0,
        'Hillsborough, FL': 170.4, 'Holmes, FL': 182.5,
        'Indian River, FL': 99.2, 'Jackson, FL': 177.5,
        'Jefferson, FL': 128.5, 'Lafayette, FL': 141.7,
        'Lake, FL': 109.7, 'Lee, FL': 89.6, 'Leon, FL': 169.8,
        'Levy, FL': 187.4, 'Liberty, FL': 125.3,
        'Madison, FL': 278.1, 'Manatee, FL': 154.7,
        'Marion, FL': 183.6, 'Martin, FL': 79.9,
        'Monroe, FL': 195.8, 'Nassau, FL': 82.4,
        'Okaloosa, FL': 124.7, 'Okeechobee, FL': 230.9,
        'Orange, FL': 205.5, 'Osceola, FL': 145.0,
        'Palm Beach, FL': 120.0, 'Pasco, FL': 103.2,
        'Pinellas, FL': 140.0, 'Polk, FL': 170.6,
        'Putnam, FL': 206.9, 'St. Johns, FL': 54.4,
        'St. Lucie, FL': 137.7, 'Santa Rosa, FL': 99.6,
        'Sarasota, FL': 90.9, 'Seminole, FL': 98.9,
        'Sumter, FL': 82.7, 'Suwannee, FL': 188.3,
        'Taylor, FL': 332.8, 'Union, FL': 185.6,
        'Volusia, FL': 189.8, 'Wakulla, FL': 117.0,
        'Walton, FL': 154.4, 'Washington, FL': 216.3
        }
description = "2022 Violent crime rate per 100k"
dataLen = len(data)

geojson_location = 'C:\\Users\\ryanw\PycharmProjects\InteractiveMap\geojson\counties.geojson'
county_location = os.path.join("stateCodes", "st01_al_cou2020.txt")

def parse_county_state(input_string):
    # Split the string into county and state based on the comma
    parts = input_string.split(',')

    # Trim any leading or trailing whitespace
    county = parts[0].strip()
    state = parts[1].strip() if len(parts) > 1 else None

    return county, state

def selectZoom(range):

    if range < 9 and range > 6:
        return 8
    else:
        return 5

counties = [""] * dataLen
states = [""] * dataLen
countyns = [""] * dataLen
values = [0] * dataLen
i = 0

for key, value in data.items():
    counties[i], states[i] = parse_county_state(key)
    values[i] = value
    countyns[i] = str(lookupCountyns.find_countyns(county_location, counties[i], states[i])).zfill(8)
    i += 1

if hasValues and dataLen >= 2:
    gradient = True
else:
    gradient = False

if gradient:
    max_value = max(values)
    min_value = min(values)
    color_scale = cm.linear.Blues_09.scale(min_value, max_value)

def select_style_function(merged):
    def style_function(feature):
        if feature['properties']['COUNTYNS'] in merged['COUNTYNS'].values:
            return {'fillColor': 'blue', 'color': 'gray'}
        else:
            return {'fillColor': 'gray', 'color': 'gray'}

    return style_function

def gradient_style_function(merged):
    def style_function(feature):
        value = merged.loc[merged['COUNTYNS'] == feature['properties']['COUNTYNS'], 'VALUE']
        if value.size == 0:
            return {
                'fillColor': 'gray',
                'color': 'black',
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0
            }
        else:
            value = value.values[0]
            return {
                'fillColor': color_scale(value),
                'color': 'black',
                'weight': 1,
                'dashArray': '5, 5',
                'fillOpacity': 0.6
            }
    return style_function

# Create a Folium map


data_df = pd.DataFrame({'COUNTYNS': countyns, 'VALUE': values})

# Merge data with GeoJSON
gdf = gpd.read_file(geojson_location)
merged = gdf.merge(data_df, on='COUNTYNS')

tooltip = GeoJsonTooltip(
    fields=['NAME', 'VALUE'],
    aliases=['County: ', description + ': '],  #Displayed text before the value
    localize=True,
    sticky=False,
    labels=True,
    style="""
        background-color: #F0EFEF;
        border: 2px solid black;
        border-radius: 3px;
        box-shadow: 3px;
    """,
    max_width=800,
)

# Add Choropleth layer
if gradient:
    my_style_function = gradient_style_function(merged)
else:
    my_style_function = select_style_function(merged)

mergedProjected = merged.to_crs('EPSG:5070')

mapX = mergedProjected.centroid.x.median()
mapY = mergedProjected.centroid.y.median()

rangeX = mergedProjected.centroid.x.max() - mergedProjected.centroid.x.min()
rangeY = mergedProjected.centroid.y.max() - mergedProjected.centroid.y.min()

maxRange = max(rangeX, rangeY)

print("The distance in x is %f", maxRange)

zoomLevel = selectZoom(maxRange)

#m = folium.Map(location=[mapX, mapY], zoom_start=zoomLevel)
m = folium.Map(location=[37.0902, -95.7129], zoom_start=5)

folium.GeoJson(
    merged,
    style_function=my_style_function,
    tooltip=tooltip
).add_to(m)

# Save the map
m.save('example.html')
