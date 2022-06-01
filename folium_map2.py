import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
import geopandas as gpd
import os
import pyproj
from pyproj import CRS
import plotly.graph_objs as go
import json
import matplotlib as plt
from streamlit_folium import st_folium
import folium

#File path for the pandas dataframe
DATA_URL = ("D:\Work\Batmati_TOF\data\Municipality_level_TOF_Forest.csv")
app_path = "D:\Work\Python\Bagmati_TOF"
#File path for the boundaries
input_folder = ("D:\Work\Batmati_TOF\data\Boundary\Bagmati_Municipalities.shp")

#Reading boundaries and tablular data
table_df = pd.read_csv(DATA_URL)
bound_gdf = gpd.read_file(input_folder).rename(columns = {"LOCAL":"municipality"})

#Merging tabular data with shapefile to get polygons of each municipality along with tabular data
#Note After this we have the final dataset named as "data" 
merged_df = table_df.merge(bound_gdf, on = "municipality", how = "left") 
merged_df_to_csv = merged_df.to_csv(os.path.join("D:\Work\Python\Bagmati_TOF", "merged_csv.csv"), header=True ,index = False)
data = pd.read_csv(os.path.join("D:\Work\Python\Bagmati_TOF", "merged_csv.csv"))
data['geometry'] = gpd.GeoSeries.from_wkt(data['geometry'])
data_gdf = gpd.GeoDataFrame(data, geometry='geometry')
#data_gdf["centroid"] = data_gdf.centroid
#data_gdf["geom_wkt"] = gpd.GeoSeries.to_wkt(data['geometry'])
data_gdf = data_gdf.set_crs('epsg:32645', allow_override = True)
data_gdf.crs = CRS.from_epsg(32645)
data_gdf = data_gdf.to_crs(epsg = 4326)

data_gdf['geoid'] = data_gdf.index.astype(str)
data_gdf = data_gdf.dropna()
data = data_gdf[["geoid","municipality", "district","tof_area_ha", "forest_area_ha", "total_tree_cover_ha", "tof_percent","forest_percent", "geometry"]]


st.title("Tree Cover Bagmati Province")
#for changing type of the maps
add_select = st.selectbox("Select Basemap",("OpenStreetMap", "Stamen Terrain","Stamen Toner"))
# Create a Map instance
m = folium.Map(location=[27.5, 85.5], tiles = add_select, zoom_start=8, control_scale=True)
#st_folium(m, width = 725)

# Plot a choropleth map
# Notice: 'geoid' column that we created earlier needs to be assigned always as the first column
custom_scale1 = (data['tof_percent'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()
custom_scale2 = (data['forest_percent'].quantile((0,0.2,0.4,0.6,0.8,1))).tolist()
tof_col = 'tof_percent'
forest_col = 'forest_percent'




def maps(column, scale):
    folium.Choropleth(
    geo_data=data,
    name='TOF',
    data=data,
    columns=['geoid', column],
    key_on='feature.id',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    line_color='white', 
    line_weight=0,
    highlight=False, 
    smooth_factor=1.0,
    threshold_scale=scale,
    legend_name= column).add_to(m)
    return st_folium(m, width = 725)

select_map_data = st.selectbox("Select Tree Cover Data to Display", ("TOF", "Forest"))
if select_map_data == "TOF":
    maps(tof_col, custom_scale1)
else:
    maps(forest_col, custom_scale2)

raw_data = data_gdf[["municipality", "district","tof_area_ha", "forest_area_ha", "total_tree_cover_ha", "tof_percent","forest_percent"]]


if st.checkbox("Show All Data", False):
    st.write(raw_data)

select_district = st.selectbox("Select district to see district data", (raw_data['district'].unique()))
st.write(raw_data.loc[raw_data["district"] == select_district][["municipality","tof_area_ha", "forest_area_ha", "total_tree_cover_ha", "tof_percent","forest_percent"]])

groups = raw_data[["district", "tof_area_ha","forest_area_ha", "total_tree_cover_ha"]] 
grouped = groups.groupby(by = "district").sum()
#st.write(grouped)

st.write(f"Total areas for {select_district}:")

st.write(grouped.loc[grouped.index == select_district][["tof_area_ha","forest_area_ha", "total_tree_cover_ha"]])

