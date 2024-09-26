import pytest

from langworld_db_data.adders.listed_value_adder import ListedValueAdder, ListedValueAdderError
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import (
    DIR_WITH_ADDERS_FEATURE_PROFILES,
    DIR_WITH_ADDERS_TEST_FILES,
    INPUT_FILE_WITH_LISTED_VALUES,
    OUTPUT_DIR_FOR_LISTED_VALUE_ADDER_FEATURE_PROFILES,
)

GS_FILE_WITH_LISTED_VALUES_ADDITION_TO_THE_END_OF_VALUE = (
    DIR_WITH_ADDERS_TEST_FILES / "features_listed_values_gold_standard_for_listed_value_adder.csv"
)
GS_FILE_WITH_LISTED_VALUES_INSERTION_AS_THIRD = (
    DIR_WITH_ADDERS_TEST_FILES / "features_listed_values_gold_standard_for_insertion_as_third.csv"
)
GS_FILE_WITH_LISTED_VALUES_INSERTION_AS_TENTH = (
    DIR_WITH_ADDERS_TEST_FILES / "features_listed_values_gold_standard_for_insertion_as_tenth.csv"
)
GS_FILE_WITH_LISTED_VALUES_INSERTION_AS_FIRST = (
    DIR_WITH_ADDERS_TEST_FILES / "features_listed_values_gold_standard_for_insertion_as_first.csv"
)
GS_DIR_WITH_FEATURE_PROFILES_AFTER_ADDITION = (
    OUTPUT_DIR_FOR_LISTED_VALUE_ADDER_FEATURE_PROFILES / "gold_standard"
)
DIR_WITH_FEATURE_PROFILES = DIR_WITH_ADDERS_TEST_FILES / "feature_profiles"
DIR_WITH_PROFILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES = (
    DIR_WITH_FEATURE_PROFILES / "increment_value_ids_in_feature_profiles"
)
DIR_WITH_INPUT_FILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES = (
    DIR_WITH_PROFILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES / "input"
)
DIR_WITH_GS_FILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES = (
    DIR_WITH_PROFILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES / "gold_standard"
)

STEMS_OF_EXPECTED_OUTPUT_FILES = ("catalan", "corsican", "franco_provencal")
STEMS_OF_FILES_THAT_MUST_NOT_BE_CHANGED = ("pashto", "ukrainian")


@pytest.fixture(scope="function")
def test_adder():
    return ListedValueAdder(
        input_file_with_listed_values=INPUT_FILE_WITH_LISTED_VALUES,
        output_file_with_listed_values=DIR_WITH_ADDERS_TEST_FILES
        / "features_listed_values_output_value_adder.csv",
        input_dir_with_feature_profiles=DIR_WITH_ADDERS_FEATURE_PROFILES,
        output_dir_with_feature_profiles=OUTPUT_DIR_FOR_LISTED_VALUE_ADDER_FEATURE_PROFILES,
    )


# add_listed_value
# Normal case
def test_add_listed_value_append_to_end_with_custom_values(test_adder):
    test_adder.add_listed_value(
        feature_id="A-11",
        new_value_en="New value, listed with a comma",
        new_value_ru="Есть первые, вторые и третьи",
        custom_values_to_rename=[
            "первые, вторые и третьи",
            "третьи, вторые и первые",
            "Первые, третьи и вторые",
        ],
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=GS_FILE_WITH_LISTED_VALUES_ADDITION_TO_THE_END_OF_VALUE,
    )

    for stem in STEMS_OF_EXPECTED_OUTPUT_FILES:
        assert (OUTPUT_DIR_FOR_LISTED_VALUE_ADDER_FEATURE_PROFILES / f"{stem}.csv").exists(), (
            f"File {stem}.csv was not created. It means that no changes were made while"
            " there should have been changes"
        )

    for file in OUTPUT_DIR_FOR_LISTED_VALUE_ADDER_FEATURE_PROFILES.glob("*.csv"):
        assert (
            file.stem not in STEMS_OF_FILES_THAT_MUST_NOT_BE_CHANGED
        ), f"File {file.name} is not supposed to be changed"

        print(f"TEST: checking amended feature profile {file.name}")
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=file,
            gold_standard_file=GS_DIR_WITH_FEATURE_PROFILES_AFTER_ADDITION / file.name,
        )


# Throws exceptions
def test_add_listed_value_throws_exception_with_empty_args(test_adder):
    for bad_set_of_values in (
        {"feature_id": "", "new_value_en": "Value", "new_value_ru": "Значение"},
        {"feature_id": "A-1", "new_value_en": "", "new_value_ru": "Значение"},
        {"feature_id": "A-1", "new_value_en": "Value", "new_value_ru": ""},
    ):
        with pytest.raises(ListedValueAdderError, match="None of the passed strings can be empty"):
            test_adder.add_listed_value(**bad_set_of_values)


def test_add_listed_value_throws_exception_with_invalid_feature_id(
    test_adder,
):
    with pytest.raises(ListedValueAdderError, match="Feature ID X-1 not found"):
        test_adder.add_listed_value("X-1", "Value", "значение")


def test_add_listed_value_throws_exception_with_existing_value(
    test_adder,
):
    for bad_args in (
        {
            "feature_id": "A-3",
            "new_value_en": "Central and back",
            "new_value_ru": "Средний и задний",
        },
        {
            "feature_id": "A-3",
            "new_value_en": "Some different value",
            "new_value_ru": "Средний и задний",
        },
        {
            "feature_id": "A-3",
            "new_value_en": "Central and back",
            "new_value_ru": "Что-то новое",
        },
    ):
        with pytest.raises(
            ListedValueAdderError, match="already contains value you are trying to add"
        ):
            test_adder.add_listed_value(**bad_args)


def test_add_listed_value_throws_exception_with_invalid_index_to_assign(test_adder):
    invalid_indices_to_assign = [-1, 0, 5, 100]
    for invalid_index in invalid_indices_to_assign:
        with pytest.raises(ListedValueAdderError, match="must be between 1 and 4"):
            test_adder.add_listed_value(
                feature_id="A-1",
                new_value_en="Value",
                new_value_ru="значение",
                index_to_assign=invalid_index,
            )


# _add_to_inventory_of_listed_values
# Normal cases
def test__add_to_inventory_of_listed_values_append_to_end_no_custom_values(test_adder):
    new_value_id = test_adder._add_to_inventory_of_listed_values(
        feature_id="A-11",
        new_value_en="New value, listed with a comma",
        new_value_ru="Есть первые, вторые и третьи",
        index_to_assign=None,
    )
    assert new_value_id == "A-11-15"

    assert test_adder.output_file_with_listed_values.exists()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=GS_FILE_WITH_LISTED_VALUES_ADDITION_TO_THE_END_OF_VALUE,
    )


def test__add_to_inventory_of_listed_values_insert_after_non_final_value_put_as_third(test_adder):
    new_value_id = test_adder._add_to_inventory_of_listed_values(
        feature_id="A-3",
        new_value_en="Central, mid-back and back",
        new_value_ru="Средний, задне-средний и задний",
        index_to_assign=3,
    )
    assert new_value_id == "A-3-3"

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=GS_FILE_WITH_LISTED_VALUES_INSERTION_AS_THIRD,
        unlink_if_successful=True,
    )


def test__add_to_inventory_of_listed_values_insert_after_non_final_value_put_as_tenth(test_adder):
    new_value_id = test_adder._add_to_inventory_of_listed_values(
        feature_id="A-11",
        new_value_en="Some value",
        new_value_ru="Какое-то значение",
        index_to_assign=10,
    )
    assert new_value_id == "A-11-10"

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=GS_FILE_WITH_LISTED_VALUES_INSERTION_AS_TENTH,
        unlink_if_successful=True,
    )


# Edge cases
def test__add_to_inventory_of_listed_values_put_as_first(test_adder):
    test_adder._add_to_inventory_of_listed_values(
        feature_id="A-3",
        new_value_en="Central, mid-back and back",
        new_value_ru="Средний, задне-средний и задний",
        index_to_assign=1,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=GS_FILE_WITH_LISTED_VALUES_INSERTION_AS_FIRST,
    )


def test__add_to_inventory_of_listed_values_append_to_end_with_explicit_index_no_custom_values(
    test_adder,
):
    # The feature has 14 values, we are asking the method to add the 15-th one
    new_value_id = test_adder._add_to_inventory_of_listed_values(
        feature_id="A-11",
        new_value_en="New value, listed with a comma",
        new_value_ru="Есть первые, вторые и третьи",
        index_to_assign=15,
    )
    assert new_value_id == "A-11-15"

    assert test_adder.output_file_with_listed_values.exists()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=GS_FILE_WITH_LISTED_VALUES_ADDITION_TO_THE_END_OF_VALUE,
    )


# _get_indices_and_their_line_numbers_for_given_feature_in_inventory_of_listed_values
# Normal case
def test__get_indices_and_their_line_numbers_for_given_feature_in_inventory_of_listed_values(
    test_adder,
):
    rows = [
        {"id": "A-1-1", "feature_id": "A-1", "en": "Two", "ru": "Две"},
        {"id": "A-2-1", "feature_id": "A-2", "en": "Close and open", "ru": "Верхний и нижний"},
        {"id": "A-2-2", "feature_id": "A-2", "en": "Close and mid", "ru": "Верхний и средний"},
    ]
    value_indices_to_inventory_line_numbers = test_adder._get_indices_and_their_line_numbers_for_given_feature_in_inventory_of_listed_values(
        rows=rows,
        feature_id="A-2",
    )

    assert value_indices_to_inventory_line_numbers == (
        {
            "index": 1,
            "line number": 1,
        },
        {
            "index": 2,
            "line number": 2,
        },
    )


# _increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign
# Normal case
def test__increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(test_adder):
    rows = [
        {"id": "A-1-1", "feature_id": "A-1", "en": "Two", "ru": "Две"},
        {"id": "A-2-1", "feature_id": "A-2", "en": "Close and open", "ru": "Верхний и нижний"},
        {"id": "A-2-2", "feature_id": "A-2", "en": "Close and mid", "ru": "Верхний и средний"},
        {
            "id": "A-2-3",
            "feature_id": "A-2",
            "en": "Close, mid and open",
            "ru": "Верхний, средний и нижний",
        },
    ]
    value_indices_to_inventory_line_numbers = (
        {"index": 1, "line number": 1},
        {"index": 2, "line number": 2},
        {"index": 3, "line number": 3},
    )
    rows = test_adder._increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(
        rows=rows,
        value_indices_to_inventory_line_numbers=value_indices_to_inventory_line_numbers,
        index_to_assign=2,
    )

    gold_standard_rows = tuple(
        [
            {"id": "A-1-1", "feature_id": "A-1", "en": "Two", "ru": "Две"},
            {"id": "A-2-1", "feature_id": "A-2", "en": "Close and open", "ru": "Верхний и нижний"},
            {"id": "A-2-3", "feature_id": "A-2", "en": "Close and mid", "ru": "Верхний и средний"},
            {
                "id": "A-2-4",
                "feature_id": "A-2",
                "en": "Close, mid and open",
                "ru": "Верхний, средний и нижний",
            },
        ]
    )

    assert rows == gold_standard_rows


def test__increment_value_ids_in_feature_profiles(test_adder):
    output_dir = DIR_WITH_PROFILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES / "output"
    if not output_dir.exists():
        output_dir.mkdir()
    input_feature_profiles = sorted(list(DIR_WITH_INPUT_FILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES.glob("*.csv")))
    test_adder._increment_value_ids_in_feature_profiles(
        new_value_id="A-11-5",
        input_dir=input_feature_profiles,
        output_dir=output_dir,
    )

    for gs_file in DIR_WITH_GS_FILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES.glob("*.csv"):
        test_output_file = output_dir / gs_file.name

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=gs_file,
        )


# _mark_value_as_listed_in_feature_profiles
# Normal case
def test__mark_value_as_listed_in_feature_profiles(test_adder):
    test_adder._mark_value_as_listed_in_feature_profiles(
        feature_id="A-11",
        new_value_id="A-11-15",
        new_value_ru="Есть первые, вторые и третьи",
        custom_values_to_rename=[
            "первые, вторые и третьи",  # it is also lowercase in feature profile
            "третьи, вторые и первые",  # first word is capitalized in feature profile
            "Первые, третьи и вторые",
        ],
    )

    for stem in STEMS_OF_EXPECTED_OUTPUT_FILES:
        assert (OUTPUT_DIR_FOR_LISTED_VALUE_ADDER_FEATURE_PROFILES / f"{stem}.csv").exists(), (
            f"File {stem}.csv was not created. It means that no changes were made while"
            " there should have been changes"
        )

    for file in OUTPUT_DIR_FOR_LISTED_VALUE_ADDER_FEATURE_PROFILES.glob("*.csv"):
        assert (
            file.stem not in STEMS_OF_FILES_THAT_MUST_NOT_BE_CHANGED
        ), f"File {file.name} is not supposed to be changed"

        print(f"TEST: checking amended feature profile {file.name}")

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=file,
            gold_standard_file=GS_DIR_WITH_FEATURE_PROFILES_AFTER_ADDITION / file.name,
        )
