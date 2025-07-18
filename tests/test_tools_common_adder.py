import pytest

from langworld_db_data.tools.common.adder import Adder, AdderError
from tests.paths import (
    DIR_WITH_FEATURE_PROFILES_FOR_TESTING_ADDER,
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


def test__validate_arguments_for_adding_feature_passes_with_default_index_to_assign(test_adder):
    
    test_adder._validate_arguments(
        feature_or_value="feature",
        args_of_new_feature_or_value={       
            "category_id": "C",
            "feature_en": "feature",
            "feature_ru": "признак",
            "listed_values_to_add": [
                {
                    "en": "value",
                    "ru": "значение",
                },
            ],
        },
    )


def test__validate_arguments_for_adding_feature_passes_with_given_index_to_assign(test_adder):
    
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
            args_of_new_feature_or_value=set_of_good_args,
        )


def test__validate_arguments_for_adding_feature_fails_with_some_obligatory_args_are_missing(test_adder):
    
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
        {
            "category_id": "C",
            "feature_en": "feature",
            "feature_ru": "признак",
            "listed_values_to_add": [
                {
                    "en": "",
                    "ru": "",
                },
            ],
        },
    ):
        with pytest.raises(AdderError, match="Some of the values passed are empty:"):
            test_adder._validate_arguments(
                feature_or_value="feature",
                args_of_new_feature_or_value=set_of_bad_args,
            )


def test__validate_arguments_for_adding_feature_fails_with_invalid_keys_in_listed_values_to_add(test_adder):

    with pytest.raises(
        AdderError,
        match=(
            "must have keys 'en' and 'ru'. Your value: {'this': 'should fail', 'en':"
            " 'this is fine'}"
        ),
    ):
        test_adder._validate_arguments(
            feature_or_value="feature",
            args_of_new_feature_or_value={
                "category_id": "A",
                "feature_ru": "раз",
                "feature_en": "one",
                "listed_values_to_add": [
                    {"ru": "раз", "en": "this is fine"},
                    {"this": "should fail", "en": "this is fine"},
                ],
            },
        )


def test__validate_arguments_for_adding_feature_fails_with_category_id_absent_from_inventory(test_adder):

    with pytest.raises(
        AdderError,
        match=(
            "Category ID <X> not found in file" f" {test_adder.file_with_categories.name}"
        ),
    ):
        test_adder._validate_arguments(
            feature_or_value="feature",
            args_of_new_feature_or_value={
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


def test__validate_arguments_for_adding_feature_fails_with_en_or_ru_name_of_feature_already_occupied(test_adder):

    for en, ru in (
        ("Stress character ", "Новый признак"),
        ("New  feature", "Типы фонации"),
    ):
        with pytest.raises(AdderError, match="English or Russian feature name is already"):
            test_adder._validate_arguments(
                feature_or_value="feature",
                args_of_new_feature_or_value={
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


def test__validate_arguments_for_adding_feature_fails_with_invalid_feature_index(test_adder):

    for bad_feature_index in (0, -7, 418):
        with pytest.raises(
            ValueError,
            match="Invalid index_to_assign",
        ):
            test_adder._validate_arguments(
                feature_or_value="feature",
                args_of_new_feature_or_value={
                    "category_id": "C",
                    "feature_en": "Something",
                    "feature_ru": "Что-нибудь",
                    "index_to_assign": bad_feature_index,
                },
            )


def test__validate_arguments_for_adding_value_passes_with_default_index_to_assign(test_adder):

    test_adder._validate_arguments(
        feature_or_value="value",
        args_of_new_feature_or_value={       
            "feature_id": "A-8",
            "value_en": "Special feature",
            "value_ru": "Особый признак",
        },
    )


def test__validate_arguments_for_adding_value_passes_with_given_index_to_assign(test_adder):

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
            args_of_new_feature_or_value=set_of_good_args,
        )


def test__validate_arguments_for_adding_value_fails_with_some_obligatory_args_missing(test_adder):

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
        with pytest.raises(AdderError, match="Some of the values passed are empty:"):
            test_adder._validate_arguments(
                feature_or_value="value",
                args_of_new_feature_or_value=set_of_bad_args,
            )


def test__validate_arguments_for_adding_value_fails_with_feature_id_absent_from_inventory(test_adder):

    with pytest.raises(
        AdderError,
        match=(
            "Feature ID <X-68> not found in file" f" {test_adder.file_with_categories.name}"
        ),
    ):
        test_adder._validate_arguments(
            feature_or_value="feature",
            args_of_new_feature_or_value={
                "feature_id": "X-68",
                "value_en": "name",
                "value_ru": "имя",
            },
        )


def test__validate_arguments_for_adding_value_fails_with_en_or_ru_name_of_value_already_occupied(test_adder):

    for en, ru in (
        ("Uvular", "Новое значение"),
        ("New  value", "Увулярные"),
    ):
        with pytest.raises(AdderError, match="English or Russian feature name is already"):
            test_adder._validate_arguments(
                feature_or_value="value",
                args_of_new_feature_or_value={
                    "feature_id": "G-3",
                    "value_en": en,
                    "value_ru": ru,
                },
            )


def test__validate_arguments_for_adding_value_fails_with_invalid_index_to_assign(test_adder):

    for bad_feature_index in (0, -7, 418):
        with pytest.raises(
            ValueError,
            match="Invalid index_to_assign",
        ):
            test_adder._validate_arguments(
                feature_or_value="feature",
                args_of_new_feature_or_value={
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

    with pytest.raises(AdderError, match="invalid index to assign"):
        for category_id_to_index in category_ids_to_indices:
            test_adder._check_if_index_to_assign_is_in_list_of_applicable_indices(
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

    with pytest.raises(AdderError, match="invalid index to assign"):
        for feature_id_to_index in feature_ids_to_indices:
            test_adder._check_if_index_to_assign_is_in_list_of_applicable_indices(
                index_to_validate=feature_id_to_index["index_to_validate"],
                category_or_feature="feature",
                category_or_feature_id=feature_id_to_index["feature_id"],
            )


def test__get_range_of_currently_existing_indices_in_features_inventory(test_adder):

    assert test_adder._get_range_of_currently_existing_indices(
        category_or_feature="category",
        category_or_feature_id="J",
    ) == (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    # Nine indices occupied, tenth is free


def test__get_range_of_currently_existing_indices_in_listed_values_inventory(test_adder):

    assert test_adder._get_range_of_currently_existing_indices(
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

    assert test_adder._compose_new_row(
        feature_or_value="feature",
        args_of_new_feature_or_value=(
            "A-2",
            "Yet another feature",
            "Еще один признак",
        ),
        for_feature_profile=False,
    ) == GOLD_STANDARD_ROW


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

    assert test_adder._compose_new_row(
        feature_or_value="feature",
        args_of_new_feature_or_value=(
            "A-2",
            "Yet another feature",
            "Еще один признак",
            "Important feature",
            "Важный признак",
        ),
        for_feature_profile=False,
    ) == GOLD_STANDARD_ROW


def test__compose_new_row_for_value_without_descriptions(test_adder):
    
    GOLD_STANDARD_ROW = {
        "id": "A-2-3",
        "feature_id": "A-2",
        "en": "Additional value",
        "ru": "Дополнительное значение",
        "description_formatted_en": "",
        "description_formatted_ru": "",
    }

    assert test_adder._compose_new_row(
        feature_or_value="value",
        args_of_new_feature_or_value=(
            "A-2-3",
            "A-2",
            "Additional value",
            "Дополнительное значение",
        ),
        for_feature_profile=False,
    ) == GOLD_STANDARD_ROW


def test__compose_new_row_for_value_with_descriptions(test_adder):
    
    GOLD_STANDARD_ROW = {
        "id": "A-2-3",
        "feature_id": "A-2",
        "en": "Additional value",
        "ru": "Дополнительное значение",
        "description_formatted_en": "Important value",
        "description_formatted_ru": "Важное значение",
    }

    assert test_adder._compose_new_row(
        feature_or_value="value",
        args_of_new_feature_or_value=(
            "A-2-3",
            "A-2",
            "Additional value",
            "Дополнительное значение",
            "Important value",
            "Важное значение",
        ),
        for_feature_profile=False,
    ) == GOLD_STANDARD_ROW


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

    assert test_adder._compose_new_row(
        feature_or_value="feature",
        args_of_new_feature_or_value=(
            "A-2",
            "Важный признак",
        ),
        for_feature_profile=True,
    ) == GOLD_STANDARD_ROW


def test__get_line_number_where_to_insert_feature_in_inventory_not_last_in_category(test_adder):
    
    assert test_adder._get_line_number_where_to_insert(
        feature_or_value="feature",
        new_feature_or_value_id="A-17",
        for_feature_profile=False,
    ) == 18


def test__get_line_number_where_to_insert_feature_in_inventory_last_in_category(test_adder):
    
    assert test_adder._get_line_number_where_to_insert(
        feature_or_value="feature",
        new_feature_or_value_id="C-3",
        for_feature_profile=False,
    ) == 39


def test__get_line_number_where_to_insert_one_listed_value_in_inventory_not_last_in_feature(test_adder):

    assert test_adder._get_line_number_where_to_insert(
        feature_or_value="value",
        new_feature_or_value_id="A-7-2",
        for_feature_profile=False,
    ) == 34


def test__get_line_number_where_to_insert_one_listed_value_in_inventory_last_in_feature(test_adder):

    assert test_adder._get_line_number_where_to_insert(
        feature_or_value="value",
        new_feature_or_value_id="A-21-17",
        for_feature_profile=False,
    ) == 170


def test__get_line_number_where_to_insert_several_listed_values_in_inventory_not_last_in_category(test_adder):

    assert test_adder._get_line_number_where_to_insert(
        feature_or_value="feature",
        new_feature_or_value_id="D-3",
        for_feature_profile=True,
    ) == 19


def test__get_line_number_where_to_insert_feature_in_feature_profiles_last_in_category(test_adder):

    assert test_adder._get_line_number_where_to_insert(
        feature_or_value="feature",
        new_feature_or_value_id="H-10",
        for_feature_profile=True,
    ) == 34
