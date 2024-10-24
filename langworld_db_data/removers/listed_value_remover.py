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
            id_of_value_to_remove
        )
        """
        Contains the feature ID and English and Russian names of the removed value.
        """
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
        """
        Contains the feature ID and English and Russian names of the removed value.
        """

        rows = read_dicts_from_csv(self.input_file_with_listed_values)

        line_number_of_value_to_remove = 0

        for i, row in enumerate(rows):
            if row["id"] != id_of_value_to_remove:
                continue
            line_number_of_value_to_remove = i
            removed_value_information = {
                key: row[key] for key in ("feature_id", "en", "ru")
            }

        rows_with_updated_value_indices = self._update_value_indices_in_inventory(
            rows=rows,
            id_of_value_to_remove=id_of_value_to_remove,
        )

        # If value not found, inventory will remain intact
        rows_without_removed_value = (
            rows_with_updated_value_indices[:line_number_of_value_to_remove]
            + rows_with_updated_value_indices[line_number_of_value_to_remove + 1 :]
        )

        write_csv(
            rows_without_removed_value,
            path_to_file=self.output_file_with_listed_values,
            overwrite=True,
            delimiter=",",
        )

        return removed_value_information

    def _remove_from_feature_profiles(self):
        self._update_value_ids_in_feature_profiles()

    @staticmethod
    def _update_value_indices_in_inventory(
        rows: list[dict[str, str]],
        id_of_value_to_remove: str,
    ) -> list[dict[str, str]]:
        feature_id = "-".join(id_of_value_to_remove.split(ID_SEPARATOR)[:2])
        rows_with_updated_indices = rows

        for i, row in enumerate(rows):
            if row["feature_id"] != feature_id:
                continue
            current_value_index = int(row["id"].split("-")[2])
            index_of_value_to_remove = int(id_of_value_to_remove.split("-")[2])
            if current_value_index > index_of_value_to_remove:
                current_value_id_decomposed = row["id"].split("-")
                new_current_value_index = str(current_value_index - 1)
                new_current_value_id = "-".join(
                    current_value_id_decomposed[:2] + [new_current_value_index]
                )
                rows_with_updated_indices[i]["id"] = new_current_value_id

        return rows_with_updated_indices

    def _update_value_ids_in_feature_profiles(self):
        pass
