from langworld_db_data.tools.featureprofiles.feature_profile_converter import (
    FeatureProfileConverter,
)
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES
from tests.test_helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard

DIR_WITH_CONVERT_TEST_FILES = DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / "convert_from_excel"


def test_convert_from_excel():
    for file in DIR_WITH_CONVERT_TEST_FILES.glob("*.xlsm"):
        path_to_resulting_csv = FeatureProfileConverter().excel_to_csv(file)

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=path_to_resulting_csv,
            gold_standard_file=DIR_WITH_CONVERT_TEST_FILES / f"{file.stem}_benchmark.csv",
        )
