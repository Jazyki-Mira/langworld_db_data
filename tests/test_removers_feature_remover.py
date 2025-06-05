import pytest

from langworld_db_data.removers.feature_remover import FeatureRemover, FeatureRemoverError
from langworld_db_data.tools.files.csv_xls import (
    remove_multiple_matching_rows_and_return_range_of_their_line_numbers,
    remove_one_matching_row_and_return_its_line_number,
)
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


@pytest.fixture(scope="function")
def dummy_rows_of_features():
    return (
        {
            "id": "A-1",
            "en": "Subject",
            "ru": "Подлежащее",
        },
        {
            "id": "A-2",
            "en": "Object",
            "ru": "Прямое дополнение",
        },
        {
            "id": "A-3",
            "en": "Predicate",
            "ru": "Сказуемое",
        },
        {
            "id": "B-1",
            "en": "Collocation",
            "ru": "Коллокация",
        },
        {
            "id": "B-2",
            "en": "Grammatical core",
            "ru": "Грамматическая основа",
        },
        {
            "id": "С-1",
            "en": "Sentence",
            "ru": "Предложение",
        },
    )


@pytest.fixture(scope="function")
def dummy_rows_of_listed_values():
    return (
        {
            "id": "A-1-1",
            "feature_id": "A-1",
            "en": "Nominative",
            "ru": "Номинатив",
        },
        {
            "id": "A-1-2",
            "feature_id": "A-1",
            "en": "Ergative",
            "ru": "Эргатив",
        },
        {
            "id": "A-1-3",
            "feature_id": "A-1",
            "en": "DSM",
            "ru": "Дифференцированное маркирование субъекта",
        },
        {
            "id": "B-1-1",
            "feature_id": "B-1",
            "en": "Agreement",
            "ru": "Согласование",
        },
        {
            "id": "B-1-2",
            "feature_id": "B-1",
            "en": "Word order",
            "ru": "Порядок слов",
        },
        {
            "id": "B-2-1",
            "feature_id": "B-2",
            "en": "Coordination",
            "ru": "Координация",
        },
    )


@pytest.fixture(scope="function")
def dummy_rows_of_feature_profile():
    return (
        {
            "feature_id": "A-1",
            "feature_name_ru": "Некий признак",
            "value_type": "listed",
            "value_id": "A-1-1",
        },
        {
            "feature_id": "A-2",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-2-2",
        },
        {
            "feature_id": "A-3",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-3-3",
        },
        {
            "feature_id": "B-1",
            "feature_name_ru": "Четвертый признак",
            "value_type": "listed",
            "value_id": "B-1-1",
        },
        {
            "feature_id": "C-1",
            "feature_name_ru": "И еще признак",
            "value_type": "listed",
            "value_id": "C-1-1",
        },
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
