from collections import Counter
from pathlib import Path
import re

from langworld_db_data.constants.paths import (
    FILE_WITH_LISTED_VALUES,
    FILE_WITH_NAMES_OF_FEATURES,
)
from langworld_db_data.filetools.csv_xls import read_csv, read_dict_from_2_csv_columns
from langworld_db_data.validators.exceptions import ValidatorError


class FeatureValueInventoryValidatorError(ValidatorError):
    pass


class FeatureValueInventoryValidator:
    def __init__(
        self,
        file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
        file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
    ):
        self.feature_ids = [row['id'] for row in read_csv(file_with_features, read_as='dicts')]

        self.rows_with_listed_values = read_csv(file_with_listed_values, read_as='dicts')

    def validate(self):
        print('\nChecking inventories of features and listed values')
        self._validate_features()
        self._validate_listed_values()

    def _validate_features(self):
        if len(self.feature_ids) > len(set(self.feature_ids)):
            raise FeatureValueInventoryValidatorError('Some feature IDs are not unique')

        for feature_id in self.feature_ids:
            if not re.match(r'[A-Z]-\d+', feature_id):
                raise FeatureValueInventoryValidatorError(f'Invalid feature ID {feature_id}')

        print(f'Feature IDs OK')

    def _validate_listed_values(self):
        value_ids = [row['id'] for row in self.rows_with_listed_values]

        counter = Counter(value_ids)
        duplicate_ids = [item for item in counter if counter[item] > 1]

        if duplicate_ids:
            raise FeatureValueInventoryValidatorError(
                f'Following value IDs are not unique: {", ".join(duplicate_ids)}'
            )

        print('OK: all value IDs are unique')

        feature_id_for_value_id = {
            row['id']: row['feature_id'] for row in self.rows_with_listed_values
        }

        for value_id in feature_id_for_value_id:
            if not value_id.startswith(feature_id_for_value_id[value_id]):
                raise FeatureValueInventoryValidatorError(
                    f'Value ID {value_id} does not start with feature ID {feature_id_for_value_id[value_id]}'
                )
            if not re.match(rf'{feature_id_for_value_id[value_id]}-\d+', value_id):
                raise FeatureValueInventoryValidatorError(
                    f'Value ID {value_id} was not formed correctly from feature ID {feature_id_for_value_id[value_id]}'
                )

        print(f'OK: all value IDs are derived from feature ID')


if __name__ == '__main__':
    FeatureValueInventoryValidator().validate()
