import pytest

from langworld_db_data.tools.common.adder import AdderError
from langworld_db_data.tools.features.feature_adder import FeatureAdder, FeatureAdderError
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import (
    DIR_WITH_ADDERS_TEST_FILES,
)

DUMMY_VALUES_TO_ADD = [
    {"ru": "Одно явление", "en": "One thing"},
    {"ru": "Одно, два и третье", "en": "One thing, second thing, and third thing"},
]

DIR_WITH_FEATURE_ADDER_TEST_FILES = DIR_WITH_ADDERS_TEST_FILES / "feature_adder"

DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_ADDER = DIR_WITH_FEATURE_ADDER_TEST_FILES / "inventories"

DIR_WITH_GOLD_STANDARD_FILES = DIR_WITH_FEATURE_ADDER_TEST_FILES / "gold_standard"


@pytest.fixture(scope="function")
def test_feature_adder():
    return FeatureAdder(
        file_with_categories=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_ADDER
        / "feature_categories.csv",
        input_file_with_features=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_ADDER / "features.csv",
        output_file_with_features=DIR_WITH_FEATURE_ADDER_TEST_FILES / "features.csv",
        input_file_with_listed_values=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_ADDER
        / "features_listed_values.csv",
        output_file_with_listed_values=DIR_WITH_FEATURE_ADDER_TEST_FILES
        / "features_listed_values.csv",
        input_dir_with_feature_profiles=DIR_WITH_FEATURE_ADDER_TEST_FILES / "feature_profiles",
        output_dir_with_feature_profiles=DIR_WITH_FEATURE_ADDER_TEST_FILES,
    )


def test_add_feature(test_feature_adder):
    test_feature_adder.add_feature(
        category_id="H",
        feature_en="Some feature",
        feature_ru="Некий признак",
        listed_values_to_add=DUMMY_VALUES_TO_ADD,
        index_to_assign=5,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_new_H_5.csv",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_new_H_5.csv",
    )

    gold_standard_feature_profiles = list(
        (DIR_WITH_GOLD_STANDARD_FILES / "feature_profiles_new_H_5").glob("*.csv")
    )

    for file in gold_standard_feature_profiles:
        test_output_file = test_feature_adder.output_dir_with_feature_profiles / file.name

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=file,
        )


def test_add_feature_fails_with_invalid_index_to_assign(test_feature_adder):
    with pytest.raises(ValueError, match="Invalid index to assign"):
        test_feature_adder.add_feature(
            category_id="C",
            feature_en="Some feature",
            feature_ru="Некий признак",
            listed_values_to_add=DUMMY_VALUES_TO_ADD,
            index_to_assign=418,
        )


def test_add_feature_fails_with_empty_arg(test_feature_adder):
    for incomplete_set_of_args in (
        {
            "category_id": "",
            "feature_ru": "раз",
            "feature_en": "one",
            "listed_values_to_add": DUMMY_VALUES_TO_ADD,
        },
        {
            "category_id": "A",
            "feature_ru": "",
            "feature_en": "one",
            "listed_values_to_add": DUMMY_VALUES_TO_ADD,
        },
        {
            "category_id": "A",
            "feature_ru": "раз",
            "feature_en": "",
            "listed_values_to_add": DUMMY_VALUES_TO_ADD,
        },
        {
            "category_id": "A",
            "feature_ru": "раз",
            "feature_en": "one",
            "listed_values_to_add": [],
        },
    ):
        with pytest.raises(AdderError, match="None of the following arguments"):
            test_feature_adder.add_feature(**incomplete_set_of_args)


def test_add_feature_fails_with_wrong_new_listed_values(test_feature_adder):
    args = {
        "category_id": "A",
        "feature_ru": "раз",
        "feature_en": "one",
        "listed_values_to_add": [
            {"ru": "раз", "en": "this is fine"},
            {"this": "should fail", "en": "this is fine"},
        ],
    }
    with pytest.raises(
        AdderError,
        match=("Each listed value must have keys"),
    ):
        test_feature_adder.add_feature(**args)


def test_add_feature_fails_with_wrong_category_id(test_feature_adder):
    with pytest.raises(
        AdderError,
        match=(
            "Category ID X not found in file" f" {test_feature_adder.file_with_categories.name}"
        ),
    ):
        test_feature_adder.add_feature(
            category_id="X",
            feature_ru="имя",
            feature_en="name",
            listed_values_to_add=DUMMY_VALUES_TO_ADD,
        )


def test_add_feature_fails_with_existing_feature_name(test_feature_adder):
    for en, ru in (
        ("Syllable onset", "Новый признак"),
        ("New  feature", "Начальный согласный в слоге"),
    ):
        with pytest.raises(AdderError, match="English or Russian feature name is already"):
            test_feature_adder.add_feature(
                category_id="C",
                feature_en=en,
                feature_ru=ru,
                listed_values_to_add=DUMMY_VALUES_TO_ADD,
            )


def test_add_feature_is_ok_with_feature_name_existing_in_another_category(test_feature_adder):
    for en, ru in (
        ("Syllable onset", "Новый признак"),
        ("New  feature", "Начальный согласный в слоге"),
    ):
        test_feature_adder.add_feature(
            category_id="B",
            feature_en=en,
            feature_ru=ru,
            listed_values_to_add=DUMMY_VALUES_TO_ADD,
        )


def test__add_feature_to_inventory_of_features_at_the_beginning_of_category(test_feature_adder):
    _ = test_feature_adder._add_feature_to_inventory_of_features(
        feature_id="A-1",
        category_id="A",
        new_feature_en="Some feature",
        new_feature_ru="Некий признак",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_new_A_1.csv",
    )


def test__add_feature_to_inventory_of_features_in_the_middle_of_category(test_feature_adder):
    _ = test_feature_adder._add_feature_to_inventory_of_features(
        feature_id="A-14",
        category_id="A",
        new_feature_en="Some feature",
        new_feature_ru="Некий признак",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_new_A_14.csv",
    )


def test_add_feature_throws_error_invalid_feature_id(test_feature_adder):
    for bad_feature_id in (0, -7, 418):
        with pytest.raises(
            ValueError,
            match="Invalid index to assign",
        ):
            _ = test_feature_adder.add_feature(
                category_id="C",
                feature_en="Something",
                feature_ru="Что-нибудь",
                index_to_assign=bad_feature_id,
                listed_values_to_add=DUMMY_VALUES_TO_ADD,
            )


def test__add_feature_to_inventory_of_features_at_the_end_of_category(test_feature_adder):
    test_feature_adder._add_feature_to_inventory_of_features(
        feature_id="A-22",
        category_id="A",
        new_feature_en="Some feature",
        new_feature_ru="Некий признак",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_new_A_22.csv",
    )


# def test__increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(
#     test_feature_adder,
# ):
#     rows = [
#         {"id": "A-1", "en": "Some feature", "ru": "Некий признак"},
#         {"id": "A-2", "en": "Old feature", "ru": "Старый признак"},
#         {"id": "A-3", "en": "Another feature", "ru": "Другой признак"},
#         {"id": "B-1", "en": "Yet another one", "ru": "И еще один"},
#     ]
#     feature_indices_to_inventory_line_numbers = (
#         {"index": 1, "line number": 0},
#         {"index": 2, "line number": 1},
#         {"index": 3, "line number": 2},
#     )
#     rows = (
#         test_feature_adder._increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(
#             rows=rows,
#             feature_indices_to_inventory_line_numbers=feature_indices_to_inventory_line_numbers,
#             index_to_assign=2,
#         )
#     )

#     gold_standard_rows = tuple(
#         [
#             {"id": "A-1", "en": "Some feature", "ru": "Некий признак"},
#             {"id": "A-3", "en": "Old feature", "ru": "Старый признак"},
#             {"id": "A-4", "en": "Another feature", "ru": "Другой признак"},
#             {"id": "B-1", "en": "Yet another one", "ru": "И еще один"},
#         ]
#     )

#     assert rows == gold_standard_rows


def test__add_values_of_new_feature_to_inventory_of_listed_values_at_the_beginning_of_category(
    test_feature_adder,
):
    test_feature_adder._add_values_of_new_feature_to_inventory_of_listed_values(
        feature_id="C-1",
        listed_values_to_add=[
            {
                "en": "One new value",
                "ru": "Одно новое значение",
            },
            {
                "en": "Another new value",
                "ru": "Другое новое значение",
            },
            {
                "en": "And one more value",
                "ru": "И еще одно значение",
            },
        ],
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_new_C_1.csv",
    )


def test__add_values_of_new_feature_to_inventory_of_listed_values_in_the_middle_of_category(
    test_feature_adder,
):
    test_feature_adder._add_values_of_new_feature_to_inventory_of_listed_values(
        feature_id="C-2",
        listed_values_to_add=[
            {
                "en": "One new value",
                "ru": "Одно новое значение",
            },
            {
                "en": "Another new value",
                "ru": "Другое новое значение",
            },
            {
                "en": "And one more value",
                "ru": "И еще одно значение",
            },
        ],
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_new_C_2.csv",
    )


def test__add_values_of_new_feature_to_inventory_of_listed_values_at_the_end_of_category(
    test_feature_adder,
):
    test_feature_adder._add_values_of_new_feature_to_inventory_of_listed_values(
        feature_id="C-3",
        listed_values_to_add=[
            {
                "en": "One new value",
                "ru": "Одно новое значение",
            },
            {
                "en": "Another new value",
                "ru": "Другое новое значение",
            },
            {
                "en": "And one more value",
                "ru": "И еще одно значение",
            },
        ],
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_new_C_3.csv",
    )


def test__add_values_of_new_feature_to_inventory_of_listed_values_at_the_end_of_inventory(
    test_feature_adder,
):
    test_feature_adder._add_values_of_new_feature_to_inventory_of_listed_values(
        feature_id="N-6",
        listed_values_to_add=[
            {
                "en": "One new value",
                "ru": "Одно новое значение",
            },
            {
                "en": "Another new value",
                "ru": "Другое новое значение",
            },
            {
                "en": "And one more value",
                "ru": "И еще одно значение",
            },
        ],
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES
        / "features_listed_values_new_last_feature.csv",
    )


def test__add_feature_to_feature_profiles_to_the_beginning_of_category(test_feature_adder):
    test_feature_adder._add_feature_to_feature_profiles(
        feature_id="A-1", feature_ru="Некий признак"
    )

    gold_standard_feature_profiles = list(
        (DIR_WITH_GOLD_STANDARD_FILES / "feature_profiles_new_A_1").glob("*.csv")
    )

    for file in gold_standard_feature_profiles:
        test_output_file = test_feature_adder.output_dir_with_feature_profiles / file.name

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=file,
        )


def test__add_feature_to_feature_profiles_in_the_middle_of_category(test_feature_adder):
    test_feature_adder._add_feature_to_feature_profiles(
        feature_id="A-12", feature_ru="Некий признак"
    )

    gold_standard_feature_profiles = list(
        (DIR_WITH_GOLD_STANDARD_FILES / "feature_profiles_new_A_12").glob("*.csv")
    )

    for file in gold_standard_feature_profiles:
        test_output_file = test_feature_adder.output_dir_with_feature_profiles / file.name

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=file,
        )


def test__add_feature_to_feature_profiles_at_the_end_of_category(test_feature_adder):
    test_feature_adder._add_feature_to_feature_profiles(
        feature_id="A-14", feature_ru="Некий признак"
    )

    gold_standard_feature_profiles = list(
        (DIR_WITH_GOLD_STANDARD_FILES / "feature_profiles_new_A_14").glob("*.csv")
    )

    for file in gold_standard_feature_profiles:
        test_output_file = test_feature_adder.output_dir_with_feature_profiles / file.name

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=file,
        )


# def test_add_feature_writes_good_output_files(test_feature_adder):
#     features_to_add = (
#         {
#             "category_id": "A",
#             "feature_en": "New feature in A",
#             "feature_ru": "Новый признак в A",
#         },
#         {
#             "category_id": "C",
#             "feature_en": "New feature in C",
#             "feature_ru": "Новый признак в C",
#         },
#         {
#             "category_id": "N",
#             "feature_en": "New feature in N in custom place",
#             "feature_ru": "Новый признак в N в указанной строке",
#             "insert_after_index": 2,
#         },
#         # adding to the very end of file (with custom index):
#         {
#             "category_id": "N",
#             "feature_en": "New feature in N inserted after 5",
#             "feature_ru": "Новый признак N после 5",
#             "insert_after_index": 5,
#         },
#         # adding to the very end of file:
#         {
#             "category_id": "N",
#             "feature_en": "New feature in N (in the very end)",
#             "feature_ru": "Новый признак N конец",
#         },
#     )

#     for kwargs in features_to_add:
#         test_feature_adder.add_feature(**kwargs, listed_values_to_add=dummy_values_to_add)

#         # Re-wire output to input after addition of first feature,
#         # otherwise the adder will just take the input file again
#         # and only last feature will be added in the end:
#         test_feature_adder.input_file_with_features = test_feature_adder.output_file_with_features
#         test_feature_adder.input_file_with_listed_values = (
#             test_feature_adder.output_file_with_listed_values
#         )
#         test_feature_adder.input_feature_profiles = (
#             test_feature_adder.output_dir_with_feature_profiles.glob("*.csv")
#         )
#         # This is justified in test because in normal use output file is same as input
#         # file and features will be added one by one.

#     assert test_feature_adder.output_file_with_features.exists()
#     assert test_feature_adder.input_file_with_listed_values.exists()

#     gold_standard_feature_profiles = list(
#         (OUTPUT_DIR_FOR_FEATURE_ADDER_FEATURE_PROFILES / "gold_standard").glob("*.csv")
#     )

#     check_existence_of_output_csv_file_and_compare_with_gold_standard(
#         output_file=test_feature_adder.output_file_with_features,
#         gold_standard_file=DIR_WITH_ADDERS_TEST_FILES
#         / "features_gold_standard_after_addition.csv",
#     )

#     check_existence_of_output_csv_file_and_compare_with_gold_standard(
#         output_file=test_feature_adder.output_file_with_listed_values,
#         gold_standard_file=DIR_WITH_ADDERS_TEST_FILES
#         / "features_listed_values_gold_standard_for_feature_adder.csv",
#     )

#     for file in gold_standard_feature_profiles:
#         test_output_file = test_feature_adder.output_dir_with_feature_profiles / file.name

#         check_existence_of_output_csv_file_and_compare_with_gold_standard(
#             output_file=test_output_file,
#             gold_standard_file=file,
#         )


def test__increment_feature_indices_of_values_following_the_inserted_value_that_belongs_to_brand_new_feature(
    test_feature_adder,
):

    test_feature_adder._increment_feature_indices_of_values_following_the_inserted_value_that_belongs_to_brand_new_feature(
        input_filepath=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_ADDER
        / "features_listed_values_with_new_B_14_1_inside_new_feature_B_14.csv",
        output_filepath=test_feature_adder.output_file_with_listed_values,
        line_number_of_insertion=267,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES
        / "features_listed_values_with_new_B_14_1_inside_new_feature_B_14_and_aligned_indices.csv",
    )


def test__increment_feature_indices_of_values_following_the_inserted_value_that_belongs_to_brand_new_feature_does_nothing(
    test_feature_adder,
):

    test_feature_adder._increment_feature_indices_of_values_following_the_inserted_value_that_belongs_to_brand_new_feature(
        input_filepath=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_ADDER
        / "features_listed_values_with_new_A_22_1.csv",
        output_filepath=test_feature_adder.output_file_with_listed_values,
        line_number_of_insertion=168,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES
        / "features_listed_values_with_new_A_22_1_no_changes.csv",
    )


def test__add_first_listed_value(test_feature_adder):

    test_feature_adder._add_first_listed_value(
        feature_id="C-3",
        first_value={
            "en": "New value",
            "ru": "Новое значение",
        },
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_new_C_3_1.csv",
    )
