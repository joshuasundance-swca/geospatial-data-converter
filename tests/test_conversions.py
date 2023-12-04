import os
import pytest
from geospatial_data_converter.utils import convert, read_file

input_exts = ["kml", "kmz", "geojson", "zip"]
output_exts = ["KML", "ESRI Shapefile", "GeoJSON", "CSV", "OpenFileGDB"]
output_format_dict = {
    "ESRI Shapefile": "shp",
    "GeoJSON": "geojson",
    "CSV": "csv",
    "KML": "kml",
    "OpenFileGDB": "gdb",
}


@pytest.mark.parametrize("in_ext", input_exts)
@pytest.mark.parametrize("out_ext", output_exts)
def test_kml_coversion(in_ext: str, out_ext: str) -> None:
    test_file = f"test.{in_ext}"
    test_file_path = os.path.join(os.getcwd(), "tests", "test_data", test_file)
    with open(test_file_path, "rb") as f:
        kml = read_file(f)
    out_file = f"test.{output_format_dict[out_ext]}"
    converted_data = convert(kml, out_file, out_ext)
    with open("test.kml", "wb") as f:
        f.write(converted_data)
