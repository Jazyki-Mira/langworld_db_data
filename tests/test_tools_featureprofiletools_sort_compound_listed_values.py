from langworld_db_data.tools.featureprofiles.sort_compound_listed_values import (
    _sort_compound_listed_values_in_one_profile,
    sort_compound_listed_values_in_feature_profiles,
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


def test_sort_compound_listed_values_in_one_profile():
    for file in DIR_WITH_PROFILES.glob("*.csv"):
        output_path = TEST_OUTPUT_DIR / file.name
        _sort_compound_listed_values_in_one_profile(
            path_to_input_feature_profile=file, path_to_output_feature_profile=output_path
        )
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=output_path, gold_standard_file=GOLD_STANDARD_DIR / file.name
        )


def test_sort_compound_listed_values_in_feature_profiles():
    sort_compound_listed_values_in_feature_profiles(
        dir_with_feature_profiles=DIR_WITH_PROFILES,
        output_dir=TEST_OUTPUT_DIR,
    )

    for file in DIR_WITH_PROFILES.glob("*.csv"):
        output_path = TEST_OUTPUT_DIR / file.name
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=output_path, gold_standard_file=GOLD_STANDARD_DIR / file.name
        )
