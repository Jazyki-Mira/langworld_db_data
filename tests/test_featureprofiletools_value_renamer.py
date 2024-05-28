import pytest

from pathlib import Path

from langworld_db_data.featureprofiletools.value_renamer import ValueRenamer, ValueRenamerError
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


def test_rename_value_in_profiles_and_inventories():
    # First change files in tmp up to their default variants
    value_renamer = ValueRenamer(
        input_feature_profiles_dir=DIR_WITH_INPUT_FEATURE_PROFILES,
        output_feature_profiles_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES,
        input_inventories_dir=DIR_WITH_INPUT_INVENTORIES,
        output_inventories_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "inventories",
    )
    value_renamer.rename_value_in_profiles_and_inventories(
        id_of_value_to_rename="A-9-2",
        new_value_name="Представлены исключительно дифтонги",
    )

    output_filenames = DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES.glob("*.csv")
    for filename in output_filenames:
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / filename.name,
            gold_standard_file=DIR_WITH_OUTPUT_GOLD_STANDARD_FEATURE_PROFILES / filename.name,
            unlink_if_successful=True,
        )
    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=(
            DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES
            / "inventories"
            / "features_listed_values.csv"
        ),
        gold_standard_file=DIR_WITH_OUTPUT_GOLD_STANDARD_INVENTORIES
        / "features_listed_values.csv",
        unlink_if_successful=True,
    )


@pytest.mark.parametrize(
    "input_file",
    [
        DIR_WITH_INPUT_FEATURE_PROFILES / "corsican.csv",
        DIR_WITH_INPUT_FEATURE_PROFILES / "pashto.csv",
        DIR_WITH_INPUT_FEATURE_PROFILES / "susu.csv",
    ]
)
def test_update_one_feature_profile(
        input_file: Path
):
    value_renamer = ValueRenamer(
        input_feature_profiles_dir=DIR_WITH_INPUT_FEATURE_PROFILES,
        output_feature_profiles_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES,
        input_inventories_dir=DIR_WITH_INPUT_INVENTORIES,
        output_inventories_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "inventories",
    )
    value_renamer._update_one_feature_profile(
        id_of_value_to_rename="A-9-2",
        new_value_name="Представлены исключительно дифтонги",
        input_file=input_file,
        output_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES,
    )
    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / input_file.name,
        gold_standard_file=DIR_WITH_OUTPUT_GOLD_STANDARD_FEATURE_PROFILES / input_file.name,
        unlink_if_successful=True,
    )


def test_update_features_listed_values():
    value_renamer = ValueRenamer(
        input_feature_profiles_dir=DIR_WITH_INPUT_FEATURE_PROFILES,
        output_feature_profiles_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES,
        input_inventories_dir=DIR_WITH_INPUT_INVENTORIES,
        output_inventories_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "inventories",
    )
    value_renamer._update_features_listed_values(
        id_of_value_to_rename="A-9-2",
        new_value_name="Представлены исключительно дифтонги",
        input_file=DIR_WITH_INPUT_INVENTORIES / "features_listed_values.csv",
        output_file=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES
        / "inventories"
        / "features_listed_values.csv",
    )
    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=(
            DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES
            / "inventories"
            / "features_listed_values.csv"
        ),
        gold_standard_file=DIR_WITH_OUTPUT_GOLD_STANDARD_INVENTORIES
        / "features_listed_values.csv",
        unlink_if_successful=True,
    )
