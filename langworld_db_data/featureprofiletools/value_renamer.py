from pathlib import Path

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, INVENTORIES_DIR
from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv
from langworld_db_data.filetools.txt import remove_extra_space

ATOMIC_VALUE_SEPARATOR = "&"


class ValueRenamerError(Exception):
    pass


class ValueRenamer:
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
            raise ValueRenamerError("a null string passed as new value name")
        if not self._value_id_exists(id_of_value_to_rename):
            raise ValueRenamerError(f"{id_of_value_to_rename} does not exist")
        if self._current_value_name_is_equal_to_new_value_name(
            id_of_value_to_rename=id_of_value_to_rename, new_value_name=new_value_name
        ):
            raise ValueRenamerError(f"'{new_value_name}' coincides with the current value name")
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
        data_from_file = read_dicts_from_csv(
            self.input_inventories_dir / "features_listed_values.csv"
        )
        for line in data_from_file:
            if line["id"] == id_of_value_to_rename:
                return True
        return False

    def _current_value_name_is_equal_to_new_value_name(
        self,
        id_of_value_to_rename: str,
        new_value_name: str,
    ):
        data_from_file = read_dicts_from_csv(
            self.input_inventories_dir / "features_listed_values.csv"
        )
        for line in data_from_file:
            if line["id"] != id_of_value_to_rename:
                continue
            if line["ru"] == new_value_name:
                return True
            return False

    @staticmethod
    def _update_features_listed_values(
        id_of_value_to_rename: str,
        new_value_name: str,
        input_file: Path,
        output_file: Path,
    ) -> None:

        data_from_file = read_dicts_from_csv(input_file)
        data_to_write = []
        for line in data_from_file:
            if id_of_value_to_rename not in line["id"]:
                data_to_write.append(line)
                continue
            line_to_write = line.copy()
            print(f"Found exact match in {input_file.name}")
            print(f"Changed {line['ru']} to {new_value_name}")
            line_to_write["ru"] = new_value_name
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
            if id_of_value_to_rename not in line["value_id"]:
                data_to_write.append(line)
                continue
            line_to_write = line.copy()
            # After this clause, only lines with the target value are considered (they may contain other values too)
            if ATOMIC_VALUE_SEPARATOR in line["value_id"]:
                print(f"Found match in combined value in {input_file.name}")
                combined_value_ids = line["value_id"].split(ATOMIC_VALUE_SEPARATOR)
                target_value_index = combined_value_ids.index(id_of_value_to_rename)
                combined_value_names = line["value_ru"].split(ATOMIC_VALUE_SEPARATOR)
                combined_value_names.pop(target_value_index)
                combined_value_names.insert(target_value_index, new_value_name)
                line_to_write["value_ru"] = ATOMIC_VALUE_SEPARATOR.join(combined_value_names)
                number_of_replacements += 1
                data_to_write.append(line_to_write)
                print(f"Changed {line['value_ru']} to {line_to_write['value_ru']}")
                continue
            # After this clause, only those lines are considered which contain the target value only
            print(f"Found exact match in {input_file.name}")
            line_to_write["value_ru"] = new_value_name
            number_of_replacements += 1
            data_to_write.append(line_to_write)
            print(f"Changed {line['value_ru']} to {new_value_name}")
        print(f"Replacements made in this file: {number_of_replacements}")
        output_file = output_dir / input_file.name
        write_csv(rows=data_to_write, path_to_file=output_file, overwrite=True, delimiter=",")
        print(f"Successfully written to {output_file}")
