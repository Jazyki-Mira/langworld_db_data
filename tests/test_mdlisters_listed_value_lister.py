from langworld_db_data.mdlisters.listed_value_lister import ListedValueLister
from tests.helpers import (
    check_existence_of_output_csv_file_and_compare_with_gold_standard,
)
from tests.paths import DIR_WITH_TEST_FEATURE_PROFILES, DIR_WITH_VALIDATORS_TEST_FILES


def test_write_grouped_by_feature():
    lister = ListedValueLister(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_features=DIR_WITH_VALIDATORS_TEST_FILES / "features_OK.csv",
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES
        / "features_listed_values_OK.csv",
    )

    output_file = DIR_WITH_VALIDATORS_TEST_FILES / "listed_values_by_feature.md"

    lister.write_grouped_by_feature(output_file=output_file)

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=output_file,
        gold_standard_file=DIR_WITH_VALIDATORS_TEST_FILES
        / "listed_values_by_feature_sample.md",
    )
