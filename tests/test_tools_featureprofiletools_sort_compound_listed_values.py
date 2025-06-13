from langworld_db_data.tools.featureprofiles.sort_compound_listed_values import (
    sort_compound_listed_values,
)
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import DIR_WITH_TEST_FILES

DIR_WITH_PROFILES = (
    DIR_WITH_TEST_FILES / "tools" / "featureprofiles" / "sort_compound_listed_values"
)
TEST_OUTPUT_DIR = DIR_WITH_PROFILES / "output"
GOLD_STANDARD_DIR = DIR_WITH_PROFILES / "gold_standard"

if not TEST_OUTPUT_DIR.exists():
    TEST_OUTPUT_DIR.mkdir()


def test_sort_compound_listed_values():
    for file in DIR_WITH_PROFILES.glob("*.csv"):
        output_path = TEST_OUTPUT_DIR / file.name
        sort_compound_listed_values(
            path_to_input_feature_profile=file, path_to_output_feature_profile=output_path
        )
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=output_path, gold_standard_file=GOLD_STANDARD_DIR / file.name
        )
