import os
import pytest
from utils import convert, read_file, output_format_dict

input_exts = ["kml", "kmz", "geojson", "zip"]
output_exts = output_format_dict.keys()


@pytest.mark.parametrize("in_ext", input_exts)
@pytest.mark.parametrize("out_ext", output_exts)
def test_coversion(in_ext: str, out_ext: str) -> None:
    test_file = f"test.{in_ext}"
    test_file_path = os.path.join(os.getcwd(), "tests", "test_data", test_file)
    with open(test_file_path, "rb") as f:
        in_file = read_file(f)
    out_file = f"test.{output_format_dict[out_ext][0]}"
    converted_data = convert(in_file, out_file, out_ext)
    with open("test.kml", "wb") as f:
        f.write(converted_data)
