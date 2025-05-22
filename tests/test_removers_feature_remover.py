import pytest

from langworld_db_data.removers.feature_remover import FeatureRemover, FeatureRemoverError
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from langworld_db_data.tools.files.csv_xls import read_dicts_from_csv, write_csv
from tests.paths import (
    DIR_WITH_REMOVERS_TEST_FILES,
)

DIR_WITH_REMOVERS_TEST_FILES = DIR_WITH_REMOVERS_TEST_FILES / "feature_remover"

DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER = DIR_WITH_REMOVERS_TEST_FILES / "inventories"

DIR_WITH_GOLD_STANDARD_FILES = DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER / "gold_standard"

DIR_WITH_TEST_FEATURE_PROFILES = DIR_WITH_REMOVERS_TEST_FILES / "feature_profiles"


@pytest.fixture(scope="function")
def test_remover():
    return FeatureRemover(
        file_with_categories=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER
        / "feature_categories.csv",
        input_file_with_features=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER / "features.csv",
        input_file_with_listed_values=DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER
        / "features_listed_values.csv",
        input_dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        output_file_with_features=DIR_WITH_REMOVERS_TEST_FILES / "features_output.csv",
        output_file_with_listed_values=DIR_WITH_REMOVERS_TEST_FILES
        / "features_listed_values_output.csv",
        output_dir_with_feature_profiles=DIR_WITH_REMOVERS_TEST_FILES,
    )


def test__remove_one_row_from_inventory_of_features(test_remover):

    rows = read_dicts_from_csv(
        DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER / "features.csv"
    )

    rows_with_one_line_removed = test_remover._remove_one_row(
        match_column_name="id",
        match_content="B-3",
        rows=rows,
    )

    write_csv(
        rows=rows_with_one_line_removed,
        path_to_file=test_remover.output_file_with_features,
        overwrite=True,
        delimiter=",",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "remove_one_row" / "features_without_B_3.csv",
    )


def test__remove_one_row_from_inventory_of_listed_values(test_remover):

    rows = read_dicts_from_csv(
        DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER / "features_listed_values.csv"
    )

    rows_with_one_line_removed = test_remover._remove_one_row(
        match_column_name="id",
        match_content="A-3-2",
        rows=rows,
    )

    write_csv(
        rows=rows_with_one_line_removed,
        path_to_file=test_remover.output_file_with_listed_values,
        overwrite=True,
        delimiter=",",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "remove_one_row" / "features_listed_values_without_A_3_2.csv",
    )


def test__remove_one_row_from_a_feature_profile(test_remover):

    rows = read_dicts_from_csv(
        DIR_WITH_TEST_FEATURE_PROFILES / "corsican.csv"
    )

    rows_with_one_line_removed = test_remover._remove_one_row(
        match_column_name="feature_id",
        match_content="B-3",
        rows=rows,
    )

    write_csv(
        rows=rows_with_one_line_removed,
        path_to_file=DIR_WITH_REMOVERS_TEST_FILES / "corsican.csv",
        overwrite=True,
        delimiter=",",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "remove_one_row" / "corsican_without_A_12.csv",
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
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES
        / "features_listed_values_without_A_20.csv",
    )


def test__remove_from_inventory_of_listed_values_remove_from_the_beginning_of_category(
    test_remover,
):
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
