from pathlib import Path

from langworld_db_data.constants.literals import (
    ATOMIC_VALUE_SEPARATOR,
    KEY_FOR_ID,
    KEY_FOR_RUSSIAN,
    KEY_FOR_RUSSIAN_NAME_OF_VALUE,
    KEY_FOR_VALUE_ID,
)
from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, INVENTORIES_DIR
from langworld_db_data.tools.common.files.csv_xls import read_dicts_from_csv, write_csv
from langworld_db_data.tools.common.files.txt import remove_extra_space


class ListedValueRenamerError(Exception):
    pass


class ListedValueRenamer:
    def __init__(
        self,
        input_feature_profiles_dir: Path = FEATURE_PROFILES_DIR,
        input_inventories_dir: Path = INVENTORIES_DIR,
        output_feature_profiles_dir: Path = FEATURE_PROFILES_DIR,
        output_inventories_dir: Path = INVENTORIES_DIR,
    ) -> None:
        self.input_feature_profiles_dir = input_feature_profiles_dir
        self.input_inventories_dir = input_inventories_dir
        self.output_feature_profiles_dir = output_feature_profiles_dir
        self.output_inventories_dir = output_inventories_dir
        self.inventory_of_listed_values = read_dicts_from_csv(
            self.input_inventories_dir / "features_listed_values.csv"
        )

    def rename_value_in_profiles_and_inventories(
        self,
        id_of_value_to_rename: str,
        new_value_name: str,
    ) -> None:
        """
        Renames value with given ID in all feature profiles and inventory of listed values.
        Also works with elementary values in multiselect features.
        """
        if remove_extra_space(new_value_name) == "":
            raise ListedValueRenamerError("a null string passed as new value name")
        if not self._value_id_exists(id_of_value_to_rename):
            raise ListedValueRenamerError(f"{id_of_value_to_rename} does not exist")
        if self._current_value_name_is_equal_to_new_value_name(
            id_of_value_to_rename=id_of_value_to_rename, new_value_name=new_value_name
        ):
            raise ListedValueRenamerError(f"Value is already called '{new_value_name}'")
        if not self.output_inventories_dir.exists():
            self.output_inventories_dir.mkdir(parents=True, exist_ok=True)
        self._update_features_listed_values(
            id_of_value_to_rename=id_of_value_to_rename,
            new_value_name=new_value_name,
            input_file=self.input_inventories_dir / "features_listed_values.csv",
            output_file=self.output_inventories_dir / "features_listed_values.csv",
        )
        files = list(self.input_feature_profiles_dir.glob("*.csv"))
        for file in files:
            print(f"Processing {file.name}")
            self._update_one_feature_profile(
                id_of_value_to_rename=id_of_value_to_rename,
                new_value_name=new_value_name,
                input_file=file,
                output_dir=self.output_feature_profiles_dir,
            )

    def _value_id_exists(
        self,
        id_of_value_to_rename: str,
    ) -> bool:
        for line in self.inventory_of_listed_values:
            if line[KEY_FOR_ID] == id_of_value_to_rename:
                return True
        return False

    def _current_value_name_is_equal_to_new_value_name(
        self,
        id_of_value_to_rename: str,
        new_value_name: str,
    ):
        for line in self.inventory_of_listed_values:
            if line[KEY_FOR_ID] != id_of_value_to_rename:
                continue
            if line[KEY_FOR_RUSSIAN] == new_value_name:
                return True
        return False

    def _update_features_listed_values(
        self,
        id_of_value_to_rename: str,
        new_value_name: str,
        input_file: Path,
        output_file: Path,
    ) -> None:

        data_to_write = []
        for line in self.inventory_of_listed_values:
            if id_of_value_to_rename != line[KEY_FOR_ID]:
                data_to_write.append(line)
                continue
            line_to_write = line.copy()
            print(f"Found exact match in {input_file.name}")
            print(f"Changed {line[KEY_FOR_RUSSIAN]} to {new_value_name}")
            line_to_write[KEY_FOR_RUSSIAN] = new_value_name
            data_to_write.append(line_to_write)
        write_csv(
            rows=data_to_write,
            path_to_file=output_file,
            overwrite=True,
            delimiter=",",
        )

    @staticmethod
    def _update_one_feature_profile(
        id_of_value_to_rename: str,
        new_value_name: str,
        input_file: Path,
        output_dir: Path,
    ) -> None:

        number_of_replacements = 0
        data_from_file = read_dicts_from_csv(input_file)
        data_to_write = []
        for line in data_from_file:
            if id_of_value_to_rename not in line[KEY_FOR_VALUE_ID]:
                data_to_write.append(line)
                continue
            line_to_write = line.copy()
            # After this clause, only lines with the target value are considered (they may contain other values too)
            if ATOMIC_VALUE_SEPARATOR in line[KEY_FOR_VALUE_ID]:
                print(f"Found match in combined value in {input_file.name}")
                combined_value_ids = line[KEY_FOR_VALUE_ID].split(ATOMIC_VALUE_SEPARATOR)
                target_value_index = combined_value_ids.index(id_of_value_to_rename)
                combined_value_names = line[KEY_FOR_RUSSIAN_NAME_OF_VALUE].split(
                    ATOMIC_VALUE_SEPARATOR
                )
                combined_value_names.pop(target_value_index)
                combined_value_names.insert(target_value_index, new_value_name)
                line_to_write[KEY_FOR_RUSSIAN_NAME_OF_VALUE] = ATOMIC_VALUE_SEPARATOR.join(
                    combined_value_names
                )
                number_of_replacements += 1
                data_to_write.append(line_to_write)
                print(
                    f"Changed {line[KEY_FOR_RUSSIAN_NAME_OF_VALUE]} to {line_to_write[KEY_FOR_RUSSIAN_NAME_OF_VALUE]}"
                )
                continue
            # After this clause, only those lines are considered which contain the target value only
            print(f"Found exact match in {input_file.name}")
            line_to_write[KEY_FOR_RUSSIAN_NAME_OF_VALUE] = new_value_name
            number_of_replacements += 1
            data_to_write.append(line_to_write)
            print(f"Changed {line[KEY_FOR_RUSSIAN_NAME_OF_VALUE]} to {new_value_name}")
        print(f"Replacements made in this file: {number_of_replacements}")
        output_file = output_dir / input_file.name
        write_csv(rows=data_to_write, path_to_file=output_file, overwrite=True, delimiter=",")
        print(f"Successfully written to {output_file}")


if __name__ == "__main__":
    ListedValueRenamer().rename_value_in_profiles_and_inventories(
        id_of_value_to_rename="",
        new_value_name="",
    )  # pragma: no cover
