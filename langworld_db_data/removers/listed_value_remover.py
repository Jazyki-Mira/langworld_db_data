from langworld_db_data import ObjectWithPaths
from langworld_db_data.constants.literals import (
    ID_SEPARATOR,
    KEY_FOR_FEATURE_ID,
    KEY_FOR_ID,
    KEY_FOR_VALUE_ID,
    KEY_FOR_VALUE_TYPE,
)
from langworld_db_data.tools.files.csv_xls import read_dicts_from_csv, write_csv
from langworld_db_data.tools.value_ids.value_ids import extract_feature_id, extract_value_index


class ListedValueRemoverError(Exception):
    pass


class ListedValueRemover(ObjectWithPaths):
    def remove_listed_value(
        self,
        id_of_value_to_remove: str,
    ) -> dict[str, str]:
        """
        Remove listed value from inventories and feature profiles.

        In feature profiles, the name of the value will be kept intact,
        but value type will be replaced with "custom".

        Returns dictionary with data of removed value.
        Its keys are identical to column names in the inventory of listed values.
        """
        removed_value = self._remove_from_inventory_of_listed_values(id_of_value_to_remove)
        self._remove_from_feature_profiles_and_update_ids_whose_indices_are_greater_than_one_of_removed_value(
            id_of_value_to_remove
        )

        return removed_value

    def _remove_from_inventory_of_listed_values(
        self,
        id_of_value_to_remove: str,
    ) -> dict[str, str]:

        line_number_of_value_to_remove = 0
        value_to_remove: dict[str, str] = {}

        rows = read_dicts_from_csv(self.input_file_with_listed_values)

        for i, row in enumerate(rows):
            if row[KEY_FOR_ID] != id_of_value_to_remove:
                continue
            line_number_of_value_to_remove = i
            value_to_remove = row

        if not value_to_remove:
            raise ListedValueRemoverError(
                f"Value ID {id_of_value_to_remove} not found. "
                f"Perhaps it is invalid or does not exist."
            )

        # If value not found, inventory will remain intact
        rows_without_removed_value = (
            rows[:line_number_of_value_to_remove] + rows[line_number_of_value_to_remove + 1 :]
        )

        rows_without_removed_value_and_with_updated_value_indices = (
            self._update_value_indices_in_inventory(
                rows=rows_without_removed_value,
                id_of_removed_value=id_of_value_to_remove,
            )
        )

        write_csv(
            rows_without_removed_value_and_with_updated_value_indices,
            path_to_file=self.output_file_with_listed_values,
            overwrite=True,
            delimiter=",",
        )

        print(f"Removed value {id_of_value_to_remove} from inventory of listed values")
        return value_to_remove

    def _remove_from_feature_profiles_and_update_ids_whose_indices_are_greater_than_one_of_removed_value(
        self,
        id_of_value_to_remove: str,
    ):
        print(id_of_value_to_remove)
        for file in self.input_feature_profiles:
            is_changed = False
            rows = read_dicts_from_csv(file)

            for row in rows:
                if row[KEY_FOR_VALUE_TYPE] != "listed":
                    continue
                if row[KEY_FOR_FEATURE_ID] != extract_feature_id(id_of_value_to_remove):
                    continue

                if row[KEY_FOR_VALUE_ID] == id_of_value_to_remove:
                    row[KEY_FOR_VALUE_ID] = ""
                    row[KEY_FOR_VALUE_TYPE] = "custom"
                    print(f"Changing value type to custom in {file.stem}")
                    is_changed = True
                    break
                elif extract_value_index(row[KEY_FOR_VALUE_ID]) > extract_value_index(
                    id_of_value_to_remove
                ):
                    print(row[KEY_FOR_VALUE_ID])
                    new_value_index = str(extract_value_index(row[KEY_FOR_VALUE_ID]) - 1)
                    row[KEY_FOR_VALUE_ID] = (
                        f"{extract_feature_id(row[KEY_FOR_VALUE_ID])}{ID_SEPARATOR}{new_value_index}"
                    )
                    print(f"Updating value id in {file.stem}")
                    is_changed = True
                    break

            if is_changed:
                write_csv(
                    rows,
                    path_to_file=self.output_dir_with_feature_profiles / file.name,
                    overwrite=True,
                    delimiter=",",
                )
            else:
                print(f"{file.stem} is not changed")

    @staticmethod
    def _update_value_indices_in_inventory(
        rows: list[dict[str, str]],
        id_of_removed_value: str,
    ) -> list[dict[str, str]]:
        feature_id = extract_feature_id(id_of_removed_value)
        index_of_value_to_remove = extract_value_index(id_of_removed_value)
        rows_with_updated_indices = rows.copy()

        for i, row in enumerate(rows):
            if row[KEY_FOR_FEATURE_ID] != feature_id:
                continue
            current_value_index = extract_value_index(row[KEY_FOR_ID])
            if current_value_index > index_of_value_to_remove:
                new_current_value_index = str(current_value_index - 1)
                new_current_value_id = (
                    f"{extract_feature_id(row[KEY_FOR_ID])}{ID_SEPARATOR}{new_current_value_index}"
                )
                rows_with_updated_indices[i][KEY_FOR_ID] = new_current_value_id

        return rows_with_updated_indices


if __name__ == "__main__":
    ListedValueRemover().remove_listed_value(
        id_of_value_to_remove="A-3-9",
    )
