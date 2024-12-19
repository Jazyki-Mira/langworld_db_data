import pytest

from langworld_db_data.movers.listed_value_mover import ListedValueMover, ListedValueMoverError
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import (
    DIR_WITH_MOVERS_FEATURE_PROFILES,
    DIR_WITH_MOVERS_TEST_FILES,
    INPUT_FILE_WITH_LISTED_VALUES_FOR_MOVERS,
    OUTPUT_DIR_FOR_LISTED_VALUE_MOVER_FEATURE_PROFILES,
)

GS_DIR_WITH_MOVERS_FEATURE_PROFILES = DIR_WITH_MOVERS_FEATURE_PROFILES / "gold_standard"


@pytest.fixture(scope="function")
def test_mover():
    return ListedValueMover(
        input_file_with_listed_values=INPUT_FILE_WITH_LISTED_VALUES_FOR_MOVERS,
        output_file_with_listed_values=DIR_WITH_MOVERS_TEST_FILES
        / "features_listed_values_output_value_remover.csv",
        input_dir_with_feature_profiles=DIR_WITH_MOVERS_FEATURE_PROFILES,
        output_dir_with_feature_profiles=OUTPUT_DIR_FOR_LISTED_VALUE_MOVER_FEATURE_PROFILES,
    )


def test_move_listed_value(test_mover):
    pass


def test__move_value_in_inventory_of_listed_values(test_mover):
    pass


def test_move_value_in_inventory_of_listed_values_throws_error_with_coinciding_from_and_to(
    test_mover,
):
    pass
