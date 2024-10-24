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

GS_DIR_WITH_REMOVERS_FEATURE_PROFILES = DIR_WITH_REMOVERS_FEATURE_PROFILES / "gold_standard"

GS_FILE_WITH_CHANGED_PROFILES_REPORT = (
    GS_DIR_WITH_REMOVERS_FEATURE_PROFILES / "changed_profiles.txt"
)

FILE_WITH_CHANGED_PROFILES_REPORT = (
    OUTPUT_DIR_FOR_LISTED_VALUE_REMOVER_FEATURE_PROFILES
    / "changed_profiles_A-9-1_No_diphthongs_and_triphthongs.txt"
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


def test__remove_from_inventory_of_listed_values_from_end_of_feature(test_remover):
    removed_value_information = test_remover._remove_from_inventory_of_listed_values(
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


def test__remove_from_inventory_of_listed_values_from_middle_of_feature(test_remover):
    removed_value_information = test_remover._remove_from_inventory_of_listed_values(
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


def test__remove_from_inventory_of_listed_values_from_beginning_of_feature(test_remover):
    removed_value_information = test_remover._remove_from_inventory_of_listed_values(
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


def test__remove_from_inventory_of_listed_values_throws_exception_with_invalid_or_absent_value_id(
    test_remover,
):
    for bad_value_id in ["A-5-256", "S-256", "ABC"]:
        with pytest.raises(ListedValueRemoverError, match="not found. Perhaps"):
            test_remover._remove_from_inventory_of_listed_values(bad_value_id)
            test_remover.output_file_with_listed_values.unlink()


# In profiles, instances of the removed value must turn custom. The user must be notified about it.
# Also, a file must be created which enumerates all profiles where the delete value has gone custom


def test__remove_from_feature_profiles(test_remover):

    stems_of_files_that_must_be_changed = [
        "corsican",
        "ukrainian",
    ]

    stems_of_files_that_must_not_be_changed = [
        "catalan",
        "franco_provencal",
        "pashto",
    ]

    test_remover._remove_from_feature_profiles(
        id_of_value_to_remove="A-9-1",
        english_name_of_value_to_remove="No diphthongs and triphthongs",
    )

    assert FILE_WITH_CHANGED_PROFILES_REPORT.exists()

    for stem in stems_of_files_that_must_be_changed:
        assert (test_remover.output_dir_with_feature_profiles / f"{stem}.csv").exists(), (
            f"File {stem}.csv was not created. It means that no changes were made while"
            " there should have been changes"
        )

    for file in test_remover.output_dir_with_feature_profiles.glob("*.csv"):
        assert (
            file.stem not in stems_of_files_that_must_not_be_changed
        ), f"File {file.name} is not supposed to be changed"

        print(f"TEST: checking amended feature profile {file.name}")

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=file,
            gold_standard_file=GS_DIR_WITH_REMOVERS_FEATURE_PROFILES / file.name,
        )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=FILE_WITH_CHANGED_PROFILES_REPORT,
        gold_standard_file=GS_FILE_WITH_CHANGED_PROFILES_REPORT,
    )
