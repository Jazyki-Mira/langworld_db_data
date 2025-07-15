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


def test__check_if_index_to_assign_is_in_list_of_applicable_indices_from_features_inventory_index_available(
    test_adder,
):
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
    # Should we also add None here?


def test__get_range_of_currently_existing_indices_in_listed_values_inventory(test_adder):

    assert test_adder._get_range_of_currently_existing_indices(
        category_or_feature="feature",
        category_or_feature_id="A-6",
    ) == (1, 2, 3, 4, 5, 6, 7)
    # Should we also add None here?


def test__make_id_for_new_feature_or_value_make_for_feature(test_adder):

    category_ids_to_indices = (
        {
            "category_id": "F",
            "index_to_validate": None,
            "resulting_id": "F-10",
        },
        {
            "category_id": "G",
            "index_to_validate": 8,
            "resulting_id": "G-8",
        },
        {
            "category_id": "G",
            "index_to_validate": 7,
            "resulting_id": "G-7",
        },
    )

    for category_id_to_index in category_ids_to_indices:
        assert (
            test_adder._make_id_for_new_feature_or_value(
                category_or_feature="category",
                category_or_feature_id=category_id_to_index["category_id"],
                index_to_assign=category_id_to_index["index_to_validate"],
            )
            == category_id_to_index["resulting_id"]
        )


def test__make_id_for_new_feature_or_value_make_for_value(test_adder):

    feature_ids_to_indices = (
        {
            "feature_id": "I-10",
            "index_to_validate": None,
            "resulting_id": "I-10-12",
        },
        {
            "feature_id": "H-6",
            "index_to_validate": 37,
            "resulting_id": "H-6-37",
        },
        {
            "feature_id": "H-6",
            "index_to_validate": 30,
            "resulting_id": "H-6-30",
        },
    )

    for feature_id_to_index in feature_ids_to_indices:
        assert (
            test_adder._make_id_for_new_feature_or_value(
                category_or_feature="feature",
                category_or_feature_id=feature_id_to_index["feature_id"],
                index_to_assign=feature_id_to_index["index_to_validate"],
            )
            == feature_id_to_index["resulting_id"]
        )
