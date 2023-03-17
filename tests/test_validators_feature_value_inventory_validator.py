import pytest

from langworld_db_data.validators.feature_value_inventory_validator import (
    FeatureValueInventoryValidator,
    FeatureValueInventoryValidatorError,
)
from tests.paths import DIR_WITH_VALIDATORS_TEST_FILES

GOOD_FEATURES_FILE = DIR_WITH_VALIDATORS_TEST_FILES / "features_OK.csv"
GOOD_LISTED_VALUES_FILE = (
    DIR_WITH_VALIDATORS_TEST_FILES / "features_listed_values_OK.csv"
)


@pytest.mark.parametrize(
    "file_name, expected_error_message",
    [
        (
            "features_listed_values_bad_non_unique_ids.csv",
            "repeating values in column <id>: A-2-2, A-2-4",
        ),
        ("features_bad_non_unique_ids.csv", "repeating values in column <id>: A-2"),
    ],
)
def test__init__fails_for_non_unique_feature_ids(file_name, expected_error_message):
    with pytest.raises(ValueError, match=expected_error_message):
        FeatureValueInventoryValidator(
            file_with_features=DIR_WITH_VALIDATORS_TEST_FILES / file_name,
            file_with_listed_values=GOOD_LISTED_VALUES_FILE,
        )


def test___validate_feature_ids_fails_for_malformed_feature_ids():
    validator = FeatureValueInventoryValidator(
        file_with_features=DIR_WITH_VALIDATORS_TEST_FILES
        / "features_bad_malformed_ids.csv",
        file_with_listed_values=GOOD_LISTED_VALUES_FILE,
    )

    with pytest.raises(
        FeatureValueInventoryValidatorError, match="Invalid feature ID foo"
    ):
        validator.validate()


def test__validate_listed_values_fails_for_malformed_ids():
    validator = FeatureValueInventoryValidator(
        file_with_features=GOOD_FEATURES_FILE,
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES
        / "features_listed_values_bad_malformed_ids.csv",
    )

    with pytest.raises(
        FeatureValueInventoryValidatorError,
        match="Value ID foo does not start with feature ID",
    ):
        validator.validate()

    validator = FeatureValueInventoryValidator(
        file_with_features=GOOD_FEATURES_FILE,
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES
        / "features_listed_values_bad_malformed_ids2.csv",
    )

    with pytest.raises(
        FeatureValueInventoryValidatorError,
        match="Value ID A-222 was not formed correctly from feature ID A-2",
    ):
        validator.validate()


@pytest.mark.parametrize(
    "file_name, error_message",
    [
        (
            "features_listed_values_bad_non_unique_name_en.csv",
            "Duplicate value names found for feature A-1: Three",
        ),
        (
            "features_listed_values_bad_non_unique_name_ru.csv",
            "Duplicate value names found for feature A-1: Три",
        ),
    ],
)
def test__validate_listed_values_fails_for_non_unique_value_names_within_one_feature(
    file_name, error_message
):
    validator = FeatureValueInventoryValidator(
        file_with_features=GOOD_FEATURES_FILE,
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES / file_name,
    )

    with pytest.raises(FeatureValueInventoryValidatorError, match=error_message):
        validator.validate()


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
