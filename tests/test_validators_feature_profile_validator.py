import pytest

from langworld_db_data.validators.feature_profile_validator import FeatureProfileValidator, FeatureProfileValidatorError
from tests.paths import DIR_WITH_TEST_FEATURE_PROFILES, DIR_WITH_VALIDATORS_TEST_FILES

DIR_WITH_BAD_PROFILES = DIR_WITH_TEST_FEATURE_PROFILES / 'must_fail'
DIR_WITH_PROFILES_BREACHING_RULES_FOR_NOT_APPLICABLE = (
    DIR_WITH_TEST_FEATURE_PROFILES / 'must_fail_if_breach_of_rules_for_not_applicable_set_to_raise_exception')


@pytest.fixture(scope='function')
def test_validator():
    return FeatureProfileValidator(
        dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES,
        file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES / 'features_listed_values_OK.csv',
        file_with_rules_for_not_applicable_value_type=(DIR_WITH_VALIDATORS_TEST_FILES /
                                                       'features_not_applicable_rules.yaml'),
        must_raise_exception_at_value_name_mismatch=True,
        must_raise_exception_at_not_applicable_rule_breach=False,
    )


def test__init(test_validator):
    assert len(test_validator.feature_profiles) == len(list(DIR_WITH_TEST_FEATURE_PROFILES.glob('*.csv')))

    assert test_validator.value_ru_for_value_id['A-3-5'] == 'Передний и непередний'


@pytest.mark.parametrize('file_stem, expected_error_message', [
    ('corsican_no_feature_ID', 'does not contain feature ID in row 4'),
    ('corsican_invalid_value_type', 'contains invalid value type in row 4'),
    ('corsican_custom_and_value_ID', 'must not contain value ID A-3-4 in row 4'),
    ('corsican_custom_no_text', 'does not contain value text in row 4'),
    ('corsican_not_stated_with_text', 'must not contain value ID or value text in row 4'),
    ('corsican_explicit_gap_with_value_ID', 'must not contain value ID or value text in row 4'),
    ('corsican_invalid_value_ID', 'contains invalid value ID A-34 in row 4'),
    ('corsican_non_matching_listed_value', 'value Передний и задний for value ID A-3-4 in row 4 does not match'),
])
def test__validate_one_file_fails_with_bad_files(test_validator, file_stem, expected_error_message):
    with pytest.raises(FeatureProfileValidatorError) as e:
        test_validator._validate_one_file(DIR_WITH_BAD_PROFILES / f'{file_stem}.csv')

    assert expected_error_message in str(e)


def test__validate_one_file_prints_message_with_must_raise_exception_at_value_name_mismatch_set_to_false(
        capsys, test_validator):
    test_validator.must_raise_exception_at_value_name_mismatch = False
    test_validator._validate_one_file(DIR_WITH_BAD_PROFILES / 'corsican_non_matching_listed_value.csv')
    stdout = capsys.readouterr()
    assert 'value Передний и задний for value ID A-3-4 in row 4 does not match' in str(stdout)


def test_validate_fails_with_bad_data():
    with pytest.raises(FeatureProfileValidatorError):
        FeatureProfileValidator(dir_with_feature_profiles=DIR_WITH_BAD_PROFILES).validate()


def test__validate_one_file_prints_message_for_files_breaching_rules_for_not_applicable_with_flag_set_to_false(
        capsys, test_validator):
    test_validator.must_raise_exception_at_not_applicable_rule_breach = False

    for file_name in ('agul', 'catalan'):
        test_validator._validate_one_file(DIR_WITH_PROFILES_BREACHING_RULES_FOR_NOT_APPLICABLE / f'{file_name}.csv')
        stdout = capsys.readouterr()
        assert 'Instead, it has value "Этого тут быть не должно"' in str(stdout)


def test_validate_fails_with_profiles_that_breach_rules_for_not_applicable_with_flag_set_to_true():

    with pytest.raises(FeatureProfileValidatorError) as e:
        FeatureProfileValidator(
            dir_with_feature_profiles=DIR_WITH_PROFILES_BREACHING_RULES_FOR_NOT_APPLICABLE,
            file_with_listed_values=DIR_WITH_VALIDATORS_TEST_FILES / 'features_listed_values_OK.csv',
            must_raise_exception_at_not_applicable_rule_breach=True,
        ).validate()

    assert "breaches of rules for 'not_applicable' value type" in str(e)


def test_validate_real_data():
    FeatureProfileValidator(must_raise_exception_at_value_name_mismatch=True).validate()
