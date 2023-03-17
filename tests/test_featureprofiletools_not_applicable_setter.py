import pytest

from langworld_db_data.featureprofiletools.not_applicable_setter import (
    NotApplicableSetter,
)
from tests.helpers import (
    check_existence_of_output_csv_file_and_compare_with_gold_standard,
)
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES

DIR_WITH_TEST_FEATURE_PROFILES = (
    DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES
    / "feature_profiles_for_not_applicable_setter"
)
TEST_FILE_WITH_RULES = (
    DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / "features_not_applicable_rules.yaml"
)


@pytest.fixture(scope="function")
def test_setter():
    return NotApplicableSetter(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_rules=TEST_FILE_WITH_RULES,
        output_dir=DIR_WITH_TEST_FEATURE_PROFILES / "output",
    )


def test__init__(test_setter):
    print(f"\nTEST rules from YAML: {test_setter.rules}")
    assert "A-9" in test_setter.rules and "K-13" in test_setter.rules

    print(f"\nTEST feature profiles: {test_setter.feature_profiles}")
    assert len(test_setter.feature_profiles) == len(
        list(DIR_WITH_TEST_FEATURE_PROFILES.glob("*.csv"))
    )


def test_replace_not_stated_with_not_applicable_in_all_profiles_according_to_rules(
    test_setter,
):
    test_setter.replace_not_stated_with_not_applicable_in_all_profiles_according_to_rules()

    dir_with_benchmark_files = DIR_WITH_TEST_FEATURE_PROFILES / "output_gold_standard"

    for benchmark_file in dir_with_benchmark_files.glob("*.csv"):
        test_output_file = (
            DIR_WITH_TEST_FEATURE_PROFILES / "output" / benchmark_file.name
        )

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=benchmark_file,
        )
