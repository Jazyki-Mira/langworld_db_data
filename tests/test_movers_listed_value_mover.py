import pytest

from langworld_db_data.movers.listed_value_mover import ListedValueMover, ListedValueMoverError
from langworld_db_data.adders.listed_value_adder import ListedValueAdder
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import (
    DIR_WITH_MOVERS_FEATURE_PROFILES,
    DIR_WITH_MOVERS_TEST_FILES,
    INPUT_FILE_WITH_LISTED_VALUES_FOR_MOVERS,
    OUTPUT_DIR_FOR_LISTED_VALUE_MOVER_FEATURE_PROFILES,
)

OUTPUT_FILE_WITH_LISTED_VALUES = DIR_WITH_MOVERS_TEST_FILES / "features_listed_values_output_value_remover.csv"

GS_DIR_WITH_MOVERS_FEATURE_PROFILES = DIR_WITH_MOVERS_FEATURE_PROFILES / "gold_standard"


GS_FILE_FOR_MOVING_FROM_FIRST_TO_MIDDLE = (
    DIR_WITH_MOVERS_TEST_FILES / "features_listed_values_gold_standard_from_first_to_middle.csv"
)

GS_FILE_FOR_MOVING_FROM_FIRST_TO_LAST = (
    DIR_WITH_MOVERS_TEST_FILES / "features_listed_values_gold_standard_from_first_to_last.csv"
)

GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_FIRST = (
    DIR_WITH_MOVERS_TEST_FILES / "features_listed_values_gold_standard_from_middle_to_first.csv"
)

GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_DIFFERENT_MIDDLE_UP = (
    DIR_WITH_MOVERS_TEST_FILES
    / "features_listed_values_gold_standard_from_middle_to_different_middle_up.csv"
)

GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_DIFFERENT_MIDDLE_DOWN = (
    DIR_WITH_MOVERS_TEST_FILES
    / "features_listed_values_gold_standard_from_middle_to_different_middle_down.csv"
)

GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_LAST = (
    DIR_WITH_MOVERS_TEST_FILES / "features_listed_values_gold_standard_from_middle_to_last.csv"
)

GS_FILE_FOR_MOVING_FROM_LAST_TO_FIRST = (
    DIR_WITH_MOVERS_TEST_FILES / "features_listed_values_gold_standard_from_last_to_first.csv"
)

GS_FILE_FOR_MOVING_FROM_LAST_TO_MIDDLE = (
    DIR_WITH_MOVERS_TEST_FILES / "features_listed_values_gold_standard_from_last_to_middle.csv"
)


@pytest.fixture(scope="function")
def test_mover():
    for filepath in sorted(list(DIR_WITH_MOVERS_FEATURE_PROFILES.glob("*.csv"))):
        path_to_write_into = OUTPUT_DIR_FOR_LISTED_VALUE_MOVER_FEATURE_PROFILES / filepath.name
        path_to_write_into.write_text(filepath.read_text())
    return ListedValueMover(
        input_file_with_listed_values=INPUT_FILE_WITH_LISTED_VALUES_FOR_MOVERS,
        output_file_with_listed_values=OUTPUT_FILE_WITH_LISTED_VALUES,
        input_dir_with_feature_profiles=DIR_WITH_MOVERS_FEATURE_PROFILES,
        output_dir_with_feature_profiles=OUTPUT_DIR_FOR_LISTED_VALUE_MOVER_FEATURE_PROFILES,
        listed_value_adder_input_file_with_inventories=OUTPUT_FILE_WITH_LISTED_VALUES,
        listed_value_adder_input_dir_with_feature_profiles=OUTPUT_DIR_FOR_LISTED_VALUE_MOVER_FEATURE_PROFILES,
    )


# move from A-3-4 to A-3-2 and update profiles
def test_move_listed_value_full_process(test_mover):

    test_mover.move_listed_value(
        initial_value_id="A-3-4",
        index_to_assign=2,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_mover.output_file_with_listed_values,
        gold_standard_file=GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_DIFFERENT_MIDDLE_UP,
    )

    for file in test_mover.output_dir_with_feature_profiles.glob("*.csv"):
        print(f"TEST: feature profile {file.name}")
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=file,
            gold_standard_file=GS_DIR_WITH_MOVERS_FEATURE_PROFILES / file.name,
        )


# different moving scenarios without profiles check
def test_move_listed_value_inventories_only(
    test_mover,
):
    for args in (
        {
            "initial_value_id": "A-3-1",
            "index_to_assign": 3,
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_FIRST_TO_MIDDLE,
        },
        {
            "initial_value_id": "A-3-1",
            "index_to_assign": 5,
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_FIRST_TO_LAST,
        },
        {
            "initial_value_id": "A-3-3",
            "index_to_assign": 1,
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_FIRST,
        },
        {
            "initial_value_id": "A-3-2",
            "index_to_assign": 4,
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_DIFFERENT_MIDDLE_DOWN,
        },
        {
            "initial_value_id": "A-3-2",
            "index_to_assign": 5,
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_LAST,
        },
        {
            "initial_value_id": "A-3-5",
            "index_to_assign": 1,
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_LAST_TO_FIRST,
        },
        {
            "initial_value_id": "A-3-5",
            "index_to_assign": 2,
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_LAST_TO_MIDDLE,
        },
    ):
        test_mover.move_listed_value(
            initial_value_id=args["initial_value_id"],
            index_to_assign=args["index_to_assign"],
        )

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_mover.output_file_with_listed_values,
            gold_standard_file=args["gold_standard_file"],
        )


def test_move_value_in_inventory_of_listed_values_throws_error_with_coinciding_from_and_to(
    test_mover,
):
    with pytest.raises(ListedValueMoverError, match="must not coincide"):
        test_mover.move_listed_value(
            initial_value_id="A-3-2",
            index_to_assign=2,
        )
