import pytest

from langworld_db_data.tools.common.adder import AdderError
from langworld_db_data.tools.listed_values.listed_value_adder import (
    ListedValueAdder,
)
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import (
    DIR_WITH_ADDERS_FEATURE_PROFILES,
    DIR_WITH_ADDERS_TEST_FILES,
)

DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES = DIR_WITH_ADDERS_TEST_FILES / "listed_value_adder"
DIR_WITH_GOLD_STANDARD_LISTED_VALUES_INVENTORIES_FOR_VARIOUS_TESTS = (
    DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES / "gold_standard_inventories"
)
DIR_WITH_GOLD_STANDARD_FEATURE_PROFILES = (
    DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES / "gold_standard_feature_profiles"
)

DIR_WITH_OUTPUT_FILES = DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES / "output_files"

INPUT_DIR_WITH_FEATURE_PROFILES = DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES / "input_feature_profiles"
INPUT_FILE_WITH_LISTED_VALUES = (
    DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES / "input_inventories" / "features_listed_values.csv"
)


CUSTOM_VALUES_TO_RENAME = [
    "Одно кастомное значение",
    "Еще одно кастомное значение",
    "Особое употребление относительных местоимений и опущение предлогов перед союзами, вводящими придаточное дополнительное",
]


@pytest.fixture(scope="function")
def test_adder():
    return ListedValueAdder(
        input_file_with_listed_values=INPUT_FILE_WITH_LISTED_VALUES,
        output_file_with_listed_values=DIR_WITH_OUTPUT_FILES / "features_listed_values.csv",
        input_dir_with_feature_profiles=INPUT_DIR_WITH_FEATURE_PROFILES,
        output_dir_with_feature_profiles=DIR_WITH_OUTPUT_FILES,
    )


# add_listed_value
def test_add_listed_value_append_to_end_with_custom_values(test_adder):

    # STEMS_OF_EXPECTED_OUTPUT_FILES = ("catalan", "corsican", "franco_provencal")
    # STEMS_OF_FILES_THAT_MUST_NOT_BE_CHANGED = ("pashto", "ukrainian")

    GS_DIR = (
        DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_add_listed_value_append_to_end_with_custom_values"
    )

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
        gold_standard_file=GS_DIR / "features_listed_values.csv",
    )

    # for stem in STEMS_OF_EXPECTED_OUTPUT_FILES:
    #     assert (DIR_WITH_OUTPUT_FILES / f"{stem}.csv").exists(), (
    #         f"File {stem}.csv was not created. It means that no changes were made while"
    #         " there should have been changes"
    #     )

    for file in test_adder.output_dir_with_feature_profiles.glob("*.csv"):
        # assert (
        #     file.stem not in STEMS_OF_FILES_THAT_MUST_NOT_BE_CHANGED
        # ), f"File {file.name} is not supposed to be changed"

        print(f"TEST: checking amended feature profile {file.name}")
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=file,
            gold_standard_file=GS_DIR / file.name,
        )


def test_add_listed_value_append_to_end_with_custom_values_and_updating_value_ids(test_adder):

    GS_DIR = (
        DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_add_listed_value_append_to_end_with_custom_values_and_updating_value_ids"
    )

    test_adder.add_listed_value(
        feature_id="A-2",
        new_value_en="Four degrees",
        new_value_ru="Четыре подъема",
        custom_values_to_rename=[
            "Верхний, средний (закрытые и открытые) и нижний",
        ],
        index_to_assign=3,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=GS_DIR / "features_listed_values.csv",
    )

    for file in test_adder.output_dir_with_feature_profiles.glob("*.csv"):
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=file,
            gold_standard_file=GS_DIR / file.name,
        )


def test_add_listed_value_add_value_homonymous_to_value_in_feature_after_the_current_one(
    test_adder,
):
    test_adder.add_listed_value(
        feature_id="A-1",
        new_value_en="Present for central vowels",
        new_value_ru="В среднем ряду",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_flv_add_listed_value_add_value_homonymous_to_value_in_feature_after_the_current_one.csv",
    )


def test_add_listed_value_add_value_homonymous_to_value_in_feature_before_the_current_one(
    test_adder,
):
    test_adder.add_listed_value(
        feature_id="A-6",
        new_value_en="Present for central vowels",
        new_value_ru="В среднем ряду",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_flv_add_listed_value_add_value_homonymous_to_value_in_feature_before_the_current_one.csv",
    )


def test_add_listed_value_throws_exception_add_value_homonymous_to_value_in_the_same_feature(
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
        with pytest.raises(AdderError, match="English or Russian value name is already present"):
            test_adder.add_listed_value(**bad_args)


def test_add_listed_value_throws_exception_with_empty_args(test_adder):
    for bad_set_of_values in (
        {"feature_id": "", "new_value_en": "Value", "new_value_ru": "Значение"},
        {"feature_id": "A-1", "new_value_en": "", "new_value_ru": "Значение"},
        {"feature_id": "A-1", "new_value_en": "Value", "new_value_ru": ""},
    ):
        with pytest.raises(AdderError, match="None of the following arguments"):
            test_adder.add_listed_value(**bad_set_of_values)


def test_add_listed_value_throws_exception_with_invalid_feature_id(
    test_adder,
):
    with pytest.raises(AdderError, match="Feature ID X-1 not found"):
        test_adder.add_listed_value("X-1", "Value", "значение")


def test_add_listed_value_throws_exception_with_invalid_index_to_assign(test_adder):
    invalid_indices_to_assign = [-1, 0, 5, 100]
    for invalid_index in invalid_indices_to_assign:
        with pytest.raises(ValueError, match="It is either less than 1 or greater"):
            test_adder.add_listed_value(
                feature_id="A-1",
                new_value_en="Value",
                new_value_ru="значение",
                index_to_assign=invalid_index,
            )


def test__add_to_inventory_of_listed_values_append_to_end_no_custom_values(test_adder):
    test_adder._add_listed_value_to_inventory_of_listed_values(
        value_id="A-11-15",
        feature_id="A-11",
        new_value_en="New value, listed with a comma",
        new_value_ru="Есть первые, вторые и третьи",
    )
    print(test_adder.output_file_with_listed_values)

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_flv__add_to_inventory_of_listed_values_append_to_end_no_custom_values.csv",
    )


def test__add_to_inventory_of_listed_values_insert_after_non_final_value_put_as_third(test_adder):
    test_adder._add_listed_value_to_inventory_of_listed_values(
        value_id="A-3-3",
        feature_id="A-3",
        new_value_en="Central, mid-back and back",
        new_value_ru="Средний, задне-средний и задний",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_flv__add_to_inventory_of_listed_values_insert_after_non_final_value_put_as_third.csv",
    )


def test__add_to_inventory_of_listed_values_insert_after_non_final_value_put_as_tenth(test_adder):
    test_adder._add_listed_value_to_inventory_of_listed_values(
        value_id="A-11-10",
        feature_id="A-11",
        new_value_en="Some value",
        new_value_ru="Какое-то значение",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_flv__add_to_inventory_of_listed_values_insert_after_non_final_value_put_as_tenth.csv",
    )


def test__add_to_inventory_of_listed_values_put_as_first(test_adder):
    test_adder._add_listed_value_to_inventory_of_listed_values(
        value_id="A-3-1",
        feature_id="A-3",
        new_value_en="Central, mid-back and back",
        new_value_ru="Средний, задне-средний и задний",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_flv__add_to_inventory_of_listed_values_put_as_first.csv",
    )


def test__add_to_inventory_of_listed_values_append_to_end_with_explicit_index_no_custom_values(
    test_adder,
):
    # The feature has 14 values, we are asking the method to add the 15-th one
    test_adder._add_listed_value_to_inventory_of_listed_values(
        value_id="A-11-15",
        feature_id="A-11",
        new_value_en="New value, listed with a comma",
        new_value_ru="Есть первые, вторые и третьи",
    )

    assert test_adder.output_file_with_listed_values.exists()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_flv__add_to_inventory_of_listed_values_append_to_end_with_explicit_index_no_custom_values.csv",
    )


def test__find_line_number_of_feature_in_feature_profile(test_adder):

    assert (
        test_adder._find_line_number_of_feature_in_feature_profile(
            feature_profile=DIR_WITH_ADDERS_FEATURE_PROFILES / "catalan.csv",
            feature_id="A-8",
        )
        == 7
    )


def test__increment_value_id_in_line_number_to_check_if_necessary(test_adder):

    input_row = {
        "feature_id": "A-3",
        "feature_name_ru": "Некий признак",
        "value_type": "listed",
        "value_id": "A-3-8",
        "value_ru": "Некое значение",
        "comment_ru": "",
        "comment_en": "",
    }

    GOLD_STANDARD_ROW = {
        "feature_id": "A-3",
        "feature_name_ru": "Некий признак",
        "value_type": "listed",
        "value_id": "A-3-9",
        "value_ru": "Некое значение",
        "comment_ru": "",
        "comment_en": "",
    }

    assert (
        test_adder._increment_value_id_in_line_number_to_check_if_necessary(
            row=input_row,
            value_id="A-3-3",
        )
        == GOLD_STANDARD_ROW
    )


def test__increment_value_id_in_line_number_to_check_if_necessary_does_nothing(test_adder):

    input_row = {
        "feature_id": "A-3",
        "feature_name_ru": "Некий признак",
        "value_type": "listed",
        "value_id": "A-3-8",
        "value_ru": "Некое значение",
        "comment_ru": "",
        "comment_en": "",
    }

    GOLD_STANDARD_ROW = {
        "feature_id": "A-3",
        "feature_name_ru": "Некий признак",
        "value_type": "listed",
        "value_id": "A-3-8",
        "value_ru": "Некое значение",
        "comment_ru": "",
        "comment_en": "",
    }

    assert (
        test_adder._increment_value_id_in_line_number_to_check_if_necessary(
            row=input_row,
            value_id="A-3-11",
        )
        == GOLD_STANDARD_ROW
    )


def test__mark_value_type_as_listed_and_rename_it_if_necessary(test_adder):

    input_row = {
        "feature_id": "A-3",
        "feature_name_ru": "Некий признак",
        "value_type": "custom",
        "value_id": "",
        "value_ru": "Подозрительно пусто",
        "comment_ru": "",
        "comment_en": "",
    }

    GOLD_STANDARD_ROW = {
        "feature_id": "A-3",
        "feature_name_ru": "Некий признак",
        "value_type": "listed",
        "value_id": "A-3-8",
        "value_ru": "Некое значение",
        "comment_ru": "",
        "comment_en": "",
    }

    assert (
        test_adder._mark_value_type_as_listed_and_rename_it_if_necessary(
            row=input_row,
            new_value_ru="Некое значение",
            value_id="A-3-8",
            custom_values_to_rename=[
                "Подозрительно пусто",
                "Очень подозрительно пусто",
            ],
        )
        == GOLD_STANDARD_ROW
    )


def test__mark_value_type_as_listed_and_rename_it_if_necessary_does_nothing(test_adder):

    input_row = {
        "feature_id": "A-3",
        "feature_name_ru": "Некий признак",
        "value_type": "custom",
        "value_id": "",
        "value_ru": "Просто пусто",
        "comment_ru": "",
        "comment_en": "",
    }

    GOLD_STANDARD_ROW = {
        "feature_id": "A-3",
        "feature_name_ru": "Некий признак",
        "value_type": "custom",
        "value_id": "",
        "value_ru": "Просто пусто",
        "comment_ru": "",
        "comment_en": "",
    }

    assert (
        test_adder._mark_value_type_as_listed_and_rename_it_if_necessary(
            row=input_row,
            new_value_ru="Некое значение",
            value_id="A-3-8",
            custom_values_to_rename=[
                "Подозрительно пусто",
                "Очень подозрительно пусто",
            ],
        )
        == GOLD_STANDARD_ROW
    )


def test__update_value_id_and_type_in_one_feature_profile_if_necessary_updates_value_type(
    test_adder,
):

    test_adder._update_value_id_and_type_in_one_feature_profile_if_necessary(
        feature_profile=test_adder.input_dir_with_feature_profiles / "catalan.csv",
        line_number_of_row_to_check=24,
        value_id="N-2-4",
        value_ru="Непустое значение",
        custom_values_to_rename=CUSTOM_VALUES_TO_RENAME,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=DIR_WITH_OUTPUT_FILES / "catalan.csv",
        gold_standard_file=DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_catalan__update_value_id_and_type_in_one_feature_profile_if_necessary_updates_value_type.csv",
    )


def test__update_value_id_and_type_in_one_feature_profile_if_necessary_updates_value_id(
    test_adder,
):

    test_adder._update_value_id_and_type_in_one_feature_profile_if_necessary(
        feature_profile=test_adder.input_dir_with_feature_profiles / "catalan.csv",
        line_number_of_row_to_check=12,
        value_id="A-13-1",
        value_ru="Непустое значение",
        custom_values_to_rename=CUSTOM_VALUES_TO_RENAME,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=DIR_WITH_OUTPUT_FILES / "catalan.csv",
        gold_standard_file=DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs_catalan__update_value_id_and_type_in_one_feature_profile_if_necessary_updates_value_id.csv",
    )


def test__update_value_ids_and_types_in_feature_profiles_if_necessary(test_adder):

    CUSTOM_VALUES_TO_RENAME_IN_A_2 = [
        "Верхний, средний (закрытые и открытые) и нижний",
        "And one moooooore thing",
    ]

    GS_DIR = (
        DIR_WITH_LISTED_VALUE_ADDER_TEST_FILES
        / "gs__update_value_ids_and_types_in_feature_profiles_if_necessary"
    )

    test_adder._update_value_ids_and_types_in_feature_profiles_if_necessary(
        feature_id="A-2",
        value_id="A-2-5",
        value_ru="Определенное значение",
        custom_values_to_rename=CUSTOM_VALUES_TO_RENAME_IN_A_2,
    )

    for file in test_adder.output_dir_with_feature_profiles.glob("*.csv"):

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=file,
            gold_standard_file=GS_DIR / file.name,
        )


def test__generate_variants_of_russian_value_name(test_adder):

    VALUE_NAMES = [
        "Есть первые, вторые и третьи.",
        "Есть первые, вторые и третьи",
        "есть первые, вторые и третьи.",
        "есть первые, вторые и третьи",
    ]
    GS_VARIANTS = set(
        [
            "Есть первые, вторые и третьи.",
            "Есть первые, вторые и третьи",
            "есть первые, вторые и третьи.",
            "есть первые, вторые и третьи",
        ]
    )
    for value_name in VALUE_NAMES:
        assert test_adder._generate_variants_of_russian_value_name(value_name) == GS_VARIANTS


# def test__mark_value_as_listed_in_feature_profiles(test_adder):
#     test_adder._mark_value_as_listed_in_feature_profiles(
#         feature_id="A-11",
#         new_value_id="A-11-15",
#         new_value_ru="Есть первые, вторые и третьи",
#         custom_values_to_rename=[
#             "первые, вторые и третьи",  # it is also lowercase in feature profile
#             "третьи, вторые и первые",  # first word is capitalized in feature profile
#             "Первые, третьи и вторые",
#         ],
#     )

#     for stem in STEMS_OF_EXPECTED_OUTPUT_FILES:
#         assert (OUTPUT_DIR_FOR_LISTED_VALUE_ADDER_FEATURE_PROFILES / f"{stem}.csv").exists(), (
#             f"File {stem}.csv was not created. It means that no changes were made while"
#             " there should have been changes"
#         )

#     for file in OUTPUT_DIR_FOR_LISTED_VALUE_ADDER_FEATURE_PROFILES.glob("*.csv"):
#         assert (
#             file.stem not in STEMS_OF_FILES_THAT_MUST_NOT_BE_CHANGED
#         ), f"File {file.name} is not supposed to be changed"

#         print(f"TEST: checking amended feature profile {file.name}")

#         check_existence_of_output_csv_file_and_compare_with_gold_standard(
#             output_file=file,
#             gold_standard_file=GS_DIR_WITH_FEATURE_PROFILES_AFTER_ADDITION_WITH_CUSTOM_VALUES
#             / file.name,
#         )


# _get_indices_and_their_line_numbers_for_given_feature_in_inventory_of_listed_values
# Normal case
# def test__get_indices_and_their_line_numbers_for_given_feature_in_inventory_of_listed_values(
#     test_adder,
# ):
#     rows = [
#         {"id": "A-1-1", "feature_id": "A-1", "en": "Two", "ru": "Две"},
#         {"id": "A-2-1", "feature_id": "A-2", "en": "Close and open", "ru": "Верхний и нижний"},
#         {"id": "A-2-2", "feature_id": "A-2", "en": "Close and mid", "ru": "Верхний и средний"},
#     ]
#     value_indices_to_inventory_line_numbers = test_adder._get_indices_and_their_line_numbers_for_given_feature_in_inventory_of_listed_values(
#         rows=rows,
#         feature_id="A-2",
#     )

#     assert value_indices_to_inventory_line_numbers == (
#         {
#             "index": 1,
#             "line number": 1,
#         },
#         {
#             "index": 2,
#             "line number": 2,
#         },
#     )


# # _increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign
# # Normal case
# def test__increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(test_adder):
#     rows = [
#         {"id": "A-1-1", "feature_id": "A-1", "en": "Two", "ru": "Две"},
#         {"id": "A-2-1", "feature_id": "A-2", "en": "Close and open", "ru": "Верхний и нижний"},
#         {"id": "A-2-2", "feature_id": "A-2", "en": "Close and mid", "ru": "Верхний и средний"},
#         {
#             "id": "A-2-3",
#             "feature_id": "A-2",
#             "en": "Close, mid and open",
#             "ru": "Верхний, средний и нижний",
#         },
#     ]
#     value_indices_to_inventory_line_numbers = (
#         {"index": 1, "line number": 1},
#         {"index": 2, "line number": 2},
#         {"index": 3, "line number": 3},
#     )
#     rows = test_adder._increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(
#         rows=rows,
#         value_indices_to_inventory_line_numbers=value_indices_to_inventory_line_numbers,
#         index_to_assign=2,
#     )

#     gold_standard_rows = tuple(
#         [
#             {"id": "A-1-1", "feature_id": "A-1", "en": "Two", "ru": "Две"},
#             {"id": "A-2-1", "feature_id": "A-2", "en": "Close and open", "ru": "Верхний и нижний"},
#             {"id": "A-2-3", "feature_id": "A-2", "en": "Close and mid", "ru": "Верхний и средний"},
#             {
#                 "id": "A-2-4",
#                 "feature_id": "A-2",
#                 "en": "Close, mid and open",
#                 "ru": "Верхний, средний и нижний",
#             },
#         ]
#     )

#     assert rows == gold_standard_rows


# def test__increment_value_ids_in_feature_profiles(test_adder):

#     stems_of_files_that_must_be_changed = [
#         "catalan_A-11-5",
#         "catalan_A-11-6",
#         "catalan_A-11-14",
#     ]

#     stems_of_files_that_must_not_be_changed = [
#         "catalan_A-11-1",
#         "catalan_A-11-2",
#         "catalan_custom",
#         "catalan_not_stated",
#     ]

#     output_dir = DIR_WITH_PROFILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES / "output"
#     if not output_dir.exists():
#         output_dir.mkdir()
#     input_feature_profiles = sorted(
#         list(DIR_WITH_INPUT_FILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES.glob("*.csv"))
#     )
#     test_adder._increment_value_ids_in_feature_profiles(
#         new_value_id="A-11-5",
#         input_files=input_feature_profiles,
#         output_dir=output_dir,
#     )

#     for stem in stems_of_files_that_must_be_changed:
#         assert (output_dir / f"{stem}.csv").exists(), (
#             f"File {stem}.csv was not created. It means that no changes were made while"
#             " there should have been changes"
#         )

#     for file in output_dir.glob("*.csv"):
#         assert (
#             file.stem not in stems_of_files_that_must_not_be_changed
#         ), f"File {file.name} is not supposed to be changed"

#         print(f"TEST: checking amended feature profile {file.name}")

#         check_existence_of_output_csv_file_and_compare_with_gold_standard(
#             output_file=file,
#             gold_standard_file=DIR_WITH_GS_FILES_FOR_INCREMENT_VALUE_IDS_IN_FEATURE_PROFILES
#             / file.name,
#         )
