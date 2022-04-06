import pytest
from langworld_db_data.validators.doculect_inventory_validator import *
from tests.paths import DIR_WITH_TEST_FEATURE_PROFILES, DIR_WITH_VALIDATORS_TEST_FILES


validator_with_good_files = DoculectInventoryValidator(
    dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
    file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES / 'doculects_OK.csv',
)


def test_init_fails_with_file_with_non_unique_doculect_ids():
    with pytest.raises(ValidatorError) as e:
        _ = DoculectInventoryValidator(
            dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
            file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES / 'doculects_bad_non_unique_doculects.csv'
        )
    assert 'Some IDs in list of doculects are not unique' in str(e)


def test__match_doculects_to_files_fails_with_more_doculects_than_files():
    validator = DoculectInventoryValidator(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES / 'doculects_bad_more_doculects_than_files.csv'
    )
    validator._match_files_to_doculects()  # this must not fail because all files correspond to doculects

    with pytest.raises(ValidatorError) as e:
        validator._match_doculects_to_files()

    assert 'Doculect nogai has no file with feature profile' in str(e)


def test__match_files_to_doculects_fails_with_less_doculects_than_files():
    validator = DoculectInventoryValidator(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES / 'doculects_bad_less_doculects_than_files1.csv'
    )
    validator._match_doculects_to_files()  # this must not fail because all doculects correspond to files

    with pytest.raises(ValidatorError) as e:
        validator._match_files_to_doculects()

    assert 'Feature profile pashto has no match in file with doculects' in str(e)

    validator = DoculectInventoryValidator(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_doculects=DIR_WITH_VALIDATORS_TEST_FILES / 'doculects_bad_less_doculects_than_files2.csv'
    )
    validator._match_doculects_to_files()  # this must not fail because all doculects correspond to files

    with pytest.raises(ValidatorError) as e:
        validator._match_files_to_doculects()

    assert 'Feature profile pashto is not marked with "1" in file with doculects' in str(e)


def test_validate_passes_for_good_file():
    validator_with_good_files.validate()


def test_validate_fails_for_bad_files():
    for file in DIR_WITH_VALIDATORS_TEST_FILES.glob('doculects_bad*.csv'):
        print(f'\nTEST: Processing file {file.name}')
        with pytest.raises(ValidatorError):
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
