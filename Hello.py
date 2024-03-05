# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Lume Cannabis plot",
        page_icon="Lume",
    )
st.write("# Lume Cannabis Co. Marketshare Visualization")

import pandas as pd
from sklearn.neighbors import BallTree
import numpy as np
import utm
import geopandas as gpd
import shapely
import json
import streamlit as st

df=pd.read_excel("CannabisDisposMich.xlsx", skiprows=[1])
df=df[["NAME","ADDRESS"]]

df_ify=pd.read_csv("4022d538b72f43d0acc2735f026273c9.csv")
df_ify=df_ify[["query.text", "lon", "lat"]]
df_ify["Name"]=df["NAME"]

df2=df_ify["Name"]=="Lume Cannabis Co."
lume_plots=df_ify[df2]
lume_plots=lume_plots.reset_index()
lume_plots.loc[len(lume_plots)] = [337,'2247 W Liberty St Ste 1, Ann Arbor, MI 48103', -83.77763, 42.27394, "Lume Cannabis Co."]

df2=df_ify["Name"]!="Lume Cannabis Co."
nonlume_plots=df_ify[df2]


def circles(lonlat, radius=10 ** 4):
    
    utm_coords = utm.from_latlon(lonlat[:, 1], lonlat[:, 0])
    utmcrs = gpd.GeoDataFrame(
        geometry=[shapely.geometry.Point(lonlat[0, 0], lonlat[0, 1])], crs="EPSG:4326"
    ).estimate_utm_crs()

    return gpd.GeoDataFrame(
        geometry=[
            shapely.geometry.Point(easting, northing).buffer(radius)
            for easting, northing in zip(utm_coords[0], utm_coords[1])
        ],
        crs=utmcrs,
    ).to_crs("EPSG:4326")

gdf = circles(lume_plots.loc[:, ["lon", "lat"]].values, radius=16093.4)

import plotly.express as px
color_scale = [(0, 'orange'), (1,'red')]
fig = px.scatter_mapbox(lume_plots, 
                        lat="lat", 
                        lon="lon", 
                        hover_name="Name", 
                        hover_data=["query.text"],
                        zoom=6, 
                        height=800,
                        width=800)

fig.update_traces(marker={'size': 8, 'color': 'darkblue'})

fig.update_layout(
    mapbox={
        "style": "open-street-map",
        "zoom": 6,
        "center":{"lat":gdf.loc[0,"geometry"].centroid.y, "lon":gdf.loc[0,"geometry"].centroid.x},
        "layers": [
            {
                "source": json.loads(gdf.geometry.to_json()),
                "below": "traces",
                "type": "line",
                "color": "darkblue",
                "line": {"width": 1.5},
            }
        ],
    },
    margin={"l": 0, "r": 0, "t": 0, "b": 0},
)

fig2 = px.scatter_mapbox(nonlume_plots, 
                        lat="lat", 
                        lon="lon", 
                        hover_name="Name", 
                        hover_data=["query.text"],
                        zoom=6, 
                        height=800,
                        width=800)

fig2.update_traces(marker={'size': 8, 'color': 'saddlebrown'})

fig.add_trace(fig2.data[0])
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)


