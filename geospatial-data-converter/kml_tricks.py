import zipfile
from io import StringIO

import bs4
import geopandas as gpd
import lxml  # nosec
import pandas as pd


def parse_descriptions_to_geodf(geodf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Parses Descriptions from Google Earth file to a GeoDataFrame object"""

    dataframes = []

    # Iterate over descriptions and extract data
    for desc in geodf["Description"]:
        desc_as_io = StringIO(desc)

        # Try to read the description into a DataFrame
        parsed_html = pd.read_html(desc_as_io)
        try:
            temp_df = parsed_html[1].T
        except IndexError:
            temp_df = parsed_html[0].T

        # Set DataFrame header and remove the first row
        temp_df.columns = temp_df.iloc[0]
        temp_df = temp_df.iloc[1:]

        dataframes.append(temp_df)

    # Combine all DataFrames
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Add geometry data
    combined_df["geometry"] = geodf["geometry"]

    # Create a GeoDataFrame with the combined data and original CRS
    result_geodf = gpd.GeoDataFrame(combined_df, crs=geodf.crs)

    return result_geodf


def load_kmz_as_geodf(file_path: str) -> gpd.GeoDataFrame:
    """Loads a KMZ file into a GeoPandas DataFrame, assuming the KMZ contains one KML file"""

    # Open the KMZ file
    with zipfile.ZipFile(file_path, "r") as kmz:
        # List all KML files in the KMZ
        kml_files = [file for file in kmz.namelist() if file.endswith(".kml")]

    # Ensure there's only one KML file in the KMZ
    if len(kml_files) != 1:
        raise IndexError(
            "KMZ contains more than one KML. Please extract or convert to multiple KMLs.",
        )

    # Read the KML file into a GeoDataFrame
    geodf = gpd.read_file(
        f"zip://{file_path}/{kml_files[0]}",
        driver="KML",
        engine="pyogrio",
    )

    return geodf


def load_ge_file(file_path: str) -> gpd.GeoDataFrame:
    """Loads a KML or KMZ file and parses its descriptions into a GeoDataFrame"""

    if file_path.endswith(".kml"):
        return parse_descriptions_to_geodf(
            gpd.read_file(file_path, driver="KML", engine="pyogrio"),
        )
    elif file_path.endswith(".kmz"):
        return parse_descriptions_to_geodf(load_kmz_as_geodf(file_path))
    raise ValueError("The file must have a .kml or .kmz extension.")


def extract_data_from_kml_code(kml_code: str) -> pd.DataFrame:
    """Extracts data from KML code into a DataFrame using SimpleData tags, excluding embedded tables in feature descriptions"""

    # Parse the KML source code
    soup = bs4.BeautifulSoup(kml_code, "html.parser")

    # Find all SchemaData tags (representing rows)
    schema_data_tags = soup.find_all("schemadata")

    # Create a generator that yields a dictionary for each row, containing the Placemark name and each SimpleData field
    row_dicts = (
        {
            "Placemark_name": tag.parent.parent.find("name").text
            if tag.parent.parent.find("name")
            else "[no name]",
            **{field.get("name"): field.text for field in tag.find_all("simpledata")},
        }
        for tag in schema_data_tags
    )

    # Convert the row dictionaries into a DataFrame
    df = pd.DataFrame(row_dicts)

    return df


def extract_kml_code_from_file(file_path: str) -> str:
    """Extracts KML source code from a Google Earth file (KML or KMZ)"""

    file_extension = file_path.lower().split(".")[-1]

    if file_extension == "kml":
        with open(file_path, "r") as kml_file:
            kml_code = kml_file.read()
    elif file_extension == "kmz":
        with zipfile.ZipFile(file_path) as kmz_file:
            # Find all KML files in the KMZ
            kml_files = [
                file for file in kmz_file.namelist() if file.lower().endswith(".kml")
            ]

            if len(kml_files) != 1:
                raise IndexError(
                    "KMZ file contains more than one KML. Please extract or convert to multiple KMLs.",
                )

            with kmz_file.open(kml_files[0]) as kml_file:
                # Decode the KML file's content from bytes to string
                kml_code = kml_file.read().decode()
    else:
        raise ValueError("The input file must have a .kml or .kmz extension.")

    return kml_code


def extract_data_from_ge_file(file_path: str) -> gpd.GeoDataFrame:
    """Extracts data from a Google Earth file (KML or KMZ) into a GeoDataFrame using SimpleData tags, excluding embedded tables in feature descriptions"""

    data_df = extract_data_from_kml_code(extract_kml_code_from_file(file_path))

    if file_path.endswith(".kmz"):
        ge_file_gdf = load_kmz_as_geodf(file_path)
    else:
        ge_file_gdf = gpd.read_file(file_path, driver="KML", engine="pyogrio")

    geo_df = gpd.GeoDataFrame(
        data_df,
        geometry=ge_file_gdf["geometry"],
        crs=ge_file_gdf.crs,
    )

    return geo_df


def load_ge_data(file_path: str) -> gpd.GeoDataFrame:
    """Extracts data from a Google Earth file (KML or KMZ) and handles errors due to parsing issues"""

    kml_code = extract_kml_code_from_file(file_path)

    # Choose the extraction method based on the presence of SimpleData or SimpleField tags in the KML code
    primary_func, fallback_func = (
        (extract_data_from_ge_file, load_ge_file)
        if any(tag in kml_code.lower() for tag in ("<simpledata", "<simplefield"))
        else (load_ge_file, extract_data_from_ge_file)
    )

    try:
        data_df = primary_func(file_path)
    except (
        pd.errors.ParserError,
        lxml.etree.ParserError,
        lxml.etree.XMLSyntaxError,
        ValueError,
    ):
        data_df = fallback_func(file_path)

    return data_df
