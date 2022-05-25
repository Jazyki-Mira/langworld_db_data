import pyperclip

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR
from langworld_db_data.filetools.csv_xls import read_csv


def get_value_for_doculect_and_feature(
        doculect_id: str, feature_id: str, copy_to_clipboard: bool = True
) -> dict:
    """A helper function to get value for given feature in given doculect.
    Prints and returns found value type, ID and text.
    **Copies value text to clipboard** (by default).

    Can be handy when renaming custom/listed values
    when adding/unifying listed values.

    If copying to clipboard does not work on Ubuntu, run
    `sudo apt install xclip` first.
    """

    file = FEATURE_PROFILES_DIR / f'{doculect_id}.csv'
    if not file.exists():
        raise FileNotFoundError(f'Feature profile {doculect_id}.csv does not exist')

    print(f'{doculect_id=}, {feature_id=}\n')

    for row in read_csv(file, read_as='dicts'):
        if row['feature_id'] == feature_id:
            data = {key: row[key] for key in ('value_type', 'value_id', 'value_ru', 'comment_ru')}

            for attr in ('value_type', 'value_id', 'value_ru', 'comment_ru'):
                attr_for_print = attr.replace("_ru", "").replace("_", " ").capitalize().replace('id', 'ID')
                if data[attr]:
                    print(f'{attr_for_print}: {data[attr]}')
                else:
                    print(f'{attr_for_print} is empty')

            # sometimes a custom value can be written in comment while value itself is left empty
            text_to_copy = data['value_ru'] if data['value_ru'] else data['comment_ru']
            if copy_to_clipboard and text_to_copy:
                pyperclip.copy(text_to_copy)
                print('\nValue (or comment for empty value) copied to clipboard')

            return data

    raise KeyError(f'{feature_id=} not found for {doculect_id=}')


if __name__ == '__main__':
    pass
