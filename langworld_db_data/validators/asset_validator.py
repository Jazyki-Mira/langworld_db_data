from collections import Counter
from pathlib import Path

from langworld_db_data.constants.paths import ASSETS_DIR, FILE_WITH_DOCULECTS
from langworld_db_data.filetools.csv_xls import read_csv
from langworld_db_data.validators.exceptions import ValidatorError


class AssetValidatorError(ValidatorError):
    pass


class AssetValidator:
    def __init__(
        self,
        file_with_doculects: Path = FILE_WITH_DOCULECTS,
        file_with_encyclopedia_maps: Path = ASSETS_DIR / 'encyclopedia_maps.csv',
        file_matching_maps_to_doculects: Path = ASSETS_DIR / 'encyclopedia_map_to_doculect.csv'
    ):
        self.file_with_doculects = file_with_doculects
        self.file_with_encyclopedia_maps = file_with_encyclopedia_maps
        self.file_matching_maps_to_doculects = file_matching_maps_to_doculects

    def validate(self):
        print('\nValidating files describing assets')
        self._validate_file_matching_maps_to_doculects()

    def _validate_file_matching_maps_to_doculects(self):
        print('Checking file mapping encyclopedia maps to doculects')

        plain_rows_as_tuples = [
            (row[0], row[1]) for row in read_csv(self.file_matching_maps_to_doculects, read_as='plain_rows')
        ]
        counter = Counter(plain_rows_as_tuples)
        for key in counter:
            if counter[key] > 1:
                raise AssetValidatorError(
                    f'File {self.file_matching_maps_to_doculects.name} has a repeating row: {key} ({counter[key]})'
                )
        print('OK: No repeating rows found')

        doculect_ids = [row['id'] for row in read_csv(self.file_with_doculects, read_as='dicts')]
        map_ids = [row['id'] for row in read_csv(self.file_with_encyclopedia_maps, read_as='dicts')]

        rows = read_csv(self.file_matching_maps_to_doculects, read_as='dicts')

        for i, row in enumerate(rows, start=2):
            if row['encyclopedia_map_id'] not in map_ids:
                raise AssetValidatorError(
                    f'Row {i} in file {self.file_matching_maps_to_doculects.name}: '
                    f'Map ID {row["encyclopedia_map_id"]} not found in file {self.file_with_encyclopedia_maps.name}'
                )
            if row['doculect_id'] not in doculect_ids:
                raise AssetValidatorError(
                    f'Row {i} in file {self.file_matching_maps_to_doculects.name}: '
                    f'Doculect ID {row["doculect_id"]} not found in file {self.file_with_doculects.name}'
                )
        print(f'OK: IDs of encyclopedia maps and doculects match IDs in respective files')


if __name__ == '__main__':
    AssetValidator().validate()
