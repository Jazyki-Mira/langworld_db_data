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


GS_FILE_FOR_MOVING_FROM_FIRST_TO_MIDDLE = (DIR_WITH_MOVERS_TEST_FILES /
    "features_listed_values_gold_standard_from_first_to_middle.csv")

GS_FILE_FOR_MOVING_FROM_FIRST_TO_LAST = (DIR_WITH_MOVERS_TEST_FILES /
    "features_listed_values_gold_standard_from_first_to_last.csv")

GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_FIRST = (DIR_WITH_MOVERS_TEST_FILES /
    "features_listed_values_gold_standard_from_middle_to_first.csv")

GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_DIFFERENT_MIDDLE_UP = (DIR_WITH_MOVERS_TEST_FILES /
    "features_listed_values_gold_standard_from_middle_to_different_middle_up.csv")

GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_DIFFERENT_MIDDLE_DOWN = (DIR_WITH_MOVERS_TEST_FILES /
    "features_listed_values_gold_standard_from_middle_to_different_middle_down.csv")

GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_LAST = (DIR_WITH_MOVERS_TEST_FILES /
    "features_listed_values_gold_standard_from_middle_to_last.csv")

GS_FILE_FOR_MOVING_FROM_LAST_TO_FIRST = (DIR_WITH_MOVERS_TEST_FILES /
    "features_listed_values_gold_standard_from_last_to_first.csv")

GS_FILE_FOR_MOVING_FROM_LAST_TO_MIDDLE = (DIR_WITH_MOVERS_TEST_FILES /
    "features_listed_values_gold_standard_from_last_to_middle.csv")


@pytest.fixture(scope="function")
def test_mover():
    return ListedValueMover(
        input_file_with_listed_values=INPUT_FILE_WITH_LISTED_VALUES_FOR_MOVERS,
        output_file_with_listed_values=DIR_WITH_MOVERS_TEST_FILES
        / "features_listed_values_output_value_remover.csv",
        input_dir_with_feature_profiles=DIR_WITH_MOVERS_FEATURE_PROFILES,
        output_dir_with_feature_profiles=OUTPUT_DIR_FOR_LISTED_VALUE_MOVER_FEATURE_PROFILES,
    )

# move from A-3-4 o A-3-2
def test_move_listed_value(test_mover):

    stems_of_files_that_must_be_changed = [
        "catalan",
        "franco_provencal",
        "pashto",
    ]

    stems_of_files_that_must_not_be_changed = [
        "corsican",
        "ukrainian",
    ]

    test_mover.move_listed_value(
        initial_value_id="A-3-4",
        final_value_id="A-3-2",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_mover.output_file_with_listed_values,
        gold_standard_file=GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_DIFFERENT_MIDDLE_UP,
    )

    for stem in stems_of_files_that_must_be_changed:
        assert (test_mover.output_dir_with_feature_profiles / f"{stem}.csv").exists(), (
            f"File {stem}.csv was not created. It means that no changes were made while"
            " there should have been changes"
        )

    for file in test_mover.output_dir_with_feature_profiles.glob("*.csv"):
        assert (
            file.stem not in stems_of_files_that_must_not_be_changed
        ), f"File {file.name} is not supposed to be changed"

        print(f"TEST: checking amended feature profile {file.name}")

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=file,
            gold_standard_file=GS_DIR_WITH_MOVERS_FEATURE_PROFILES / file.name,
        )


def test__move_value_in_inventory_of_listed_values(
    test_mover,
):
    for args in (
        {
            "initial_value_id": "A-3-1",
            "final_value_id": "A-3-3",
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_FIRST_TO_MIDDLE,
            },
            {
            "initial_value_id": "A-3-1",
            "final_value_id": "A-3-5",
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_FIRST_TO_LAST,
            },
            {
            "initial_value_id": "A-3-3",
            "final_value_id": "A-3-1",
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_FIRST,
            },
            {
            "initial_value_id": "A-3-2",
            "final_value_id": "A-3-4",
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_DIFFERENT_MIDDLE_DOWN,
            },
            {
            "initial_value_id": "A-3-2",
            "final_value_id": "A-3-5",
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_MIDDLE_TO_LAST,
            },
            {
            "initial_value_id": "A-3-5",
            "final_value_id": "A-3-1",
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_LAST_TO_FIRST,
            },
            {
            "initial_value_id": "A-3-5",
            "final_value_id": "A-3-2",
            "gold_standard_file": GS_FILE_FOR_MOVING_FROM_LAST_TO_MIDDLE,
            },
    ):
        test_mover.move_listed_value(
            initial_value_id=args["initial_value_id"],
            final_value_id=args["final_value_id"],
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
            final_value_id="A-3-2",
        )
