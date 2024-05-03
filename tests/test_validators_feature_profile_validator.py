import pytest

from langworld_db_data.validators.feature_profile_validator import (
    FeatureProfileValidator,
    FeatureProfileValidatorError,
)
from tests.paths import DIR_WITH_TEST_FEATURE_PROFILES, DIR_WITH_VALIDATORS_TEST_FILES

DIR_WITH_BAD_PROFILES = DIR_WITH_TEST_FEATURE_PROFILES / "must_fail"
DIR_WITH_PROFILES_BREACHING_RULES_FOR_NOT_APPLICABLE = (
    DIR_WITH_TEST_FEATURE_PROFILES
    / "must_fail_if_breach_of_rules_for_not_applicable_set_to_raise_exception"
)


@pytest.fixture(scope="function")
def test_validator():
    return FeatureProfileValidator(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_features=DIR_WITH_VALIDATORS_TEST_FILES / "features_OK.csv",
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES / "features_listed_values_OK.csv",
    )


def test__init(test_validator):
    assert len(test_validator.feature_profiles) == len(
        list(DIR_WITH_TEST_FEATURE_PROFILES.glob("*.csv"))
    )

    assert test_validator.value_ru_for_value_id["A-3-5"] == "Передний и непередний"


@pytest.mark.parametrize(
    "file_stem, expected_error_message",
    [
        ("corsican_no_feature_ID", "does not contain feature ID in row 4"),
        ("corsican_invalid_value_type", "contains invalid value type in row 4"),
        ("corsican_custom_and_value_ID", "must not contain value ID A-3-4 in row 4"),
        ("corsican_custom_no_text", "does not contain value text in row 4"),
        (
            "corsican_not_stated_with_text",
            "must not contain value ID or value text in row 4",
        ),
        (
            "corsican_explicit_gap_with_value_ID",
            "must not contain value ID or value text in row 4",
        ),
        ("corsican_invalid_value_ID", "contains invalid value ID A-34 in row 4"),
        (
            "corsican_non_matching_listed_value",
            "value Передний и задний for value ID A-3-4 in row 4 does not match",
        ),
        (
            "ukrainian_invalid_value_ID_in_multiselect",
            "contains invalid value ID K-143 in row 108",
        ),
        (
            "ukrainian_no_correspondence_in_multiselect",
            "value По лицу for value ID K-14-2 in row 108 does not match",
        ),
    ],
)
def test__validate_one_file_fails_with_bad_files(
    test_validator, file_stem, expected_error_message
):
    with pytest.raises(FeatureProfileValidatorError, match=expected_error_message):
        test_validator.validate_one_file(DIR_WITH_BAD_PROFILES / f"{file_stem}.csv")


def test__validate_one_file_prints_message_with_must_throw_error_at_feature_or_value_name_mismatch_set_to_false(  # noqa E501
    capsys, test_validator
):
    test_validator.must_throw_error_at_feature_or_value_name_mismatch = False
    test_validator.validate_one_file(
        DIR_WITH_BAD_PROFILES / "corsican_non_matching_listed_value.csv"
    )
    stdout = capsys.readouterr()
    assert "value Передний и задний for value ID A-3-4 in row 4 does not match" in str(stdout)


def test_validate_fails_with_bad_data():
    # this test is very general and will pass even if just one error is caught,
    # not all of them
    with pytest.raises(FeatureProfileValidatorError):
        FeatureProfileValidator(dir_with_feature_profiles=DIR_WITH_BAD_PROFILES).validate()


@pytest.mark.parametrize(
    "file_name, error_msg",
    [("agul", '"Этого тут быть не должно" of type `custom`'), ("catalan", "of type `not_stated`")],
)
def test__validate_one_file_prints_message_for_files_breaching_rules_for_not_applicable_with_flag_set_to_false(  # noqa E501
    capsys, test_validator, file_name, error_msg
):
    test_validator.must_throw_error_at_not_applicable_rule_breach = False

    test_validator.validate_one_file(
        DIR_WITH_PROFILES_BREACHING_RULES_FOR_NOT_APPLICABLE / f"{file_name}.csv"
    )
    stdout = capsys.readouterr()
    assert error_msg in str(stdout)


def test_validate_fails_with_profiles_that_breach_rules_for_not_applicable_with_flag_set_to_true():  # noqa E501
    with pytest.raises(FeatureProfileValidatorError, match="However, "):
        FeatureProfileValidator(
            dir_with_feature_profiles=DIR_WITH_PROFILES_BREACHING_RULES_FOR_NOT_APPLICABLE,
            file_with_features=DIR_WITH_VALIDATORS_TEST_FILES / "features_OK.csv",
            file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES
            / "features_listed_values_OK.csv",
            must_throw_error_at_not_applicable_rule_breach=True,
        ).validate()


def test_validate_real_data():
    FeatureProfileValidator().validate()
