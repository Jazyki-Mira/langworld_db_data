import pytest

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


@pytest.fixture
def create_value_renamer():
    value_renamer = ValueRenamer(
        input_feature_profiles_dir=DIR_WITH_INPUT_FEATURE_PROFILES,
        output_feature_profiles_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES,
        input_inventories_dir=DIR_WITH_INPUT_INVENTORIES,
        output_inventories_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "inventories",
    )
    return value_renamer


def test_rename_value_in_profiles_and_inventories(create_value_renamer):
    value_renamer = create_value_renamer
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


def test_update_one_feature_profile(create_value_renamer):
    value_renamer = create_value_renamer
    for filestem in ["corsican", "pashto", "susu"]:
        value_renamer._update_one_feature_profile(
            id_of_value_to_rename="A-9-2",
            new_value_name="Представлены исключительно дифтонги",
            input_file=DIR_WITH_INPUT_FEATURE_PROFILES / f"{filestem}.csv",
            output_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES,
        )
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / f"{filestem}.csv",
            gold_standard_file=DIR_WITH_OUTPUT_GOLD_STANDARD_FEATURE_PROFILES / f"{filestem}.csv",
            unlink_if_successful=True,
        )


def test_update_features_listed_values(create_value_renamer):
    value_renamer = create_value_renamer
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


def test_set_empty_name_for_value(create_value_renamer):
    value_renamer = create_value_renamer

    with pytest.raises(ValueRenamerError, match="a null string passed as new value name"):
        value_renamer.rename_value_in_profiles_and_inventories(
            id_of_value_to_rename="A-9-2",
            new_value_name="",
        )


def test_rename_value_whose_id_does_not_exist(create_value_renamer):
    value_renamer = create_value_renamer
    id_of_value_to_rename = "A-99-2"
    with pytest.raises(ValueRenamerError, match=f"{id_of_value_to_rename} does not exist"):
        value_renamer.rename_value_in_profiles_and_inventories(
            id_of_value_to_rename=id_of_value_to_rename,
            new_value_name="Представлены исключительно дифтонги",
        )


def test_current_value_name_is_equal_to_new_value_name(create_value_renamer):
    value_renamer = create_value_renamer
    new_value_name = "Только дифтонги"
    with pytest.raises(
        ValueRenamerError, match=f"'{new_value_name}' coincides with the current value name"
    ):
        value_renamer.rename_value_in_profiles_and_inventories(
            id_of_value_to_rename="A-9-2",
            new_value_name=new_value_name,
        )
