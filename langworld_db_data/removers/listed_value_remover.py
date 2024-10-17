from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv
from langworld_db_data.removers.remover import Remover, RemoverError


class ListedValueRemoverError(RemoverError):
    pass


class ListedValueRemover(Remover):
    def remove_listed_value(
        self,
        id_of_value_to_remove: str,
    ) -> dict[str, str]:
        removed_value_information = self._remove_from_inventory_of_listed_values(
            id_of_value_to_remove=id_of_value_to_remove
        )
        self._remove_from_feature_profiles()

        if not removed_value_information:
            raise ListedValueRemoverError(
                f"Value ID {id_of_value_to_remove} not found. "
                f"Perhaps it is invalid or does not exist"
            )
        else:
            return removed_value_information

    def _remove_from_inventory_of_listed_values(
        self,
        id_of_value_to_remove: str,
    ) -> dict[str, str]:
        removed_value_information = {}

        rows = read_dicts_from_csv(self.input_file_with_listed_values)
        for i, row in enumerate(rows):
            if row["id"] == id_of_value_to_remove:
                line_number_of_value_to_remove = i
                removed_value_information["feature_id"] = row["feature_id"]
                removed_value_information["en"] = row["en"]
                removed_value_information["ru"] = row["ru"]
                break

        self._update_value_ids_in_inventory()

        rows_without_removed_value = (
            rows[:line_number_of_value_to_remove] + rows[line_number_of_value_to_remove + 1 :]
        )

        write_csv(
            rows_without_removed_value,
            path_to_file=self.output_file_with_listed_values,
            overwrite=True,
            delimiter=",",
        )

        return removed_value_information

    def _remove_from_feature_profiles(self):
        pass

    def _update_value_ids_in_inventory(self):
        self._update_value_ids_in_feature_profiles()

    def _update_value_ids_in_feature_profiles(self):
        pass
