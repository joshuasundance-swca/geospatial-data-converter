import os

import streamlit as st

from utils import read_file, convert, output_format_dict

__version__ = "0.0.2"

# --- Initialization ---
st.set_page_config(
    page_title=f"geospatial-data-converter v{__version__}",
    page_icon="🌎",
)


# Upload the file
st.file_uploader(
    "Choose a geospatial file",
    key="uploaded_file",
    type=["kml", "kmz", "geojson", "zip"],
)


if st.session_state.uploaded_file is not None:
    fn_without_extension, _ = os.path.splitext(
        os.path.basename(st.session_state.uploaded_file.name),
    )

    st.session_state.gdf = read_file(st.session_state.uploaded_file)

    st.selectbox(
        "Select output format",
        output_format_dict.keys(),
        key="output_format",
        index=0,
    )

    if st.button("Convert"):
        file_ext, dl_ext, mimetype = output_format_dict[st.session_state.output_format]
        output_fn = f"{fn_without_extension}.{file_ext}"
        dl_fn = f"{fn_without_extension}.{dl_ext}"

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
        f"## {fn_without_extension}\n"
        f"### CRS: *{st.session_state.gdf.crs}*\n"
        f"### Shape: *{st.session_state.gdf.shape}*\n"
        "*(geometry omitted for display purposes)*",
    )

    display_df = st.session_state.gdf.drop(columns=["geometry"])

    st.dataframe(display_df)
