import pytest

from langworld_db_data.validators.feature_value_inventory_validator import *
from tests.paths import DIR_WITH_VALIDATORS_TEST_FILES

GOOD_FEATURES_FILE = DIR_WITH_VALIDATORS_TEST_FILES / 'features_OK.csv'
GOOD_LISTED_VALUES_FILE = DIR_WITH_VALIDATORS_TEST_FILES / 'features_listed_values_OK.csv'


def test___validate_features_fails_for_non_unique_feature_ids():
    validator = FeatureValueInventoryValidator(
        file_with_features=DIR_WITH_VALIDATORS_TEST_FILES / 'features_bad_non_unique_ids.csv',
        file_with_listed_values=GOOD_LISTED_VALUES_FILE
    )

    with pytest.raises(FeatureValueInventoryValidatorError) as e:
        validator.validate()

    assert 'Some feature IDs are not unique' in str(e)


def test___validate_features_fails_for_malformed_feature_ids():
    validator = FeatureValueInventoryValidator(
        file_with_features=DIR_WITH_VALIDATORS_TEST_FILES / 'features_bad_malformed_ids.csv',
        file_with_listed_values=GOOD_LISTED_VALUES_FILE
    )

    with pytest.raises(FeatureValueInventoryValidatorError) as e:
        validator.validate()

    assert 'Invalid feature ID foo' in str(e)


def test__validate_listed_values_fails_for_non_unique_ids():
    validator = FeatureValueInventoryValidator(
        file_with_features=GOOD_FEATURES_FILE,
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES / 'features_listed_values_bad_non_unique_ids.csv'
    )

    with pytest.raises(FeatureValueInventoryValidatorError) as e:
        validator.validate()

    assert 'Following value IDs are not unique: A-2-2, A-2-4' in str(e)


def test__validate_listed_values_fails_for_malformed_ids():
    validator = FeatureValueInventoryValidator(
        file_with_features=GOOD_FEATURES_FILE,
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES / 'features_listed_values_bad_malformed_ids.csv'
    )

    with pytest.raises(FeatureValueInventoryValidatorError) as e:
        validator.validate()

    assert 'Value ID foo does not start with feature ID' in str(e)

    validator = FeatureValueInventoryValidator(
        file_with_features=GOOD_FEATURES_FILE,
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES / 'features_listed_values_bad_malformed_ids2.csv'
    )

    with pytest.raises(FeatureValueInventoryValidatorError) as e:
        validator.validate()

    assert 'Value ID A-222 was not formed correctly from feature ID A-2' in str(e)


def test__validate_listed_values_fails_for_non_unique_value_names_within_one_feature():
    validator = FeatureValueInventoryValidator(
        file_with_features=GOOD_FEATURES_FILE,
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES / 'features_listed_values_bad_non_unique_name_en.csv'
    )

    with pytest.raises(FeatureValueInventoryValidatorError) as e:
        validator.validate()

    assert 'Duplicate value names found for feature A-1: Three' in str(e)

    validator = FeatureValueInventoryValidator(
        file_with_features=GOOD_FEATURES_FILE,
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES / 'features_listed_values_bad_non_unique_name_ru.csv'
    )

    with pytest.raises(FeatureValueInventoryValidatorError) as e:
        validator.validate()

    assert 'Duplicate value names found for feature A-1: Три' in str(e)


def test_validate_passes_for_good_files():
    validator = FeatureValueInventoryValidator(
        file_with_features=GOOD_FEATURES_FILE,
        file_with_listed_values=GOOD_LISTED_VALUES_FILE,
    )
    validator.validate()


def test_validate_real_data():
    # Previous tests test the validator. Now test the real DATA using the validator.
    # Empty arguments mean that default (i.e. real) files/dirs will be used.
    validator = FeatureValueInventoryValidator()
    validator.validate()
