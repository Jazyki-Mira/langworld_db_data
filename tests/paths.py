from pathlib import Path

DIR_WITH_TEST_FILES = Path(__file__).parent / "test_data"

DIR_WITH_ADDERS_TEST_FILES = DIR_WITH_TEST_FILES / "adders"
DIR_WITH_ADDERS_FEATURE_PROFILES = DIR_WITH_ADDERS_TEST_FILES / "feature_profiles"
INPUT_FILE_WITH_LISTED_VALUES = DIR_WITH_ADDERS_TEST_FILES / "features_listed_values.csv"

OUTPUT_DIR_FOR_LISTED_VALUE_ADDER_FEATURE_PROFILES = (
    DIR_WITH_ADDERS_FEATURE_PROFILES / "output_listed_value_adder"
)
OUTPUT_DIR_FOR_FEATURE_ADDER_FEATURE_PROFILES = (
    DIR_WITH_ADDERS_FEATURE_PROFILES / "output_feature_adder"
)

DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES = DIR_WITH_TEST_FILES / "featureprofiletools"

DIR_WITH_FILETOOLS_TEST_FILES = DIR_WITH_TEST_FILES / "filetools"
PATH_TO_TEST_OUTPUT_TXT_FILE = DIR_WITH_FILETOOLS_TEST_FILES / "test_file_write.txt"
PATH_TO_TEST_OUTPUT_CSV_FILE = DIR_WITH_FILETOOLS_TEST_FILES / "test_file_write.csv"

DIR_WITH_REMOVERS_TEST_FILES = DIR_WITH_TEST_FILES / "removers"
DIR_WITH_REMOVERS_FEATURE_PROFILES = DIR_WITH_REMOVERS_TEST_FILES / "feature_profiles"
INPUT_FILE_WITH_LISTED_VALUES_FOR_REMOVERS = (
    DIR_WITH_ADDERS_TEST_FILES / "features_listed_values.csv"
)
OUTPUT_DIR_FOR_LISTED_VALUE_REMOVER_FEATURE_PROFILES = (
    DIR_WITH_REMOVERS_TEST_FILES / "output_listed_value_remover"
)
OUTPUT_DIR_FOR_FEATURE_REMOVER_FEATURE_PROFILES = (
    DIR_WITH_REMOVERS_TEST_FILES / "output_feature_remover"
)

DIR_WITH_VALIDATORS_TEST_FILES = DIR_WITH_TEST_FILES / "validators_and_markdown_generators"
DIR_WITH_TEST_FEATURE_PROFILES = DIR_WITH_VALIDATORS_TEST_FILES / "feature_profiles"

DIR_WITH_WRITERS_TEST_FILES = DIR_WITH_TEST_FILES / "writers"
