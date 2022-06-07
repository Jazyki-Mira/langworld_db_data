from pathlib import Path
import pyperclip

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR
from langworld_db_data.filetools.csv_xls import read_csv


def get_feature_profile_as_dict(
    doculect_id: str,
    dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
) -> dict[str, dict[str, str]]:
    """
    Reads feature profile and returns dictionary:
    {`feature ID`: {'feature_name_ru': ...,
    'value_type': ..., 'value_id': ...,
    'value_ru': ..., 'comment_ru': ..., 'comment_en': ...}
    """
    file = dir_with_feature_profiles / f'{doculect_id}.csv'

    feature_id_to_row_dict = {}

    for row in read_csv(file, read_as='dicts'):
        feature_id_to_row_dict[row['feature_id']] = {
            key: row[key] for key in row.keys() if key != 'feature_id'
        }

    return feature_id_to_row_dict


def get_value_for_doculect_and_feature(
        doculect_id: str,
        feature_id: str,
        dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
        copy_to_clipboard: bool = True,
        verbose: bool = True
) -> dict:
    """A helper function to get value for given feature in given doculect.
    Prints and returns found value type, ID and text.
    **Copies value text to clipboard** (by default).

    Can be handy when renaming custom/listed values
    when adding/unifying listed values.

    If copying to clipboard does not work on Ubuntu, run
    `sudo apt install xclip` first.
    """

    try:
        loaded_data_for_feature = get_feature_profile_as_dict(
            doculect_id=doculect_id,
            dir_with_feature_profiles=dir_with_feature_profiles,
        )[feature_id]
    except KeyError:
        raise KeyError(f'{feature_id=} not found for {doculect_id=}')

    data_to_return = {
        key: loaded_data_for_feature[key] for key in ('value_type', 'value_id', 'value_ru', 'comment_ru')
    }

    if verbose:
        print(f'{doculect_id=}, {feature_id=}\n')
        for key in data_to_return.keys():
            key_for_print = key.replace("_ru", "").replace("_", " ").capitalize().replace('id', 'ID')
            if data_to_return[key]:
                print(f'{key_for_print}: {data_to_return[key]}')
            else:
                print(f'{key_for_print} is empty')

    # sometimes a custom value can be written in comment while value itself is left empty
    text_to_copy = data_to_return['value_ru'] if data_to_return['value_ru'] else data_to_return['comment_ru']
    if copy_to_clipboard and text_to_copy:
        pyperclip.copy(text_to_copy)
        print('\nValue (or comment for empty value) copied to clipboard')

    return data_to_return


if __name__ == '__main__':
    pass
