import pytest

from langworld_db_data.removers.feature_remover import FeatureRemover, FeatureRemoverError
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import (
    DIR_WITH_REMOVERS_TEST_FILES,
)

DIR_WITH_REMOVERS_TEST_FILES = DIR_WITH_REMOVERS_TEST_FILES / "feature_remover"

DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER = DIR_WITH_REMOVERS_TEST_FILES / "inventories"

DIR_WITH_GOLD_STANDARD_FILES = DIR_WITH_REMOVERS_TEST_FILES / "gold_standard"

DIR_WITH_TEST_FEATURE_PROFILES = DIR_WITH_REMOVERS_TEST_FILES / "feature_profiles"


@pytest.fixture(scope="class")
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


def test__remove_from_inventory_of_features_remove_from_the_middle_of_category(test_remover):
    test_remover._remove_from_inventory_of_features(
        feature_id="A-10",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_without_A_10.csv",
    )


def test__remove_from_inventory_of_features_remove_from_the_beginning_of_category(test_remover):
    test_remover._remove_from_inventory_of_features(
        feature_id="C-1",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_without_C_1.csv",
    )


def test__remove_from_inventory_of_features_remove_from_the_end_of_category(test_remover):
    test_remover._remove_from_inventory_of_features(
        feature_id="D-8",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_without_D_8.csv",
    )


def test__remove_from_inventory_of_listed_values_remove_from_the_middle_of_category(test_remover):
    test_remover._remove_from_inventory_of_listed_values(
        feature_id="A-20",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES
        / "features_listed_values_without_A_20.csv",
    )


def test__remove_from_inventory_of_listed_values_remove_from_the_beginning_of_category(
    test_remover,
):
    test_remover._remove_from_inventory_of_listed_values(
        feature_id="C-1",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_without_C_1.csv",
    )


def test__remove_from_inventory_of_listed_values_remove_from_the_end_of_category(test_remover):
    test_remover._remove_from_inventory_of_listed_values(
        feature_id="D-8",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_without_D_8.csv",
    )


def test__remove_from_feature_profiles_remove_from_the_beginning_of_category(test_remover):
    test_remover._remove_from_feature_profiles(
        feature_id="C-1",
    )

    gold_standard_feature_profiles = list(
        (DIR_WITH_GOLD_STANDARD_FILES / "feature_profiles_after_deletion_of_C_1").glob("*.csv")
    )

    for file in gold_standard_feature_profiles:
        test_output_file = test_remover.output_dir_with_feature_profiles / file.name

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=file,
        )


def test__remove_from_feature_profiles_remove_from_the_middle_of_category(test_remover):
    test_remover._remove_from_feature_profiles(
        feature_id="D-7",
    )

    gold_standard_feature_profiles = list(
        (DIR_WITH_GOLD_STANDARD_FILES / "feature_profiles_after_deletion_of_D_7").glob("*.csv")
    )

    for file in gold_standard_feature_profiles:
        test_output_file = test_remover.output_dir_with_feature_profiles / file.name

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=file,
        )


def test__remove_from_feature_profiles_remove_from_the_end_of_category(test_remover):
    test_remover._remove_from_feature_profiles(
        feature_id="D-8",
    )

    gold_standard_feature_profiles = list(
        (DIR_WITH_GOLD_STANDARD_FILES / "feature_profiles_after_deletion_of_D_8").glob("*.csv")
    )

    for file in gold_standard_feature_profiles:
        test_output_file = test_remover.output_dir_with_feature_profiles / file.name

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=file,
        )


def test_remove_feature(test_remover):
    test_remover.remove_feature(feature_id="N-3")

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_features,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_without_N_3.csv",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_GOLD_STANDARD_FILES / "features_listed_values_without_N_3.csv",
    )

    gold_standard_feature_profiles = list(
        (DIR_WITH_GOLD_STANDARD_FILES / "feature_profiles_after_deletion_of_N_3").glob("*.csv")
    )

    for file in gold_standard_feature_profiles:
        test_output_file = test_remover.output_dir_with_feature_profiles / file.name

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=file,
        )


def test_remove_feature_throws_exception_with_invalid_feature_ID(test_remover):

    with pytest.raises(FeatureRemoverError, match="Feature ID <X-1> not found in file"):
        test_remover.remove_feature(
            feature_id="X-1",
        )
