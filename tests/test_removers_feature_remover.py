import pytest

from langworld_db_data.removers.feature_remover import FeatureRemover, FeatureRemoverError
from langworld_db_data.tools.files.csv_xls import read_dicts_from_csv, write_csv
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import (
    DIR_WITH_REMOVERS_TEST_FILES,
)

DIR_WITH_REMOVERS_TEST_FILES = DIR_WITH_REMOVERS_TEST_FILES / "feature_remover"

DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER = DIR_WITH_REMOVERS_TEST_FILES / "inventories"

DIR_WITH_GOLD_STANDARD_FILES = DIR_WITH_INVENTORIES_FOR_TESTING_FEATURE_REMOVER / "gold_standard"

DIR_WITH_TEST_FEATURE_PROFILES = DIR_WITH_REMOVERS_TEST_FILES / "feature_profiles"


DUMMY_ROWS_OF_FEATURES = (
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

DUMMY_ROWS_OF_LISTED_VALUES = (
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

DUMMY_ROWS_OF_FEATURE_PROFILE = (
    {
        "feature_id": "A-1",
        "feature_name_ru": "Некий признак",
        "value_type": "listed",
        "value_id": "A-1-3",
    },
    {
        "feature_id": "A-2",
        "feature_name_ru": "Еще один признак",
        "value_type": "listed",
        "value_id": "A-2-1",
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
        "value_id": "B-1-3",
    },
    {
        "feature_id": "C-1",
        "feature_name_ru": "И еще признак",
        "value_type": "listed",
        "value_id": "C-1-6",
    },
)


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


def test__remove_one_row_and_return_its_line_number_remove_from_inventory_of_features(
    test_remover,
):

    GOLD_STANDARD_DUMMY_ROWS = (
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

    rows_with_one_line_removed, line_number_of_removed_row = (
        test_remover._remove_one_matching_row_and_return_its_line_number(
            match_column_name="id",
            match_content="A-3",
            rows=DUMMY_ROWS_OF_FEATURES,
        )
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == 2


def test__remove_one_row_from_inventory_of_listed_values(test_remover):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "A-1-1",
            "feature_id": "A-1",
            "en": "Nominative",
            "ru": "Номинатив",
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

    rows_with_one_line_removed, line_number_of_removed_row = (
        test_remover._remove_one_matching_row_and_return_its_line_number(
            match_column_name="id",
            match_content="A-1-2",
            rows=DUMMY_ROWS_OF_LISTED_VALUES,
        )
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == 1


def test__remove_one_row_from_a_feature_profile(test_remover):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "feature_id": "A-1",
            "feature_name_ru": "Некий признак",
            "value_type": "listed",
            "value_id": "A-1-3",
        },
        {
            "feature_id": "A-2",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-2-1",
        },
        {
            "feature_id": "A-3",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-3-3",
        },
        {
            "feature_id": "C-1",
            "feature_name_ru": "И еще признак",
            "value_type": "listed",
            "value_id": "C-1-6",
        },
    )

    rows_with_one_line_removed, line_number_of_removed_row = (
        test_remover._remove_one_matching_row_and_return_its_line_number(
            match_column_name="feature_id",
            match_content="B-1",
            rows=DUMMY_ROWS_OF_FEATURE_PROFILE,
        )
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == 3


def test__remove_one_row_remove_last_row(test_remover):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "feature_id": "A-1",
            "feature_name_ru": "Некий признак",
            "value_type": "listed",
            "value_id": "A-1-3",
        },
        {
            "feature_id": "A-2",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-2-1",
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
            "value_id": "B-1-3",
        },
    )

    rows_with_one_line_removed, line_number_of_removed_row = (
        test_remover._remove_one_matching_row_and_return_its_line_number(
            match_column_name="feature_id",
            match_content="C-1",
            rows=DUMMY_ROWS_OF_FEATURE_PROFILE,
        )
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == 4


def test__remove_one_row_throws_exception_invalid_match_content(test_remover):

    for bad_arg in ("abc", "A-189"):
        with pytest.raises(Exception, match="Row with given properties not found"):

            _, _ = test_remover._remove_one_row_and_return_its_line_number(
                match_column_name="id",
                match_content=bad_arg,
                rows=DUMMY_ROWS_OF_LISTED_VALUES,
            )


def test__remove_multiple_matching_rows_and_return_range_of_their_line_numbers_remove_values_of_A_1(
    test_remover,
):

    GOLD_STANDARD_DUMMY_ROWS = (
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

    rows_with_multiple_rows_removed, range_of_lin_numbers_of_removed_rows = (
        test_remover._remove_multiple_matching_rows_and_return_range_of_their_line_numbers(
            match_content="A-1",
            rows=DUMMY_ROWS_OF_LISTED_VALUES,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert range_of_lin_numbers_of_removed_rows == (0, 2)


def test__remove_multiple_matching_rows_and_return_range_of_their_line_numbers_remove_values_of_B_1(
    test_remover,
):

    GOLD_STANDARD_DUMMY_ROWS = (
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
            "id": "B-2-1",
            "feature_id": "B-2",
            "en": "Coordination",
            "ru": "Координация",
        },
    )

    rows_with_multiple_rows_removed, range_of_lin_numbers_of_removed_rows = (
        test_remover._remove_multiple_matching_rows_and_return_range_of_their_line_numbers(
            match_content="B-1",
            rows=DUMMY_ROWS_OF_LISTED_VALUES,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert range_of_lin_numbers_of_removed_rows == (3, 4)


def test__remove_multiple_matching_rows_and_return_range_of_their_line_numbers_remove_value_of_B_2(
    test_remover,
):

    GOLD_STANDARD_DUMMY_ROWS = (
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
    )

    rows_with_multiple_rows_removed, range_of_lin_numbers_of_removed_rows = (
        test_remover._remove_multiple_matching_rows_and_return_range_of_their_line_numbers(
            match_content="B-2",
            rows=DUMMY_ROWS_OF_LISTED_VALUES,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert range_of_lin_numbers_of_removed_rows == (5, 5)


def test__update_indices_after_given_line_number_if_necessary_in_features_update_is_necessary(
    test_remover,
):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "A-1",
            "en": "Subject",
            "ru": "Подлежащее",
        },
        {
            "id": "A-2",
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

    rows_without_A_2, line_number_of_removed_row = (
        test_remover._remove_one_row_and_return_its_line_number(
            match_column_name="id",
            match_content="A-2",
            rows=DUMMY_ROWS_OF_FEATURES,
        )
    )

    rows_without_A_2_with_updated_feature_indices = (
        test_remover._update_indices_after_given_line_number_if_necessary(
            match_column_name="id",
            match_content="A",
            line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
            rows=rows_without_A_2,
        )
    )

    assert rows_without_A_2_with_updated_feature_indices == GOLD_STANDARD_DUMMY_ROWS


def test__update_indices_after_given_line_number_if_necessary_in_features_update_is_not_necessary(
    test_remover,
):

    GOLD_STANDARD_DUMMY_ROWS = (
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

    rows_without_last_feature_in_category_A, line_number_of_removed_row = (
        test_remover._remove_one_row_and_return_its_line_number(
            match_column_name="id",
            match_content="A-3",
            rows=DUMMY_ROWS_OF_FEATURES,
        )
    )

    rows_without_last_feature_in_category_A_with_updated_feature_indices = (
        test_remover._update_indices_after_given_line_number_if_necessary(
            match_column_name="id",
            match_content="A",
            line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
            rows=rows_without_last_feature_in_category_A,
        )
    )

    assert (
        rows_without_last_feature_in_category_A_with_updated_feature_indices
        == GOLD_STANDARD_DUMMY_ROWS
    )


def test__update_indices_after_given_line_number_if_necessary_in_feature_profile_update_is_necessary(
    test_remover,
):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "feature_id": "A-1",
            "feature_name_ru": "Некий признак",
            "value_type": "listed",
            "value_id": "A-1-3",
        },
        {
            "feature_id": "A-2",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-2-1",
        },
        {
            "feature_id": "B-1",
            "feature_name_ru": "Четвертый признак",
            "value_type": "listed",
            "value_id": "B-1-3",
        },
        {
            "feature_id": "C-1",
            "feature_name_ru": "И еще признак",
            "value_type": "listed",
            "value_id": "C-1-6",
        },
    )

    rows_without_A_2, line_number_of_removed_row = (
        test_remover._remove_one_row_and_return_its_line_number(
            match_column_name="feature_id",
            match_content="A-2",
            rows=DUMMY_ROWS_OF_FEATURES,
        )
    )

    rows_without_A_2_with_updated_feature_indices = (
        test_remover._update_indices_after_given_line_number_if_necessary(
            match_column_name="feature_id",
            match_content="A",
            line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
            rows=rows_without_A_2,
        )
    )

    assert rows_without_A_2_with_updated_feature_indices == GOLD_STANDARD_DUMMY_ROWS


def test__update_indices_after_given_line_number_if_necessary_in_feature_profile_update_is_not_necessary(
    test_remover,
):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "feature_id": "A-1",
            "feature_name_ru": "Некий признак",
            "value_type": "listed",
            "value_id": "A-1-3",
        },
        {
            "feature_id": "A-2",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-2-1",
        },
        {
            "feature_id": "B-1",
            "feature_name_ru": "Четвертый признак",
            "value_type": "listed",
            "value_id": "B-1-3",
        },
        {
            "feature_id": "C-1",
            "feature_name_ru": "И еще признак",
            "value_type": "listed",
            "value_id": "C-1-6",
        },
    )

    rows_without_last_feature_in_category_A, line_number_of_removed_row = (
        test_remover._remove_one_row_and_return_its_line_number(
            match_column_name="feature_id",
            match_content="A-3",
            rows=DUMMY_ROWS_OF_FEATURES,
        )
    )

    rows_without_last_feature_in_category_A_with_updated_feature_indices = (
        test_remover._update_indices_after_given_line_number_if_necessary(
            match_column_name="feature_id",
            match_content="A",
            line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
            rows=rows_without_last_feature_in_category_A,
        )
    )

    assert (
        rows_without_last_feature_in_category_A_with_updated_feature_indices
        == GOLD_STANDARD_DUMMY_ROWS
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
