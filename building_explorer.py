import streamlit as st
import geopandas as gpd
import pydeck as pdk

FILE_PATH = "/data/BUILDING_HISTORIC.gpkg"
st.set_page_config(layout="wide")
st.title("3D Building Explorer - NYC") 

@st.cache_data
def load_data():
    gdf = gpd.read_file(FILE_PATH)

    gdf["HEIGHT_M"] = gdf["HEIGHT_ROOF"] * 0.3048

    return gdf

gdf = load_data()

st.success(f"Loaded {len(gdf):,} buildings")

st.subheader("Sample Building Data")

st.dataframe(
    gdf[
        ["BIN","HEIGHT_ROOF","GROUND_ELEVATION"]
    ].head(20)
)

gdf_small = gdf[gdf["HEIGHT_ROOF"].notna()].copy()

gdf_small = gdf_small.nlargest(50000,"HEIGHT_ROOF")

gdf_small = gdf_small.to_crs(4326)

st.write("Geometry Type:")
st.write(gdf_small.geometry.geom_type.unique())

st.write("Sample Height:")
st.write(gdf_small["HEIGHT_M"].head())

st.write(gdf_small.columns.tolist())

st.write(gdf_small[["HEIGHT_ROOF", "HEIGHT_M"]].head())

st.write(gdf_small.crs)

st.write("Buildings used:", len(gdf_small))
st.write(gdf_small.total_bounds)

gdf_small = gdf_small.drop(
    columns=["LAST_EDITED_DATE"],
    errors="ignore"
)
gdf_small = gdf_small[
    ["BIN","HEIGHT_ROOF","GROUND_ELEVATION","HEIGHT_M","geometry"]
]
geojson_data = gdf_small.to_json()
layer = pdk.Layer(
    "GeoJsonLayer",
    gdf_small.__geo_interface__,
    pickable=True,
    filled=True,
    extruded=True,
    wireframe=True,
    get_elevation="properties.HEIGHT_M",
    get_fill_color=[255, 0, 0, 150],
)
view_state = pdk.ViewState(
    latitude=40.758,
    longitude=-73.9855,
    zoom=14,
    pitch=50,
    bearing=0,
)
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="road",
    tooltip={
        "html": """
        <b>BIN:</b> {BIN}<br/>
        <b>Height:</b> {HEIGHT_ROOF} ft
        """
    }
)
layer = pdk.Layer(
    "GeoJsonLayer",
    gdf_small.__geo_interface__,
    pickable=True,
    extruded=True,
    filled=True,
    wireframe=False,
    get_elevation="properties.HEIGHT_M",
    get_fill_color="[HEIGHT_M, 100, 200]",
)

st.pydeck_chart(deck)

st.subheader("Top 10 - Tallest Buildings")

top10 = gdf.nlargest(10,"HEIGHT_ROOF")
[
    ["BIN","HEIGHT_ROOF","GROUND_ELEVATION"]
]
st.dataframe(top10)