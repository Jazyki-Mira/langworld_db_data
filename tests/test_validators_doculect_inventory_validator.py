import pytest

from langworld_db_data.validators.doculect_inventory_validator import (
    DoculectInventoryValidator,
    DoculectInventoryValidatorError,
)
from tests.paths import DIR_WITH_TEST_FEATURE_PROFILES, DIR_WITH_VALIDATORS_TEST_FILES

GOOD_FILE_WITH_DOCULECTS = DIR_WITH_VALIDATORS_TEST_FILES / "doculects_OK.csv"
FILE_WITH_GENEALOGY_NAMES = (
    DIR_WITH_VALIDATORS_TEST_FILES
    / "genealogy_families_names_for_doculect_inventory_validator.csv"
)


def test__init__fails_with_file_with_non_unique_doculect_ids():
    with pytest.raises(
        DoculectInventoryValidatorError,
        match="repeating values in column <id>: ukrainian",
    ):
        _ = DoculectInventoryValidator(
            dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
            file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES
            / "doculects_bad_non_unique_doculects.csv",
        )


def test__check_family_ids_in_genealogy_fails_with_bad_file():
    with pytest.raises(
        DoculectInventoryValidatorError, match="genealogy family ID foobar not found"
    ):
        DoculectInventoryValidator(
            dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
            file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES
            / "doculects_bad_non_matching_family_id.csv",
            file_with_genealogy_names=FILE_WITH_GENEALOGY_NAMES,
        )._check_family_ids_in_genealogy()


def test__check_uniqueness_of_coordinates_fails_with_bad_file():
    with pytest.raises(DoculectInventoryValidatorError, match="identical coordinates"):
        DoculectInventoryValidator(
            dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
            file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES
            / "doculects_bad_non_unique_coordinates.csv",
            file_with_genealogy_names=FILE_WITH_GENEALOGY_NAMES,
        )._check_uniqueness_of_coordinates()


def test__match_doculects_to_files_fails_with_more_doculects_than_files():
    validator = DoculectInventoryValidator(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES
        / "doculects_bad_more_doculects_than_files.csv",
    )
    # this must not fail because all files correspond to doculects
    validator._match_files_to_doculects()

    with pytest.raises(
        DoculectInventoryValidatorError,
        match="Doculect nogai has no file with feature profile",
    ):
        validator._match_doculects_to_files()


def test__match_files_to_doculects_fails_with_less_doculects_than_files():
    validator = DoculectInventoryValidator(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES
        / "doculects_bad_less_doculects_than_files1.csv",
    )
    # this must not fail because all doculects correspond to files
    validator._match_doculects_to_files()

    with pytest.raises(
        DoculectInventoryValidatorError,
        match="Feature profile pashto has no match in file with doculects",
    ):
        validator._match_files_to_doculects()

    validator = DoculectInventoryValidator(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES
        / "doculects_bad_less_doculects_than_files2.csv",
    )
    # this must not fail because all doculects correspond to files
    validator._match_doculects_to_files()

    with pytest.raises(
        DoculectInventoryValidatorError,
        match='Feature profile pashto is not marked with "1" in file with doculects',
    ):
        validator._match_files_to_doculects()


def test_validate_passes_for_good_file():
    DoculectInventoryValidator(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_doculects=GOOD_FILE_WITH_DOCULECTS,
        file_with_genealogy_names=FILE_WITH_GENEALOGY_NAMES,
    ).validate()


def test_validate_fails_for_bad_files():
    for file in DIR_WITH_VALIDATORS_TEST_FILES.glob("doculects_bad*.csv"):
        print(f"\nTEST: Processing file {file.name}")
        with pytest.raises(DoculectInventoryValidatorError):
            # it will either fail at init or at validate
            validator = DoculectInventoryValidator(
                dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
                file_with_doculects=file,
            )
            validator.validate()


def test_validate_real_data():
    # Previous tests test the validator. Now test the real DATA using the validator.
    # Empty arguments mean that default (i.e. real) files/dirs will be used.
    validator = DoculectInventoryValidator()
    validator.validate()
