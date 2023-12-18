import asyncio
import os

import geopandas as gpd
import streamlit as st
from aiohttp import ClientSession
from restgdf import FeatureLayer

from utils import read_file, convert, output_format_dict

__version__ = "1.0.1"


def st_init_null(*variable_names) -> None:
    for variable_name in variable_names:
        if variable_name not in st.session_state:
            st.session_state[variable_name] = None


st_init_null(
    "fn_without_extension",
    "gdf",
)


# --- Initialization ---
st.set_page_config(
    page_title=f"geospatial-data-converter v{__version__}",
    page_icon="🌎",
)


# Enter a URL
st.text_input(
    "Enter a URL to an ArcGIS featurelayer",
    key="arcgis_url",
    placeholder="https://maps1.vcgov.org/arcgis/rest/services/Beaches/MapServer/6",
)


# Or upload a file
st.file_uploader(
    "Choose a geospatial file",
    key="uploaded_file",
    type=["kml", "kmz", "geojson", "zip"],
)


async def get_arcgis_data(url: str) -> tuple[str, gpd.GeoDataFrame]:
    """Get data from an ArcGIS featurelayer"""
    async with ClientSession() as session:
        rest = await FeatureLayer.from_url(url, session=session)
        name = rest.name
        gdf = await rest.getgdf()
    return name, gdf


if st.session_state.arcgis_url:
    st.session_state.fn_without_extension, gdf = asyncio.run(
        get_arcgis_data(st.session_state.arcgis_url),
    )

    st.session_state.gdf = gdf

elif st.session_state.uploaded_file is not None:
    # try:
    st.session_state.fn_without_extension, _ = os.path.splitext(
        os.path.basename(st.session_state.uploaded_file.name),
    )
    st.session_state.gdf = read_file(st.session_state.uploaded_file)

if st.session_state.gdf is not None:
    st.selectbox(
        "Select output format",
        output_format_dict.keys(),
        key="output_format",
        index=0,
    )

    if st.button("Convert"):
        file_ext, dl_ext, mimetype = output_format_dict[st.session_state.output_format]
        output_fn = f"{st.session_state.fn_without_extension}.{file_ext}"
        dl_fn = f"{st.session_state.fn_without_extension}.{dl_ext}"

        st.session_state.converted_data = convert(
            gdf=st.session_state.gdf,
            output_name=output_fn,
            output_format=st.session_state.output_format,
        )

        st.download_button(
            label="Download",
            data=st.session_state.converted_data,
            file_name=dl_fn,
            mime=mimetype,
        )

    st.markdown(
        "---\n"
        f"## {st.session_state.fn_without_extension}\n"
        f"### CRS: *{st.session_state.gdf.crs}*\n"
        f"### Shape: *{st.session_state.gdf.shape}*\n"
        "*(geometry omitted for display purposes)*",
    )

    display_df = st.session_state.gdf.drop(columns=["geometry"]).to_dict(
        orient="records",
    )

    st.dataframe(display_df)
