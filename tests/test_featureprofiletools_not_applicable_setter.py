import pytest

from langworld_db_data.featureprofiletools.not_applicable_setter import *
from langworld_db_data.filetools.csv_xls import read_csv
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES

DIR_WITH_TEST_FEATURE_PROFILES = (
    DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / 'feature_profiles_for_not_applicable_setter'
)
TEST_FILE_WITH_RULES = DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / 'features_not_applicable_rules.yaml'


@pytest.fixture(scope='function')
def test_setter():
    return NotApplicableSetter(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_rules=TEST_FILE_WITH_RULES,
        output_dir=DIR_WITH_TEST_FEATURE_PROFILES / 'output'
    )


def test__init__(test_setter):
    print(f'\nTEST rules from YAML: {test_setter.rules}')
    assert 'A-9' in test_setter.rules and 'K-13' in test_setter.rules

    print(f'\nTEST feature profiles: {test_setter.feature_profiles}')
    assert len(test_setter.feature_profiles) == len(list(DIR_WITH_TEST_FEATURE_PROFILES.glob('*.csv')))


def test_replace_not_stated_with_not_applicable_in_all_profiles_according_to_rules(test_setter):
    test_setter.replace_not_stated_with_not_applicable_in_all_profiles_according_to_rules()

    dir_with_benchmark_files = DIR_WITH_TEST_FEATURE_PROFILES / 'output_gold_standard'

    for benchmark_file in dir_with_benchmark_files.glob('*.csv'):
        test_output_file = DIR_WITH_TEST_FEATURE_PROFILES / 'output' / benchmark_file.name
        assert test_output_file.exists()

        output_lines = read_csv(test_output_file, read_as='plain_rows')
        benchmark_lines = read_csv(benchmark_file, read_as='plain_rows')

        for output_line, benchmark_line in zip(output_lines, benchmark_lines):
            assert output_line == benchmark_line

        test_output_file.unlink()
