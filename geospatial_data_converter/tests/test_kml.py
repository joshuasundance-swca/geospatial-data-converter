import sys

sys.path.append("..")
from utils import convert, read_file


def test_kml_coversion():
    with open("boundary.kml", "rb") as f:
        kml = read_file(f)
    converted_data = convert(kml, "boundary_converted.kml", "kml")
    with open("boundary_converted.kml", "wb") as f:
        f.write(converted_data)


def test_kmz_conversion():
    pass
