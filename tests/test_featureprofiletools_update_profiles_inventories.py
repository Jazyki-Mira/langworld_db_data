from langworld_db_data.featureprofiletools.update_profiles_inventories import (
    rename_value_in_profiles_and_inventories,
)
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES
from tests.test_helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard

DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES = (
    DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / "update_profiles_inventories"
)

DIR_WITH_INPUT_FILES = DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "input"

DIR_WITH_INPUT_FEATURE_PROFILES = DIR_WITH_INPUT_FILES / "feature_profiles"

DIR_WITH_INPUT_INVENTORIES = DIR_WITH_INPUT_FILES / "inventories"

DIR_WITH_OUTPUT_GOLD_STANDARD_FILES = (
    DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "output_gold_standard"
)

DIR_WITH_OUTPUT_GOLD_STANDARD_FEATURE_PROFILES = (
    DIR_WITH_OUTPUT_GOLD_STANDARD_FILES / "feature_profiles"
)

DIR_WITH_OUTPUT_GOLD_STANDARD_INVENTORIES = DIR_WITH_OUTPUT_GOLD_STANDARD_FILES / "inventories"


# Currently I am working with values only, but I put features_listed_values.csv in this folder where features.csv will
# be added later.


def test_rename_value_in_profiles_and_inventories():
    # First change files in tmp up to their default variants
    rename_value_in_profiles_and_inventories(
        id_of_value_to_rename="A-9-2",
        new_value_name="Представлены исключительно дифтонги",
        input_feature_profiles_dir=DIR_WITH_INPUT_FEATURE_PROFILES,
        output_feature_profiles_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES,
        input_inventories_dir=DIR_WITH_INPUT_INVENTORIES,
        output_inventories_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "inventories",
    )

    output_filenames_list = DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES.glob("*.csv")
    for filename in output_filenames_list:
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / filename.name,
            gold_standard_file=DIR_WITH_OUTPUT_GOLD_STANDARD_FEATURE_PROFILES / filename.name,
            unlink_if_successful=True,
        )
    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES
        / "inventories"
        / "features_listed_values.csv",
        gold_standard_file=DIR_WITH_OUTPUT_GOLD_STANDARD_INVENTORIES
        / "features_listed_values.csv",
        unlink_if_successful=True,
    )
