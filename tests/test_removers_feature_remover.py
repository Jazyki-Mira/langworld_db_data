import pytest

from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from langworld_db_data.removers.feature_remover import FeatureRemover, FeatureRemoverError
from tests.paths import (
    DIR_WITH_REMOVERS_TEST_FILES,
)

DIR_WITH_REMOVERS_TEST_FILES = DIR_WITH_REMOVERS_TEST_FILES / "feature_remover"

DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER = DIR_WITH_REMOVERS_TEST_FILES / "inventories"

DIR_WITH_GOLD_STANDARD_FILES = DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER / "gold_standard"


@pytest.fixture(scope="function")
def test_remover():
    return FeatureRemover(
        file_with_categories=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER / "feature_categories.csv",
        input_file_with_features=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER / "features.csv",
        input_file_with_listed_values=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER / "features_listed_values.csv",
        input_dir_with_feature_profiles=DIR_WITH_REMOVERS_TEST_FILES / "feature_profiles",
        output_file_with_features=DIR_WITH_REMOVERS_TEST_FILES / "features_output.csv",
        output_file_with_listed_values=DIR_WITH_REMOVERS_TEST_FILES / "features_listed_values_output.csv",
        output_dir_with_feature_profiles=DIR_WITH_REMOVERS_TEST_FILES,
    )


def test__remove_from_inventory_of_features_remove_from_the_middle_of_category(test_remover):
    test_remover._remove_from_inventory_of_features()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_without_A_10.csv",
    )


def test__remove_from_inventory_of_features_remove_from_the_beginning_of_category(test_remover):
    test_remover._remove_from_inventory_of_features()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_without_C_1.csv",
    )


def test__remove_from_inventory_of_features_remove_from_the_end_of_category(test_remover):
    test_remover._remove_from_inventory_of_features()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_without_D_8.csv",
    )


def test__remove_from_inventory_of_listed_values_remove_from_the_middle_of_category(test_remover):
    test_remover._remove_from_inventory_of_listed_values()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_without_A_20.csv",
    )


def test__remove_from_inventory_of_listed_values_remove_from_the_beginning_of_category(test_remover):
    test_remover._remove_from_inventory_of_listed_values()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_without_C_1.csv",
    )


def test__remove_from_inventory_of_listed_values_remove_from_the_end_of_category(test_remover):
    test_remover._remove_from_inventory_of_listed_values()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_without_D_8.csv",
    )
