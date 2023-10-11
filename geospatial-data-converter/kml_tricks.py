import zipfile

import bs4
import fiona
import geopandas as gpd
import pandas as pd

fiona.drvsupport.supported_drivers["KML"] = "rw"


def desctogdf(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Parses Descriptions from Google Earth file to create a legit gpd.GeoDataFrame"""
    dfs = []
    len(gdf)
    # pull chunks of data from feature descriptions
    for idx, desc in enumerate(gdf["Description"], start=1):
        try:
            tmpdf = pd.read_html(desc)[1].T
        except IndexError:
            tmpdf = pd.read_html(desc)[0].T
        tmpdf.columns = tmpdf.iloc[0]
        tmpdf = tmpdf.iloc[1:]
        dfs.append(tmpdf)
    # join chunks together
    ccdf = pd.concat(dfs, ignore_index=True)
    ccdf["geometry"] = gdf["geometry"]
    df = gpd.GeoDataFrame(ccdf, crs=gdf.crs)
    return df


def readkmz(path: str) -> gpd.GeoDataFrame:
    """Simply read kmz using geopandas/fiona without parsing Descriptions"""
    # get name of kml in kmz (should be doc.kml but we don't assume)
    with zipfile.ZipFile(path, "r") as kmz:
        namelist = [f for f in kmz.namelist() if f.endswith(".kml")]
    if len(namelist) != 1:
        # this should never really happen
        raise IndexError(
            "kmz contains more than one kml. Extract or convert to multiple kmls.",
        )
    # return GeoDataFrame by reading contents of kmz
    return gpd.read_file("zip://{}\\{}".format(path, namelist[0]), driver="KML")


def ge_togdf(path: str) -> gpd.GeoDataFrame:
    """Return gpd.GeoDataFrame after reading kmz or kml and parsing Descriptions"""
    if path.endswith(".kml"):
        gdf = desctogdf(gpd.read_file(path, driver="KML"))
    elif path.endswith(".kmz"):
        gdf = desctogdf(readkmz(path))
    else:
        raise ValueError("File must end with .kml or .kmz")
    return gdf


def simpledata_fromcode(kmlcode: str) -> pd.DataFrame:
    """Return DataFrame extracted from KML code
    parameter kmlcode (str): kml source code
    Uses simpledata tags, NOT embedded tables in feature descriptions
    """
    # get the KML source code as a BeautifulSoup object
    soup = bs4.BeautifulSoup(kmlcode, "html.parser")
    # find all rows (schemadata tags) in the soup
    rowtags = soup.find_all("schemadata")
    # generator expression yielding a {name: value} dict for each row
    rowdicts = (
        {field.get("name"): field.text for field in row.find_all("simpledata")}
        for row in rowtags
    )
    # return pd.DataFrame from row dict generator
    return pd.DataFrame(rowdicts)


def kmlcode_fromfile(gefile: str) -> str:
    """Return kml source code (str) extracted from Google Earth File
    parameter gefile (str): absolute or relative path to Google Earth file
    (kmz or kml)
    Uses simpledata tags, NOT embedded tables in feature descriptions
    """
    fileextension = gefile.lower().split(".")[-1]
    if fileextension == "kml":
        with open(gefile, "r") as kml:
            kmlsrc = kml.read()
    elif fileextension == "kmz":
        with zipfile.ZipFile(gefile) as kmz:
            # there should only be one kml file and it should be named doc.kml
            # we won't make that assumption
            kmls = [f for f in kmz.namelist() if f.lower().endswith(".kml")]
            if len(kmls) != 1:
                raise IndexError(
                    "kmz contains more than one kml. Extract or convert to multiple kmls.",
                )
            with kmz.open(kmls[0]) as kml:
                # .decode() because zipfile.ZipFile.open(name).read() -> bytes
                kmlsrc = kml.read().decode()
    else:
        raise ValueError("parameter gefile must end with .kml or .kmz")
    return kmlsrc


def simpledata_fromfile(gefile: str) -> pd.DataFrame:
    """Return DataFrame extracted from Google Earth File
    parameter gefile (str): absolute or relative path to Google Earth file
    (kmz or kml)
    Uses simpledata tags, NOT embedded tables in feature descriptions
    """
    df = simpledata_fromcode(kmlcode_fromfile(gefile))
    if gefile.endswith(".kmz"):
        gefile_gdf = readkmz(gefile)
    else:
        gefile_gdf = gpd.read_file(gefile, driver="KML")
    gdf = gpd.GeoDataFrame(df, geometry=gefile_gdf["geometry"], crs=gefile_gdf.crs)
    return gdf


def readge(gefile: str) -> pd.DataFrame:
    """Extract data from Google Earth file & save as zip
    parameter gefile (str): absolute or relative path to Google Earth file
    parameter zipfile (str): absolute or relative path to output zip file
    Will read simpledata tags OR embedded tables in feature descriptions
    """
    # retrieve DataFrame from gefile and use its to_file method
    try:
        # this function pulls data from tables embedded in feature descriptions
        df = ge_togdf(gefile)
    except (pd.errors.ParserError, ValueError):
        # this function pulls data from simpledata tags
        df = simpledata_fromfile(gefile)
    return df
