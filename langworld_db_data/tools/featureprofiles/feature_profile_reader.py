from pathlib import Path

import pyperclip

from langworld_db_data.constants.literals import (
    KEY_FOR_FEATURE_ID,
    KEY_FOR_RUSSIAN_COMMENT,
    KEY_FOR_RUSSIAN_NAME_OF_VALUE,
    KEY_FOR_VALUE_ID,
    KEY_FOR_VALUE_TYPE,
)
from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR
from langworld_db_data.tools.featureprofiles.data_structures import (
    ValueForFeatureProfileDictionary,
)
from langworld_db_data.tools.files.csv_xls import read_dicts_from_csv


class FeatureProfileReader:
    def read_feature_profile_as_dict_from_doculect_id(
        self,
        doculect_id: str,
        dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
    ) -> dict[str, ValueForFeatureProfileDictionary]:
        """
        Accepts Doculect ID and directory with feature profiles.

        Reads feature profile and returns dictionary:
        Keys are feature IDs, values are `ValueForFeatureProfileDictionary` objects
        with the rest of the columns for the respective row.
        """
        return self.read_feature_profile_as_dict_from_file(
            dir_with_feature_profiles / f"{doculect_id}.csv"
        )

    @staticmethod
    def read_feature_profile_as_dict_from_file(
        file: Path,
    ) -> dict[str, ValueForFeatureProfileDictionary]:
        """
        Accepts path to feature profile.

        Reads feature profile and returns dictionary:
        Keys are feature IDs, values are `ValueForFeatureProfileDictionary` objects
        with the rest of the columns for the respective row.
        """
        feature_id_to_row_dict = {}

        for i, row in enumerate(read_dicts_from_csv(file), start=1):
            if not row[KEY_FOR_FEATURE_ID]:
                raise ValueError(f"File {file.stem} does not contain feature ID in row {i + 1}")
            relevant_columns = {key: row[key] for key in row if key != KEY_FOR_FEATURE_ID}
            feature_id_to_row_dict[row[KEY_FOR_FEATURE_ID]] = ValueForFeatureProfileDictionary(
                **relevant_columns
            )

        return feature_id_to_row_dict

    def read_value_for_doculect_and_feature(
        self,
        doculect_id: str,
        feature_id: str,
        dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
        copy_to_clipboard: bool = True,
        verbose: bool = True,
    ) -> dict[str, str]:
        """A helper function to get value for given feature in given doculect.
        Prints and returns found value type, ID, value text, and comment.
        **Copies value text to clipboard** (by default).

        Can be handy when renaming custom/listed values
        when adding/unifying listed values.

        If copying to clipboard does not work on Ubuntu, run
        `sudo apt install xclip` first.
        """

        try:
            loaded_data_for_feature = self.read_feature_profile_as_dict_from_doculect_id(
                doculect_id=doculect_id,
                dir_with_feature_profiles=dir_with_feature_profiles,
            )[feature_id]
        except KeyError:
            raise KeyError(f"{feature_id=} not found for {doculect_id=}")

        data_to_return = {
            key: getattr(loaded_data_for_feature, key)
            for key in (
                KEY_FOR_VALUE_TYPE,
                KEY_FOR_VALUE_ID,
                KEY_FOR_RUSSIAN_NAME_OF_VALUE,
                KEY_FOR_RUSSIAN_COMMENT,
            )
        }

        if verbose:
            print(f"{doculect_id=}, {feature_id=}\n")
            for key in data_to_return.keys():
                key_for_print = (
                    key.replace("_ru", "").replace("_", " ").capitalize().replace("id", "ID")
                )
                if data_to_return[key]:
                    print(f"{key_for_print}: {data_to_return[key]}")
                else:
                    print(f"{key_for_print} is empty")

        # sometimes a custom value can be written in comment while value itself is empty
        text_to_copy = (
            data_to_return[KEY_FOR_RUSSIAN_NAME_OF_VALUE] or data_to_return[KEY_FOR_RUSSIAN_COMMENT]
        )
        if copy_to_clipboard and text_to_copy:
            pyperclip.copy(text_to_copy)
            print("\nValue (or comment for empty value) copied to clipboard")

        return data_to_return
