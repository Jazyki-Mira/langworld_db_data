import pyperclip

from langworld_db_data.constants.paths import CLDF_DIR
from langworld_db_data.filetools.csv_xls import read_csv


def get_value_for_doculect_and_feature(doculect_id: str, feature_id: str) -> dict:
    """A helper function to get value for given feature in given doculect.
    Prints and returns found value type, ID and text. **Copies value text to clipboard**.

    Can be handy for renaming custom/listed values
    when adding/unifying listed values.

    Note that this function reads from the **CLDF dataset**,
    not from CSV feature profiles.

    If copying to clipboard does not work on Ubuntu, run
    `sudo apt install xclip` first.
    """

    values_file = CLDF_DIR / 'values.csv'
    for row in read_csv(values_file, read_as='dicts'):
        if row['Language_ID'] == doculect_id and row['Parameter_ID'] == feature_id:
            value_type = 'listed' if row['Code_ID'] else 'custom'
            data = {'value_type': value_type, 'value_id': row['Code_ID'], 'value': row['Value_RU']}

            print('Value type: ', data['value_type'])
            if data['value_type'] == 'listed':
                print(data['value_id'])
            print(data['value'])

            pyperclip.copy(data['value'])
            print('Value text copied to clipboard')

            return data

    raise KeyError(f'{feature_id=} not found for {doculect_id=}')


if __name__ == '__main__':
    pass
