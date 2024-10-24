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
            removed_value_information = {key: row[key] for key in ("feature_id", "en", "ru")}

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

        return removed_value_information

    def _remove_from_feature_profiles(self):
        self._update_value_ids_in_feature_profiles()

    @staticmethod
    def _update_value_indices_in_inventory(
        rows: list[dict[str, str]],
        id_of_removed_value: str,
    ) -> list[dict[str, str]]:
        feature_id = "-".join(id_of_removed_value.split(ID_SEPARATOR)[:2])
        rows_with_updated_indices = rows

        for i, row in enumerate(rows):
            if row["feature_id"] != feature_id:
                continue
            current_value_index = int(row["id"].split("-")[2])
            index_of_value_to_remove = int(id_of_removed_value.split("-")[2])
            if current_value_index > index_of_value_to_remove:
                current_value_id_decomposed = row["id"].split("-")
                new_current_value_index = str(current_value_index - 1)
                new_current_value_id = "-".join(
                    current_value_id_decomposed[:2] + [new_current_value_index]
                )
                rows_with_updated_indices[i]["id"] = new_current_value_id

        return rows_with_updated_indices

    def _update_value_ids_in_feature_profiles(
        self,
        id_of_value_to_remove: str,
    ):
        if not self.output_dir_with_feature_profiles.exists():
            self.output_dir_with_feature_profiles.mkdir()

        file_with_changed_profiles_report = (
            self.output_dir_with_feature_profiles / "changed_profiles.txt"
        )
        file_with_changed_profiles_report.touch()

        for file in self.input_feature_profiles:
            is_changed = False
            rows = read_dicts_from_csv(file)

            for row in rows:
                if row["value_id"] == id_of_value_to_remove:
                    row["value_id"] = ""
                    row["value_type"] = "custom"
                    is_changed = True
                    break

            if is_changed:
                print(f"Writing new file for {file.stem}")
                write_csv(
                    rows,
                    path_to_file=self.output_dir_with_feature_profiles / file.name,
                    overwrite=True,
                    delimiter=",",
                )
                with open(file_with_changed_profiles_report, "w", encoding="utf-8") as report:
                    print(f"Adding '{file.stem}' to the changed files report")
                    report.write(f"{file.stem}")
            else:
                print(f"{file.stem} is not changed")

        with open(file_with_changed_profiles_report, "w", encoding="utf-8") as report:
            report.write("\n")
