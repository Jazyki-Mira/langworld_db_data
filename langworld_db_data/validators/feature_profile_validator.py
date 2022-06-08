from pathlib import Path
import re

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, FILE_WITH_LISTED_VALUES
from langworld_db_data.filetools.csv_xls import (
    check_csv_for_malformed_rows,
    check_csv_for_repetitions_in_column,
    read_csv,
    read_dict_from_2_csv_columns
)
from langworld_db_data.validators.exceptions import ValidatorError


class FeatureProfileValidatorError(ValidatorError):
    pass


class FeatureProfileValidator:
    def __init__(
            self,
            dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
            file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
            must_raise_exception_at_value_name_mismatch: bool = True,
    ):
        self.feature_profiles = sorted(list(dir_with_feature_profiles.glob('*.csv')))

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

    def validate(self):
        for feature_profile in self.feature_profiles:
            self._validate_one_file(feature_profile)

    def _validate_one_file(self, file: Path):
        # print(f'Checking feature profile {file.stem}')
        rows = read_csv(file, read_as='dicts')

        for i, row in enumerate(rows, start=1):
            if not row['feature_id']:
                raise FeatureProfileValidatorError(f'File {file.stem} does not contain feature ID in row {i + 1}')

            if row['value_type'] not in ('listed', 'custom', 'not_stated', 'explicit_gap', 'not_applicable'):
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


if __name__ == '__main__':
    FeatureProfileValidator().validate()
