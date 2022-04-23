from pathlib import Path
from typing import Optional

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, FILE_WITH_LISTED_VALUES
from langworld_db_data.filetools.csv_xls import read_csv, write_csv


class ListedValueAdderError(Exception):
    pass


class ListedValueAdder:
    def __init__(
        self,
        input_file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
        input_dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,

        # This is mainly for testing: there should be an option to give different paths.
        # In a default scenario, these paths will be the same, meaning the file will be updated in place.
        output_file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
        output_dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
    ):

        self.input_file_with_listed_values = input_file_with_listed_values
        self.input_feature_profiles = sorted(list(input_dir_with_feature_profiles.glob('*.csv')))

        self.output_file_with_listed_values = output_file_with_listed_values
        self.output_dir_with_feature_profiles = output_dir_with_feature_profiles

    def add_listed_value(
        self,
        feature_id: str,
        new_value_en: str,
        new_value_ru: str,
        custom_values_to_rename: Optional[list[str]] = None
    ):
        """Adds listed value to the inventory and marks matching custom value
        in feature profiles as listed.  If one or more custom values
        in feature profiles were formulated differently but now
        have to be renamed to be the new `listed` value, these custom values
        can be passed as a list.
        """
        if not (feature_id and new_value_en and new_value_ru):
            raise ListedValueAdderError('None of the passed strings can be empty')

        id_of_new_value = self._add_to_inventory_of_listed_values(
            feature_id=feature_id, new_value_en=new_value_en, new_value_ru=new_value_ru
        )
        self._mark_value_as_listed_in_feature_profiles(
            feature_id=feature_id,
            new_value_id=id_of_new_value,
            new_value_ru=new_value_ru,
            custom_values_to_rename=custom_values_to_rename
        )

    def _add_to_inventory_of_listed_values(
        self,
        feature_id: str,
        new_value_en: str,
        new_value_ru: str,
    ):
        rows = read_csv(self.input_file_with_listed_values, read_as='dicts')

        if not [r for r in rows if r['feature_id'] == feature_id]:
            raise ListedValueAdderError(f'Feature ID {feature_id} not found')

        index_of_last_row_for_given_feature = 0
        id_of_new_value = ''

        for i, row in enumerate(rows):
            if row['feature_id'] == feature_id:
                if row['en'] == new_value_en or row['ru'] == new_value_ru:
                    raise ListedValueAdderError(
                        f'Row {row} already contains value you are trying to add'
                    )

                # Keep updating those with each row.
                # This means that at the last row of the feature they will reach the required values.
                index_of_last_row_for_given_feature = i
                last_digit_of_value_id = int(row['id'].split('-')[-1])
                id_of_new_value = feature_id + '-' + str(last_digit_of_value_id + 1)

        row_with_new_value = [{
            'id': id_of_new_value, 'feature_id': feature_id,
            'en': new_value_en[0].upper() + new_value_en[1:],
            'ru': new_value_ru[0].upper() + new_value_ru[1:]
        }]

        rows_with_new_value_inserted = (
            rows[:index_of_last_row_for_given_feature + 1]
            + row_with_new_value
            + rows[index_of_last_row_for_given_feature + 1:]
        )

        write_csv(
            rows_with_new_value_inserted,
            path_to_file=self.output_file_with_listed_values,
            overwrite=True,
            delimiter=','
        )

        return id_of_new_value

    def _mark_value_as_listed_in_feature_profiles(
        self,
        feature_id: str,
        new_value_id: str,
        new_value_ru: str,
        custom_values_to_rename: Optional[list[str]] = None
    ):

        for file in self.input_feature_profiles:
            is_changed = False
            rows = read_csv(file, read_as='dicts')

            for i, row in enumerate(rows):
                if (
                        row['feature_id'] == feature_id and
                        row['value_type'] == 'custom'
                ):
                    value_ru = row['value_ru'].strip()
                    value_ru = value_ru[:-1] if value_ru.endswith('.') else value_ru

                    if value_ru.lower() not in [v.lower() for v in
                        [new_value_ru] + custom_values_to_rename
                    ]:
                        break

                    print(f'{file.name}: changing row {i + 2} (feature {feature_id}). '
                          f'Custom value <{row["value_ru"]}> will become listed value '
                          f'<{new_value_ru}> ({new_value_id})')
                    row['value_type'] = 'listed'
                    row['value_id'] = new_value_id
                    row['value_ru'] = new_value_ru
                    is_changed = True
                    break

            if is_changed:
                write_csv(
                    rows, path_to_file=self.output_dir_with_feature_profiles / file.name,
                    overwrite=True, delimiter=','
                )


if __name__ == '__main__':
    pass
