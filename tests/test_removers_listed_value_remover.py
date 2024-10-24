import pytest

from langworld_db_data.removers.listed_value_remover import (
    ListedValueRemover,
    ListedValueRemoverError,
)
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import (
    DIR_WITH_REMOVERS_FEATURE_PROFILES,
    DIR_WITH_REMOVERS_TEST_FILES,
    INPUT_FILE_WITH_LISTED_VALUES_FOR_REMOVERS,
    OUTPUT_DIR_FOR_LISTED_VALUE_REMOVER_FEATURE_PROFILES,
)

GS_FILE_WITH_LISTED_VALUES_REMOVING_THE_FIRST = (
    DIR_WITH_REMOVERS_TEST_FILES
    / "features_listed_values_gold_standard_for_removing_the_first.csv"
)

GS_FILE_WITH_LISTED_VALUES_REMOVING_IN_MIDDLE = (
    DIR_WITH_REMOVERS_TEST_FILES
    / "features_listed_values_gold_standard_for_removing_in_middle.csv"
)

GS_FILE_WITH_LISTED_VALUES_REMOVING_THE_LAST = (
    DIR_WITH_REMOVERS_TEST_FILES / "features_listed_values_gold_standard_for_removing_the_last.csv"
)


@pytest.fixture(scope="function")
def test_remover():
    return ListedValueRemover(
        input_file_with_listed_values=INPUT_FILE_WITH_LISTED_VALUES_FOR_REMOVERS,
        output_file_with_listed_values=DIR_WITH_REMOVERS_TEST_FILES
        / "features_listed_values_output_value_remover.csv",
        input_dir_with_feature_profiles=DIR_WITH_REMOVERS_FEATURE_PROFILES,
        output_dir_with_feature_profiles=OUTPUT_DIR_FOR_LISTED_VALUE_REMOVER_FEATURE_PROFILES,
    )


def test_remove_listed_value_from_end_of_feature(test_remover):
    removed_value_information = test_remover.remove_listed_value(
        id_of_value_to_remove="A-5-8",
    )
    gs_removed_value_information = {
        "feature_id": "A-5",
        "en": "Present for front, central and back vowels",
        "ru": "В переднем, среднем и заднем рядах",
    }
    assert removed_value_information == gs_removed_value_information

    assert test_remover.output_file_with_listed_values.exists()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=GS_FILE_WITH_LISTED_VALUES_REMOVING_THE_LAST,
    )


def test_remove_listed_value_from_middle_of_feature(test_remover):
    removed_value_information = test_remover.remove_listed_value(
        id_of_value_to_remove="A-5-5",
    )
    gs_removed_value_information = {
        "feature_id": "A-5",
        "en": "Present for front and central vowels",
        "ru": "В переднем и среднем рядах",
    }
    assert removed_value_information == gs_removed_value_information

    assert test_remover.output_file_with_listed_values.exists()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=GS_FILE_WITH_LISTED_VALUES_REMOVING_IN_MIDDLE,
    )


def test_remove_listed_value_from_beginning_of_feature(test_remover):
    removed_value_information = test_remover.remove_listed_value(
        id_of_value_to_remove="A-5-1",
    )
    gs_removed_value_information = {
        "feature_id": "A-5",
        "en": "No vowel opposition in labialization",
        "ru": "Противопоставление гласных по лабиализации отсутствует",
    }
    assert removed_value_information == gs_removed_value_information

    assert test_remover.output_file_with_listed_values.exists()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_remover.output_file_with_listed_values,
        gold_standard_file=GS_FILE_WITH_LISTED_VALUES_REMOVING_THE_FIRST,
    )


def test_remove_listed_value_throws_exception_with_invalid_or_absent_value_id(test_remover):
    for bad_value_id in ["A-5-256", "S-256", "ABC"]:
        with pytest.raises(ListedValueRemoverError, match="not found. Perhaps"):
            test_remover.remove_listed_value(bad_value_id)
            test_remover.output_file_with_listed_values.unlink()


# In profiles, instances of the removed value must turn custom. The user must be notified about it.
# Also, a file msu be created which enumerates all profiles where the delete value has gone custom
