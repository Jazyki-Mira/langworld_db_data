from langworld_db_data.featureprofiletools.convert_from_excel import convert_from_excel
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES
from tests.test_helpers import (
    check_existence_of_output_csv_file_and_compare_with_gold_standard,
)

DIR_WITH_CONVERT_TEST_FILES = (
    DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / "convert_from_excel"
)


def test_convert_from_excel():
    path_to_excel_file = DIR_WITH_CONVERT_TEST_FILES / "french.xlsm"
    path_to_resulting_csv = convert_from_excel(path_to_excel_file)

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=path_to_resulting_csv,
        gold_standard_file=DIR_WITH_CONVERT_TEST_FILES / "french_gold_standard.csv",
    )
