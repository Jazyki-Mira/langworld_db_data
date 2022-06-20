from pathlib import Path
import re

from langworld_db_data.constants.paths import (
    FEATURE_PROFILES_DIR,
    FILE_WITH_LISTED_VALUES,
    FILE_WITH_NOT_APPLICABLE_RULES,
    FILE_WITH_VALUE_TYPES,
)
from langworld_db_data.featureprofiletools.feature_profile_reader import FeatureProfileReader
from langworld_db_data.filetools.csv_xls import (
    check_csv_for_malformed_rows,
    check_csv_for_repetitions_in_column,
    read_csv,
    read_dict_from_2_csv_columns
)
from langworld_db_data.filetools.json_toml_yaml import read_json_toml_yaml
from langworld_db_data.validators.exceptions import ValidatorError


class FeatureProfileValidatorError(ValidatorError):
    pass


class FeatureProfileValidator:
    def __init__(
            self,
            dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
            file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
            file_with_rules_for_not_applicable_value_type: Path = FILE_WITH_NOT_APPLICABLE_RULES,
            file_with_value_types: Path = FILE_WITH_VALUE_TYPES,
            must_raise_exception_at_value_name_mismatch: bool = True,
            must_raise_exception_at_not_applicable_rule_breach: bool = False,
    ):
        self.feature_profiles = sorted(list(dir_with_feature_profiles.glob('*.csv')))
        self.reader = FeatureProfileReader()

        self.rules_for_not_applicable_value_type = read_json_toml_yaml(file_with_rules_for_not_applicable_value_type)
        self.valid_value_types = [row['id'] for row in read_csv(file_with_value_types, read_as='dicts')]

        for file in self.feature_profiles:
            check_csv_for_malformed_rows(file)
            for column_name in ('feature_id', 'feature_name_ru'):
                check_csv_for_repetitions_in_column(file, column_name=column_name)

        self.value_ru_for_value_id = read_dict_from_2_csv_columns(
            file_with_listed_values,
            key_col='id',
            val_col='ru',
        )

        self.must_raise_exception_at_value_name_mismatch = must_raise_exception_at_value_name_mismatch
        self.must_raise_exception_at_not_applicable_rule_breach = must_raise_exception_at_not_applicable_rule_breach

    def validate(self):
        print(f'\nChecking feature profiles ({len(self.feature_profiles)} files)')
        for feature_profile in self.feature_profiles:
            self._validate_one_file(feature_profile)

    def _validate_one_file(self, file: Path):
        # print(f'Checking feature profile {file.stem}')
        rows = read_csv(file, read_as='dicts')

        for i, row in enumerate(rows, start=1):
            if not row['feature_id']:
                raise FeatureProfileValidatorError(f'File {file.stem} does not contain feature ID in row {i + 1}')

            if row['value_type'] not in self.valid_value_types:
                raise FeatureProfileValidatorError(f'File {file.stem} contains invalid value type in row {i + 1}')

            if row['value_type'] == 'custom':
                if row['value_id']:
                    raise FeatureProfileValidatorError(
                        f'File {file.stem} must not contain value ID {row["value_id"]} in row {i + 1} '
                        f'or value type must be "listed"'
                    )
                if not row['value_ru']:
                    raise FeatureProfileValidatorError(
                        f'File {file.stem} does not contain value text in row {i + 1}'
                    )

            elif row['value_type'] in ('not_stated', 'not_applicable', 'explicit_gap'):
                if row['value_id'] or row['value_ru']:
                    raise FeatureProfileValidatorError(
                        f'File {file.stem} must not contain value ID or value text in row {i + 1} '
                        f'or value type must be different'
                    )

            elif row['value_type'] == 'listed':
                if not re.match(rf"{row['feature_id']}-\d+", row['value_id']):
                    raise FeatureProfileValidatorError(
                        f'File {file.stem} contains invalid value ID {row["value_id"]} in row {i + 1}'
                    )

                if row['value_ru'] != self.value_ru_for_value_id[row['value_id']]:
                    message = (
                        f'File {file.stem}, row {i + 1}: value {row["value_ru"]} for value ID {row["value_id"]} '
                        f'in row {i + 1} does not match name of this value in inventory '
                        f'(value ID {row["value_id"]} should be {self.value_ru_for_value_id[row["value_id"]]})'
                    )
                    if self.must_raise_exception_at_value_name_mismatch:
                        raise FeatureProfileValidatorError(message)
                    else:
                        print(message)

        breaches_of_rules_for_not_applicable = []
        data_from_profile = self.reader.read_feature_profile_as_dict_from_file(file)
        # TODO I can refactor the code above (that handles rows) to work with this dictionary

        rules = self.rules_for_not_applicable_value_type
        for feature_id in rules:

            # noinspection PyTypeChecker
            if data_from_profile[feature_id].value_id == rules[feature_id]['trigger']:

                # noinspection PyTypeChecker
                for id_of_feature_that_must_be_not_applicable in rules[feature_id]['features_to_get_not_applicable']:

                    if data_from_profile[id_of_feature_that_must_be_not_applicable].value_type != 'not_applicable':

                        error_message = (
                                f'{file.stem.capitalize()}: Feature {feature_id} '
                                f'"{data_from_profile[feature_id].feature_name_ru}" has value ID '
                                f'{data_from_profile[feature_id].value_id} '
                                f'"{data_from_profile[feature_id].value_ru}" => feature ID '
                                f"{id_of_feature_that_must_be_not_applicable} must have value type 'not_applicable'. "
                                f'Instead, it has value '
                                f'"{data_from_profile[id_of_feature_that_must_be_not_applicable].value_ru}" (value type'
                                f': {data_from_profile[id_of_feature_that_must_be_not_applicable].value_type})'
                        )
                        print(error_message)
                        breaches_of_rules_for_not_applicable.append(error_message)

        if breaches_of_rules_for_not_applicable and self.must_raise_exception_at_not_applicable_rule_breach:
            raise FeatureProfileValidatorError(
                f"File {file.name}: found {len(breaches_of_rules_for_not_applicable)} breaches of rules "
                f"for 'not_applicable' value type."
            )


if __name__ == '__main__':
    FeatureProfileValidator().validate()
