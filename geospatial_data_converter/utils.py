import io
import os
import zipfile
from tempfile import TemporaryDirectory
from typing import BinaryIO
import geopandas as gpd

from kml_tricks import load_ge_data

output_format_dict = {
    "ESRI Shapefile": ("shp", "zip", "application/zip"),  # must be zipped
    "OpenFileGDB": ("gdb", "zip", "application/zip"),  # must be zipped
    "GeoJSON": ("geojson", "geojson", "application/geo+json"),
    "CSV": ("csv", "csv", "text/csv"),
    "KML": ("kml", "kml", "application/vnd.google-earth.kml+xml"),
}


def read_file(file: BinaryIO, *args, **kwargs) -> gpd.GeoDataFrame:
    """Read a file and return a GeoDataFrame"""
    basename, ext = os.path.splitext(os.path.basename(file.name))
    ext = ext.lower().strip(".")
    if ext == "zip":
        with TemporaryDirectory() as tmp_dir:
            tmp_file_path = os.path.join(tmp_dir, file.name)
            with open(tmp_file_path, "wb") as tmp_file:
                tmp_file.write(file.read())
            return gpd.read_file(
                f"zip://{tmp_file_path}",
                *args,
                engine="pyogrio",
                **kwargs,
            )
    elif ext in ("kml", "kmz"):
        with TemporaryDirectory() as tmp_dir:
            tmp_file_path = os.path.join(tmp_dir, file.name)
            with open(tmp_file_path, "wb") as tmp_file:
                tmp_file.write(file.read())
            return load_ge_data(tmp_file_path)
    return gpd.read_file(file, *args, engine="pyogrio", **kwargs)


def zip_dir(directory: str) -> bytes:
    """Zip a directory and return the bytes"""
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                new_member = os.path.join(root, file)
                zipf.write(
                    new_member,
                    os.path.relpath(new_member, directory),
                )

    return zip_buffer.getvalue()


def convert(gdf: gpd.GeoDataFrame, output_name: str, output_format: str) -> bytes:
    """Convert a GeoDataFrame to the specified format"""
    with TemporaryDirectory() as tmpdir:
        out_path = os.path.join(tmpdir, output_name)

        if output_format == "CSV":
            gdf.to_csv(out_path)
        else:
            gdf.to_file(out_path, driver=output_format, engine="pyogrio")

        if output_format in ("ESRI Shapefile", "OpenFileGDB"):
            output_bytes = zip_dir(tmpdir)
        else:
            with open(out_path, "rb") as f:
                output_bytes = f.read()

        return output_bytes
