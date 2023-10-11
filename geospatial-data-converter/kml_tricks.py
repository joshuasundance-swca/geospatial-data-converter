import zipfile
from typing import Any

import bs4
import fiona
import geopandas as gpd
import pandas as pd

fiona.drvsupport.supported_drivers["KML"] = "rw"


def parse_description_to_gdf(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    parsed_dataframes = [
        pd.read_html(desc)[1 if len(pd.read_html(desc)) > 1 else 0].T
        for desc in gdf["Description"]
    ]

    for df in parsed_dataframes:
        df.columns = df.iloc[0]
        df.drop(df.index[0], inplace=True)

    combined_df = pd.concat(parsed_dataframes, ignore_index=True)
    combined_df["geometry"] = gdf["geometry"]

    return gpd.GeoDataFrame(combined_df, crs=gdf.crs)


def read_kml_file(path: str) -> Any:
    with zipfile.ZipFile(path, "r") as kmz:
        kml_files = [f for f in kmz.namelist() if f.endswith(".kml")]

    if len(kml_files) != 1:
        raise IndexError(
            "KMZ contains more than one KML. Extract or convert to multiple KMLs.",
        )

    return gpd.read_file(f"zip://{path}\\{kml_files[0]}", driver="KML")


def parse_file_to_gdf(path: str) -> gpd.GeoDataFrame:
    if path.endswith(".kml"):
        return parse_description_to_gdf(gpd.read_file(path, driver="KML"))

    if path.endswith(".kmz"):
        return parse_description_to_gdf(read_kml_file(path))

    raise ValueError("File must end with .kml or .kmz")


def extract_data_from_kml_code(kml_code: str) -> pd.DataFrame:
    soup = bs4.BeautifulSoup(kml_code, "html.parser")
    rows = soup.find_all("schemadata")

    data = (
        {field.get("name"): field.text for field in row.find_all("simpledata")}
        for row in rows
    )

    return pd.DataFrame(data)


def extract_kml_from_file(file_path: str) -> str:
    file_extension = file_path.lower().split(".")[-1]
    kml_files = None

    if file_extension == "kml":
        with open(file_path, "r") as kml:
            return kml.read()

    if file_extension == "kmz":
        with zipfile.ZipFile(file_path) as kmz:
            kml_files = [f for f in kmz.namelist() if f.lower().endswith(".kml")]
        if len(kml_files) != 1:
            raise IndexError(
                "KMZ contains more than one KML. Extract or convert to multiple KMLs.",
            )
        with kmz.open(kml_files[0]) as kml:
            return kml.read().decode()

    raise ValueError("File path must end with .kml or .kmz")


def extract_data_from_file(file_path: str) -> pd.DataFrame:
    df = extract_data_from_kml_code(extract_kml_from_file(file_path))

    if file_path.endswith(".kmz"):
        file_gdf = read_kml_file(file_path)
    else:
        file_gdf = gpd.read_file(file_path, driver="KML")

    return gpd.GeoDataFrame(df, geometry=file_gdf["geometry"], crs=file_gdf.crs)


def read_ge_file(file_path: str) -> pd.DataFrame:
    try:
        return parse_file_to_gdf(file_path)
    except (pd.errors.ParserError, ValueError):
        return extract_data_from_file(file_path)
