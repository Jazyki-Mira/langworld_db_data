import pytest

from langworld_db_data.tools.common.adder import Adder, AdderError
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import (
    DIR_WITH_FEATURE_PROFILES_FOR_TESTING_ADDER,
    DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER,
    DIR_WITH_INVENTORIES_FOR_TESTING_ADDER,
    DIR_WITH_OUTPUT_FILES_FOR_TESTING_ADDER,
)


@pytest.fixture(scope="function")
def test_adder():
    return Adder(
        file_with_categories=DIR_WITH_INVENTORIES_FOR_TESTING_ADDER / "feature_categories.csv",
        input_file_with_features=DIR_WITH_INVENTORIES_FOR_TESTING_ADDER / "features.csv",
        input_file_with_listed_values=DIR_WITH_INVENTORIES_FOR_TESTING_ADDER
        / "features_listed_values.csv",
        input_dir_with_feature_profiles=DIR_WITH_FEATURE_PROFILES_FOR_TESTING_ADDER,
        output_file_with_features=DIR_WITH_OUTPUT_FILES_FOR_TESTING_ADDER / "features.csv",
        output_file_with_listed_values=DIR_WITH_OUTPUT_FILES_FOR_TESTING_ADDER
        / "features_listed_values.csv",
        output_dir_with_feature_profiles=DIR_WITH_OUTPUT_FILES_FOR_TESTING_ADDER,
    )


def test__validate_arguments_for_adding_feature_passes(test_adder):

    for set_of_good_args in (
        {
            "category_id": "C",
            "feature_en": "feature",
            "feature_ru": "признак",
            "listed_values_to_add": [
                {
                    "en": "value",
                    "ru": "значение",
                },
            ],
            "index_to_assign": None,
        },
        {
            "category_id": "C",
            "feature_en": "feature",
            "feature_ru": "признак",
            "listed_values_to_add": [
                {
                    "en": "value",
                    "ru": "значение",
                },
            ],
            "index_to_assign": 3,
        },
        {
            "category_id": "C",
            "feature_en": "feature",
            "feature_ru": "признак",
            "listed_values_to_add": [
                {
                    "en": "value",
                    "ru": "значение",
                },
            ],
            "index_to_assign": 1,
        },
    ):
        test_adder._validate_arguments(
            feature_or_value="feature",
            args_to_validate=set_of_good_args,
        )


def test__check_that_all_obligatory_args_are_not_empty_for_feature_fails(
    test_adder,
):

    for set_of_bad_args in (
        {
            "category_id": "",
            "feature_en": "feature",
            "feature_ru": "признак",
            "listed_values_to_add": [
                {
                    "en": "value",
                    "ru": "значение",
                },
            ],
        },
        {
            "category_id": "C",
            "feature_en": "",
            "feature_ru": "признак",
            "listed_values_to_add": [
                {
                    "en": "value",
                    "ru": "значение",
                },
            ],
        },
        {
            "category_id": "C",
            "feature_en": "feature",
            "feature_ru": "",
            "listed_values_to_add": [
                {
                    "en": "value",
                    "ru": "значение",
                },
            ],
        },
        {
            "category_id": "C",
            "feature_en": "feature",
            "feature_ru": "признак",
            "listed_values_to_add": [],
        },
    ):
        with pytest.raises(AdderError, match="None of the following arguments"):
            test_adder._check_that_all_obligatory_args_are_not_empty(
                feature_or_value="feature",
                args_to_validate=set_of_bad_args,
            )


def test__check_validity_of_keys_in_passed_listed_values_fails(
    test_adder,
):

    with pytest.raises(
        AdderError,
        match=(
            "Each listed value must have keys 'en' and 'ru'. Your "
            "value: {'this': 'should fail', 'en': 'this is fine'}"
        ),
    ):
        test_adder._check_validity_of_keys_in_passed_listed_values(
            listed_values_to_add=[
                {"ru": "раз", "en": "this is fine"},
                {"this": "should fail", "en": "this is fine"},
            ]
        )


def test__check_that_category_or_feature_where_to_add_exists_fails_with_non_existing_category(
    test_adder,
):

    with pytest.raises(
        AdderError,
        match=("Category ID X not found in file" f" {test_adder.file_with_categories.name}"),
    ):
        test_adder._check_that_category_or_feature_where_to_add_exists(
            feature_or_value="feature",
            args_to_validate={
                "category_id": "X",
                "feature_ru": "имя",
                "feature_en": "name",
                "listed_values_to_add": [
                    {
                        "en": "value",
                        "ru": "значение",
                    },
                ],
            },
        )


def test__check_that_en_and_ru_are_not_already_used_in_features_inventory_fails(
    test_adder,
):

    for en, ru in (
        ("Types of phonation", "Новый признак"),
        ("New  feature", "Типы фонации"),
    ):
        with pytest.raises(AdderError, match="name is already present in"):
            test_adder._check_that_en_and_ru_are_not_already_used(
                feature_or_value="feature",
                args_to_validate={
                    "category_id": "A",
                    "feature_en": en,
                    "feature_ru": ru,
                    "listed_values_to_add": [
                        {
                            "en": "value",
                            "ru": "значение",
                        },
                    ],
                },
            )


def test__check_validity_of_index_to_assign_for_feature_fails(test_adder):

    for bad_feature_index in (0, -7, 418):
        with pytest.raises(
            ValueError,
            match="Invalid index to assign",
        ):
            test_adder._check_validity_of_index_to_assign(
                feature_or_value="feature",
                args_to_validate={
                    "category_id": "C",
                    "feature_en": "Something",
                    "feature_ru": "Что-нибудь",
                    "listed_values_to_add": [
                        {
                            "en": "some value",
                            "ru": "некое значение",
                        },
                    ],
                    "index_to_assign": bad_feature_index,
                },
            )


def test__validate_arguments_for_adding_value_passes(test_adder):

    for set_of_good_args in (
        {
            "feature_id": "A-20",
            "value_en": "Special feature",
            "value_ru": "Особый признак",
            "index_to_assign": None,
        },
        {
            "feature_id": "A-20",
            "value_en": "Special feature",
            "value_ru": "Особый признак",
            "index_to_assign": 19,
        },
        {
            "feature_id": "A-20",
            "value_en": "Special feature",
            "value_ru": "Особый признак",
            "index_to_assign": 14,
        },
    ):
        test_adder._validate_arguments(
            feature_or_value="value",
            args_to_validate=set_of_good_args,
        )


def test__check_that_all_obligatory_args_are_not_empty_for_value_fails(test_adder):

    for set_of_bad_args in (
        {
            "feature_id": "",
            "value_en": "value",
            "value_ru": "значение",
        },
        {
            "feature_id": "C",
            "value_en": "",
            "value_ru": "значение",
        },
        {
            "feature_id": "C",
            "value_en": "value",
            "value_ru": "",
        },
    ):
        with pytest.raises(AdderError, match="must be empty, but an empty"):
            test_adder._check_that_all_obligatory_args_are_not_empty(
                feature_or_value="value",
                args_to_validate=set_of_bad_args,
            )


def test__check_that_category_or_feature_where_to_add_exists_fails_with_non_existing_feature(
    test_adder,
):

    with pytest.raises(
        AdderError,
        match=("Feature ID X-68 not found in file" f" {test_adder.input_file_with_features.name}"),
    ):
        test_adder._check_that_category_or_feature_where_to_add_exists(
            feature_or_value="value",
            args_to_validate={
                "feature_id": "X-68",
                "value_en": "name",
                "value_ru": "имя",
            },
        )


def test__check_that_en_and_ru_are_not_already_used_in_values_inventory_fails(
    test_adder,
):

    for en, ru in (
        ("Uvular", "Новое значение"),
        ("New  value", "Увулярные"),
    ):
        with pytest.raises(AdderError, match="name is already present in"):
            test_adder._check_that_en_and_ru_are_not_already_used(
                feature_or_value="value",
                args_to_validate={
                    "feature_id": "G-3",
                    "value_en": en,
                    "value_ru": ru,
                },
            )


def test__check_validity_of_index_to_assign_for_value_invalid(test_adder):

    for bad_feature_index in (0, -7, 418):
        with pytest.raises(
            ValueError,
            match="Invalid index to assign",
        ):
            test_adder._validate_arguments(
                feature_or_value="value",
                args_to_validate={
                    "feature_id": "C-1",
                    "value_en": "Something",
                    "value_ru": "Что-нибудь",
                    "index_to_assign": bad_feature_index,
                },
            )


def test__check_if_index_to_assign_is_in_list_of_applicable_indices_from_features_inventory_index_available(
    test_adder,
):
    # First case is insertion in the middle of category,
    # second case is appending to the end
    category_ids_to_indices = (
        {
            "category_id": "J",
            "index_to_validate": 5,
        },
        {
            "category_id": "G",
            "index_to_validate": 8,
        },
    )

    for category_id_to_index in category_ids_to_indices:
        assert test_adder._check_if_index_to_assign_is_in_list_of_applicable_indices(
            index_to_validate=category_id_to_index["index_to_validate"],
            category_or_feature="category",
            category_or_feature_id=category_id_to_index["category_id"],
        )


def test__check_if_index_to_assign_is_in_list_of_applicable_indices_from_features_inventory_index_not_available(
    test_adder,
):

    category_ids_to_indices = (
        {
            "category_id": "J",
            "index_to_validate": 25,
        },
        {
            "category_id": "G",
            "index_to_validate": -8,
        },
        {
            "category_id": "A",
            "index_to_validate": 0,
        },
    )

    for category_id_to_index in category_ids_to_indices:
        assert not test_adder._check_if_index_to_assign_is_in_list_of_applicable_indices(
            index_to_validate=category_id_to_index["index_to_validate"],
            category_or_feature="category",
            category_or_feature_id=category_id_to_index["category_id"],
        )


def test__check_if_index_to_assign_is_in_list_of_applicable_indices_from_values_inventory_index_available(
    test_adder,
):
    # First case is insertion in the middle of feature,
    # second case is appending to the end
    feature_ids_to_indices = (
        {
            "feature_id": "N-1",
            "index_to_validate": 4,
        },
        {
            "feature_id": "L-1",
            "index_to_validate": 27,
        },
    )

    for feature_id_to_index in feature_ids_to_indices:
        assert test_adder._check_if_index_to_assign_is_in_list_of_applicable_indices(
            index_to_validate=feature_id_to_index["index_to_validate"],
            category_or_feature="feature",
            category_or_feature_id=feature_id_to_index["feature_id"],
        )


def test__check_if_index_to_assign_is_in_list_of_applicable_indices_from_values_inventory_index_not_available(
    test_adder,
):

    feature_ids_to_indices = (
        {
            "feature_id": "J-1",
            "index_to_validate": 25,
        },
        {
            "feature_id": "G-4",
            "index_to_validate": -8,
        },
        {
            "feature_id": "A-1",
            "index_to_validate": 0,
        },
    )

    for feature_id_to_index in feature_ids_to_indices:
        assert not test_adder._check_if_index_to_assign_is_in_list_of_applicable_indices(
            index_to_validate=feature_id_to_index["index_to_validate"],
            category_or_feature="feature",
            category_or_feature_id=feature_id_to_index["feature_id"],
        )


def test__get_tuple_of_currently_available_indices_in_features_inventory(test_adder):

    assert test_adder._get_tuple_of_currently_available_indices(
        category_or_feature="category",
        category_or_feature_id="J",
    ) == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    # Nine indices occupied, tenth is free


def test__get_tuple_of_currently_available_indices_in_listed_values_inventory(test_adder):

    assert test_adder._get_tuple_of_currently_available_indices(
        category_or_feature="feature",
        category_or_feature_id="A-6",
    ) == (1, 2, 3, 4, 5, 6, 7)
    # Six indices occupied, seventh is free


def test__make_id_for_new_feature_or_value_make_for_feature(test_adder):

    category_ids_to_indices = (
        {
            "category_id": "F",
            "index_to_assign": None,
            "resulting_id": "F-10",
        },
        {
            "category_id": "G",
            "index_to_assign": 8,
            "resulting_id": "G-8",
        },
        {
            "category_id": "G",
            "index_to_assign": 7,
            "resulting_id": "G-7",
        },
    )

    for category_id_to_index in category_ids_to_indices:
        assert (
            test_adder._make_id_for_new_feature_or_value(
                category_or_feature="category",
                category_or_feature_id=category_id_to_index["category_id"],
                index_to_assign=category_id_to_index["index_to_assign"],
            )
            == category_id_to_index["resulting_id"]
        )


def test__make_id_for_new_feature_or_value_make_for_value(test_adder):

    feature_ids_to_indices = (
        {
            "feature_id": "I-10",
            "index_to_assign": None,
            "resulting_id": "I-10-12",
        },
        {
            "feature_id": "H-6",
            "index_to_assign": 37,
            "resulting_id": "H-6-37",
        },
        {
            "feature_id": "H-6",
            "index_to_assign": 30,
            "resulting_id": "H-6-30",
        },
    )

    for feature_id_to_index in feature_ids_to_indices:
        assert (
            test_adder._make_id_for_new_feature_or_value(
                category_or_feature="feature",
                category_or_feature_id=feature_id_to_index["feature_id"],
                index_to_assign=feature_id_to_index["index_to_assign"],
            )
            == feature_id_to_index["resulting_id"]
        )


def test__compose_new_row_for_feature_in_inventory_without_descriptions(test_adder):

    GOLD_STANDARD_ROW = {
        "id": "A-2",
        "en": "Yet another feature",
        "ru": "Еще один признак",
        "description_formatted_en": "",
        "description_formatted_ru": "",
        "is_multiselect": "",
        "not_applicable_if": "",
        "schema_sections": "",
    }

    assert (
        test_adder._compose_new_row(
            feature_or_value="feature",
            args={
                "id": "A-2",
                "en": "Yet another feature",
                "ru": "Еще один признак",
            },
            for_feature_profile=False,
        )
        == GOLD_STANDARD_ROW
    )


def test__compose_new_row_for_feature_in_inventory_with_descriptions(test_adder):

    GOLD_STANDARD_ROW = {
        "id": "A-2",
        "en": "Yet another feature",
        "ru": "Еще один признак",
        "description_formatted_en": "Important feature",
        "description_formatted_ru": "Важный признак",
        "is_multiselect": "",
        "not_applicable_if": "",
        "schema_sections": "",
    }

    assert (
        test_adder._compose_new_row(
            feature_or_value="feature",
            args={
                "id": "A-2",
                "en": "Yet another feature",
                "ru": "Еще один признак",
                "description_formatted_en": "Important feature",
                "description_formatted_ru": "Важный признак",
            },
            for_feature_profile=False,
        )
        == GOLD_STANDARD_ROW
    )


def test__compose_new_row_for_value_without_descriptions(test_adder):

    GOLD_STANDARD_ROW = {
        "id": "A-2-3",
        "feature_id": "A-2",
        "en": "Additional value",
        "ru": "Дополнительное значение",
        "description_formatted_en": "",
        "description_formatted_ru": "",
    }

    assert (
        test_adder._compose_new_row(
            feature_or_value="value",
            args={
                "id": "A-2-3",
                "feature_id": "A-2",
                "en": "Additional value",
                "ru": "Дополнительное значение",
            },
            for_feature_profile=False,
        )
        == GOLD_STANDARD_ROW
    )


def test__compose_new_row_for_value_with_descriptions(test_adder):

    GOLD_STANDARD_ROW = {
        "id": "A-2-3",
        "feature_id": "A-2",
        "en": "Additional value",
        "ru": "Дополнительное значение",
        "description_formatted_en": "Important value",
        "description_formatted_ru": "Важное значение",
    }

    assert (
        test_adder._compose_new_row(
            feature_or_value="value",
            args={
                "id": "A-2-3",
                "feature_id": "A-2",
                "en": "Additional value",
                "ru": "Дополнительное значение",
                "description_formatted_en": "Important value",
                "description_formatted_ru": "Важное значение",
            },
            for_feature_profile=False,
        )
        == GOLD_STANDARD_ROW
    )


def test__compose_new_row_for_feature_in_feature_profile(test_adder):

    GOLD_STANDARD_ROW = {
        "feature_id": "A-2",
        "feature_name_ru": "Важный признак",
        "value_type": "not_stated",
        "value_id": "",
        "value_ru": "",
        "comment_ru": "",
        "comment_en": "",
        "page_numbers": "",
    }
    # So few attributes are filled because this is a new feature
    # which, for each profile, will be filled with a value (and, perhaps, a description)
    # manually

    assert (
        test_adder._compose_new_row(
            feature_or_value="feature",
            args={
                "feature_id": "A-2",
                "feature_name_ru": "Важный признак",
            },
            for_feature_profile=True,
        )
        == GOLD_STANDARD_ROW
    )


def test__get_line_number_where_to_insert_feature_in_inventory_not_last_in_category(test_adder):

    assert (
        test_adder._get_line_number_where_to_insert(
            feature_or_value="feature",
            new_feature_or_value_id="A-17",
            for_feature_profile=False,
        )
        == 16
    )


def test__get_line_number_where_to_insert_feature_in_inventory_last_in_category(test_adder):

    assert (
        test_adder._get_line_number_where_to_insert(
            feature_or_value="feature",
            new_feature_or_value_id="C-3",
            for_feature_profile=False,
        )
        == 37
    )


def test__get_line_number_where_to_insert_one_listed_value_in_inventory_not_last_in_feature(
    test_adder,
):

    assert (
        test_adder._get_line_number_where_to_insert(
            feature_or_value="value",
            new_feature_or_value_id="A-7-2",
            for_feature_profile=False,
        )
        == 32
    )


def test__get_line_number_where_to_insert_one_listed_value_in_inventory_last_in_feature(
    test_adder,
):

    assert (
        test_adder._get_line_number_where_to_insert(
            feature_or_value="value",
            new_feature_or_value_id="A-21-17",
            for_feature_profile=False,
        )
        == 168
    )


def test__get_line_number_where_to_insert_feature_in_feature_profile_not_last_in_category(
    test_adder,
):

    assert (
        test_adder._get_line_number_where_to_insert(
            feature_or_value="feature",
            new_feature_or_value_id="D-3",
            for_feature_profile=True,
        )
        == 17
    )


def test__get_line_number_where_to_insert_feature_in_feature_profiles_last_in_category(test_adder):

    assert (
        test_adder._get_line_number_where_to_insert(
            feature_or_value="feature",
            new_feature_or_value_id="H-10",
            for_feature_profile=True,
        )
        == 32
    )


def test__insert_new_row_at_given_line_number_in_features_inventory_not_last_in_category(
    test_adder,
):

    NEW_ROW = {
        "id": "A-17",
        "en": "Some feature",
        "ru": "Некий признак",
        "description_formatted_en": "",
        "description_formatted_ru": "",
        "is_multiselect": "",
        "not_applicable_if": "",
        "schema_sections": "",
    }

    test_adder._insert_new_row_at_given_line_number(
        new_row=NEW_ROW,
        line_number_to_insert_into=16,
        file_to_insert_into=test_adder.input_file_with_features,
        feature_or_value="feature",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER
        / "features_with_new_A_17.csv",
    )


def test__insert_new_row_at_given_line_number_in_features_inventory_last_in_category(test_adder):

    NEW_ROW = {
        "id": "C-3",
        "en": "Some feature",
        "ru": "Некий признак",
        "description_formatted_en": "",
        "description_formatted_ru": "",
        "is_multiselect": "",
        "not_applicable_if": "",
        "schema_sections": "",
    }

    test_adder._insert_new_row_at_given_line_number(
        new_row=NEW_ROW,
        line_number_to_insert_into=37,
        file_to_insert_into=test_adder.input_file_with_features,
        feature_or_value="feature",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER
        / "features_with_new_C_3.csv",
    )


def test__insert_new_row_at_given_line_number_in_values_inventory_not_last_in_feature(test_adder):

    NEW_ROW = {
        "id": "A-7-2",
        "feature_id": "A-7",
        "en": "Some value",
        "ru": "Некое значение",
        "description_formatted_en": "",
        "description_formatted_ru": "",
    }

    test_adder._insert_new_row_at_given_line_number(
        new_row=NEW_ROW,
        line_number_to_insert_into=32,
        file_to_insert_into=test_adder.input_file_with_listed_values,
        feature_or_value="value",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER
        / "features_listed_values_with_new_A_7_2.csv",
    )


def test__insert_new_row_at_given_line_number_in_values_inventory_last_in_feature(test_adder):

    NEW_ROW = {
        "id": "A-21-17",
        "feature_id": "A-21",
        "en": "Some value",
        "ru": "Некое значение",
        "description_formatted_en": "",
        "description_formatted_ru": "",
    }

    test_adder._insert_new_row_at_given_line_number(
        new_row=NEW_ROW,
        line_number_to_insert_into=168,
        file_to_insert_into=test_adder.input_file_with_listed_values,
        feature_or_value="value",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER
        / "features_listed_values_with_new_A_21_17.csv",
    )


def test__insert_new_row_at_given_line_number_in_feature_profile_not_last_in_category(test_adder):

    NEW_ROW = {
        "feature_id": "D-3",
        "feature_name_ru": "Некий признак",
        "value_type": "not_stated",
        "value_id": "",
        "value_ru": "",
        "comment_ru": "",
        "comment_en": "",
        "page_numbers": "",
    }

    test_adder._insert_new_row_at_given_line_number(
        new_row=NEW_ROW,
        line_number_to_insert_into=17,
        file_to_insert_into=test_adder.input_dir_with_feature_profiles / "catalan.csv",
        feature_or_value="feature",
        for_feature_profile=True,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_dir_with_feature_profiles / "catalan.csv",
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER
        / "feature_profile_with_new_D_3.csv",
    )


def test__insert_new_row_at_given_line_number_in_feature_profile_last_in_category(test_adder):

    NEW_ROW = {
        "feature_id": "H-10",
        "feature_name_ru": "Некий признак",
        "value_type": "not_stated",
        "value_id": "",
        "value_ru": "",
        "comment_ru": "",
        "comment_en": "",
        "page_numbers": "",
    }

    test_adder._insert_new_row_at_given_line_number(
        new_row=NEW_ROW,
        line_number_to_insert_into=32,
        file_to_insert_into=test_adder.input_dir_with_feature_profiles / "catalan.csv",
        feature_or_value="feature",
        for_feature_profile=True,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_dir_with_feature_profiles / "catalan.csv",
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER
        / "feature_profile_with_new_H_10.csv",
    )


def test__align_indices_of_features_or_values_that_come_after_inserted_one_in_features_inventory(
    test_adder,
):

    test_adder._align_indices_of_features_or_values_that_come_after_inserted_one(
        input_filepath=DIR_WITH_INVENTORIES_FOR_TESTING_ADDER / "features_with_new_A_17.csv",
        output_filepath=test_adder.output_file_with_features,
        line_number_of_insertion=16,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER
        / "features_with_new_A_17_and_aligned_indices.csv",
    )


def test__align_indices_of_features_or_values_that_come_after_inserted_one_in_listed_values_inventory(
    test_adder,
):

    test_adder._align_indices_of_features_or_values_that_come_after_inserted_one(
        input_filepath=DIR_WITH_INVENTORIES_FOR_TESTING_ADDER
        / "features_listed_values_with_new_A_7_2.csv",
        output_filepath=test_adder.output_file_with_listed_values,
        line_number_of_insertion=32,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER
        / "features_listed_values_with_new_A_7_2_and_aligned_indices.csv",
    )


def test__align_indices_of_features_or_values_that_come_after_inserted_one_in_feature_profile(
    test_adder,
):

    test_adder._align_indices_of_features_or_values_that_come_after_inserted_one(
        input_filepath=DIR_WITH_FEATURE_PROFILES_FOR_TESTING_ADDER
        / "feature_profile_with_new_D_3.csv",
        output_filepath=test_adder.output_dir_with_feature_profiles
        / "feature_profile_with_new_D_3.csv",
        line_number_of_insertion=17,
        for_feature_profile=True,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_dir_with_feature_profiles
        / "feature_profile_with_new_D_3.csv",
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER
        / "feature_profile_with_new_D_3_and_aligned_indices.csv",
    )


def test__increment_feature_indices_of_values_following_the_inserted_value_that_belongs_to_brand_new_feature(
    test_adder,
):

    test_adder._increment_feature_indices_of_values_following_the_inserted_value_that_belongs_to_brand_new_feature(
        input_filepath=DIR_WITH_INVENTORIES_FOR_TESTING_ADDER
        / "features_listed_values_with_new_B_14_1_inside_new_feature_B_14.csv",
        output_filepath=test_adder.output_file_with_listed_values,
        line_number_of_insertion=267,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES_FOR_TESTING_ADDER
        / "features_listed_values_with_new_B_14_1_inside_new_feature_B_14_and_aligned_indices.csv",
    )
