import pytest
from tinybear.csv_xls import write_csv

from tests.helpers import (
    check_existence_of_output_csv_file_and_compare_with_gold_standard,
    check_existence_of_output_csv_files_in_dir_and_compare_them_with_gold_standards,
)

# selecting these files/dirs for no specific reason, can be anything that is CSV:
from tests.paths import (
    DIR_WITH_ADDERS_TEST_FILES,
    DIR_WITH_TEST_FILES,
    INPUT_FILE_WITH_LISTED_VALUES,
)

DIR_WITH_HELPERS_TEST_FILES = DIR_WITH_TEST_FILES / "helpers"
VALID_OUTPUT_DIR = DIR_WITH_HELPERS_TEST_FILES / "output_dir"
OUTPUT_DIR_WITH_MISSING_FILES = DIR_WITH_HELPERS_TEST_FILES / "output_dir_without_some_files"
OUTPUT_DIR_WITH_INCORRECT_FILE = DIR_WITH_HELPERS_TEST_FILES / "output_dir_with_incorrect_file"
GOLD_STANDARD_DIR = DIR_WITH_HELPERS_TEST_FILES / "gold_standard_dir"


def test_check_existence_of_output_csv_file_and_compare_with_gold_standard_passes_with_identical_files():  # noqa E501
    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=INPUT_FILE_WITH_LISTED_VALUES,
        gold_standard_file=INPUT_FILE_WITH_LISTED_VALUES,
        unlink_if_successful=False,
    )


def test_check_existence_of_output_csv_file_and_compare_with_gold_standard_fails_with_different_files():  # noqa E501
    with pytest.raises(AssertionError):
        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=INPUT_FILE_WITH_LISTED_VALUES,
            gold_standard_file=DIR_WITH_ADDERS_TEST_FILES / "features.csv",
            unlink_if_successful=False,
        )


def test_check_existence_of_output_csv_files_in_dir_and_compare_them_with_gold_standards_passes():
    check_existence_of_output_csv_files_in_dir_and_compare_them_with_gold_standards(
        output_dir=VALID_OUTPUT_DIR,
        gold_standard_dir=GOLD_STANDARD_DIR,
        unlink_files_if_successful=False,
        remove_output_dir_if_successful=False,
    )

def test_check_existence_of_output_csv_files_in_dir_and_compare_them_with_gold_standards_fails_with_some_output_files_missing():
    with pytest.raises(AssertionError):
        check_existence_of_output_csv_files_in_dir_and_compare_them_with_gold_standards(
            output_dir=OUTPUT_DIR_WITH_MISSING_FILES,
            gold_standard_dir=GOLD_STANDARD_DIR,
            unlink_files_if_successful=False,
            remove_output_dir_if_successful=False,
        )


def test_check_existence_of_output_csv_files_in_dir_and_compare_them_with_gold_standards_fails_with_an_incorrect_output_file():
    with pytest.raises(AssertionError):
        check_existence_of_output_csv_files_in_dir_and_compare_them_with_gold_standards(
            output_dir=OUTPUT_DIR_WITH_INCORRECT_FILE,
            gold_standard_dir=GOLD_STANDARD_DIR,
            unlink_files_if_successful=False,
            remove_output_dir_if_successful=False,
        )


def test_check_existence_of_output_csv_file_and_compare_with_gold_standard_unlinks_output_file_after_comparison():  # noqa E501
    dummy_gold_standard_file = DIR_WITH_TEST_FILES / "helpers_dummy_gold_standard.csv"
    dummy_output_file = DIR_WITH_TEST_FILES / "helpers_dummy_output.csv"

    rows = [["id", "en"], ["1", "foo"]]

    for path in dummy_output_file, dummy_gold_standard_file:
        write_csv(rows, path, overwrite=True, delimiter=",")

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=dummy_output_file,
        gold_standard_file=dummy_gold_standard_file,
    )

    assert not dummy_output_file.exists()
    assert dummy_gold_standard_file.exists()
    dummy_gold_standard_file.unlink()
