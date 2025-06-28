"""Tests for the HTML validator."""

from langworld_db_data.validators.html_validator import HTMLValidator
from tests.paths import DIR_WITH_VALIDATORS_TEST_FILES


def test_validate_with_good_files():
    validator = HTMLValidator(
        input_file_with_features=DIR_WITH_VALIDATORS_TEST_FILES
        / "features_for_html_validator.csv",
        input_file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES
        / "features_listed_values_for_html_validator.csv",
    )
    validator.validate()
