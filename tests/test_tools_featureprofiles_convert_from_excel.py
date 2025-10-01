import zipfile

from langworld_db_data.tools.convert_from_excel.convert_from_excel import (
    _unzip_file,
    convert_from_excel,
)
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES
from tests.test_helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard

DIR_WITH_CONVERT_TEST_FILES = DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / "convert_from_excel"


def test_convert_from_excel():
    for file in DIR_WITH_CONVERT_TEST_FILES.glob("*.xlsm"):
        path_to_resulting_csv = convert_from_excel(file)

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=path_to_resulting_csv,
            gold_standard_file=DIR_WITH_CONVERT_TEST_FILES / f"{file.stem}_benchmark.csv",
        )


def test__unzip_file_function(tmp_path):
    # Setup: create a zip to extract
    zip_path = tmp_path / "mini.zip"
    file_name = "mini_inside.txt"
    mini_content = b"Mini!"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(file_name, mini_content)
    extract_dir = tmp_path / "output_dir"
    extract_dir.mkdir()
    # Call _unzip_file directly
    _unzip_file(zip_path, extract_dir)
    extracted = extract_dir / file_name
    assert extracted.exists()
    assert extracted.read_bytes() == mini_content


# --- FOCUSED TEST ON LINES 95-97 (extractall logic) ---
def test_extractall_behavior(tmp_path):
    # This test verifies the zipfile.ZipFile/extractall combo directly
    zip_path = tmp_path / "archive.zip"
    name = "a.txt"
    content = b"Ziplogic!"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr(name, content)
    extract_to = tmp_path / "out"
    extract_to.mkdir()

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    target = extract_to / name
    assert target.exists() and target.read_bytes() == content
