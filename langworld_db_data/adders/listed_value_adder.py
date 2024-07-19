from typing import Optional

from langworld_db_data.adders.adder import Adder, AdderError
from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv


class ListedValueAdderError(AdderError):
    pass


class ListedValueAdder(Adder):
    def add_listed_value(
        self,
        feature_id: str,
        new_value_en: str,
        new_value_ru: str,
        custom_values_to_rename: Optional[list[str]] = None,
        index_to_assign: int = -1,
    ) -> None:
        """Adds listed value to the inventory and marks matching custom value
        in feature profiles as listed.  If one or more custom values
        in feature profiles were formulated differently but now
        have to be renamed to be the new `listed` value, these custom values
        can be passed as a list.
        If no id to assign is given, the new value will be appended after
        the last present value, else the new value will receive ID based on the passed index.
        """

        if not (feature_id and new_value_en and new_value_ru):
            raise ListedValueAdderError("None of the passed strings can be empty")

        try:
            id_of_new_value, _ = self._add_to_inventory_of_listed_values(
                feature_id=feature_id,
                new_value_en=new_value_en,
                new_value_ru=new_value_ru,
                index_to_assign=index_to_assign,
            )

            self._mark_value_as_listed_in_feature_profiles(
                feature_id=feature_id,
                new_value_id=id_of_new_value,
                new_value_ru=new_value_ru,
                custom_values_to_rename=custom_values_to_rename,
            )
        except ValueError as e:
            raise ListedValueAdderError(e)

    def _add_to_inventory_of_listed_values(
        self,
        feature_id: str,
        new_value_en: str,
        new_value_ru: str,
        index_to_assign: int,
    ) -> (str, tuple[int]):
        """
        Returns ID of new value and tuple of indices that must be incremented in feature profiles.
        index_to_assign means number that must be assigned to the new value within the feature, ex. 13 for A-2-13.
        If no index_to_assign is given, the new value will be added as the last one in the feature.
        index_to_assign must be greater than 0.
        """

        rows = read_dicts_from_csv(self.input_file_with_listed_values)

        if not [r for r in rows if r["feature_id"] == feature_id]:
            raise ListedValueAdderError(f"Feature ID {feature_id} not found")

        value_indices_to_inventory_line_numbers: list[dict[str, int]] = []
        """List of dictionaries, each mapping value index to line number in features_listed_values,
        ex. [{"index": 1, "line number": 4}, {"index": 2, "line number": 5}, {"index": 3, "line number": 6}].
        Contains all indices and line numbers of values with given feature_id.
        """

        # Collect all indices and line numbers of given feature into value_indices_to_inventory_line_numbers
        for i, row in enumerate(rows):
            if row["feature_id"] != feature_id:
                continue

            if row["en"] == new_value_en or row["ru"] == new_value_ru:
                raise ValueError(
                    f"Row {row} already contains value you are trying to add"
                )

            value_index = int(row["id"].split(ID_SEPARATOR)[-1])
            value_indices_to_inventory_line_numbers.append(
                {
                    "index": value_index,
                    "line number": i,
                }
            )

        # Check if index_to_assign is -1 or belongs to range of indices in value_indices_to_inventory_line_numbers
        last_index_in_feature = value_indices_to_inventory_line_numbers[-1]["index"]
        acceptable_indices_to_assign = [-1] + [i for i in range(1, last_index_in_feature)]
        if index_to_assign not in acceptable_indices_to_assign:
            raise ValueError(
                f"Invalid index_to assign (must be between 1 and {last_index_in_feature}, "
                f"{index_to_assign} was given)"
            )

        # id_of_new_value and line_number_of_new_value are assigned for default case and then changed if necessary
        id_of_new_value = (
            f"{feature_id}{ID_SEPARATOR}{value_indices_to_inventory_line_numbers[-1]['index'] + 1}"
        )
        line_number_of_new_value = value_indices_to_inventory_line_numbers[-1]["line number"] + 1

        # If value is inserted into range of values, IDs following it must be incremented
        line_numbers_with_ids_to_increment = []

        if index_to_assign > -1:
            id_of_new_value = f"{feature_id}{ID_SEPARATOR}{index_to_assign}"
            for value_index_and_line_number in value_indices_to_inventory_line_numbers:
                if value_index_and_line_number["index"] < index_to_assign:
                    continue

                line_numbers_with_ids_to_increment.append(
                    value_index_and_line_number["line number"]
                )
                if value_index_and_line_number["index"] == index_to_assign:
                    line_number_of_new_value = value_index_and_line_number["line number"]

        # Empty list or list of ints. Contains indices within given feature and is used to correct language profiles:
        # if a profile contains a value whose index belongs to this list, the value ID must be incremented by one.
        # TODO: despite its name, the list now collects indices. Perhaps it should either be renamed or collect IDs
        ids_to_increment_in_profiles = []

        # Update IDs of values whose line numbers are in line_numbers_with_ids_to_increment
        for i, row in enumerate(rows):
            if i not in line_numbers_with_ids_to_increment:
                continue

            ids_to_increment_in_profiles.append(row["id"])
            value_id_to_increment = row["id"]
            components_of_value_id_to_increment = value_id_to_increment.split("-")
            row["id"] = (
                f"{components_of_value_id_to_increment[0]}-{components_of_value_id_to_increment[1]}-"
                f"{int(components_of_value_id_to_increment[2]) + 1}"
            )

        row_with_new_value = [
            {
                "id": id_of_new_value,
                "feature_id": feature_id,
                "en": new_value_en[0].upper() + new_value_en[1:],
                "ru": new_value_ru[0].upper() + new_value_ru[1:],
            }
        ]

        rows_with_new_value_inserted = (
            rows[:line_number_of_new_value] + row_with_new_value + rows[line_number_of_new_value:]
        )

        write_csv(
            rows_with_new_value_inserted,
            path_to_file=self.output_file_with_listed_values,
            overwrite=True,
            delimiter=",",
        )

        return id_of_new_value, ids_to_increment_in_profiles

    def _mark_value_as_listed_in_feature_profiles(
        self,
        feature_id: str,
        new_value_id: str,
        new_value_ru: str,
        custom_values_to_rename: Optional[list[str]] = None,
    ) -> None:
        for file in self.input_feature_profiles:  # MASH: for every Path in the list
            is_changed = False
            rows = read_dicts_from_csv(file)  # MASH: here we get info from the Path

            for i, row in enumerate(rows):
                if row["feature_id"] == feature_id and row["value_type"] == "custom":
                    value_ru = row[
                        "value_ru"
                    ].strip()  # MASH: cut extra whitespaces in the beginning and in the end
                    value_ru = (
                        value_ru[:-1] if value_ru.endswith(".") else value_ru
                    )  # MASH: drop period if exists

                    new_value_with_variants: list[str] = (
                        [new_value_ru] + custom_values_to_rename
                        if custom_values_to_rename
                        else [new_value_ru]
                    )
                    new_value_with_variants = [v.lower() for v in new_value_with_variants]

                    if value_ru.lower() not in new_value_with_variants:
                        break

                    print(
                        f"{file.name}: changing row {i + 2} (feature {feature_id}). "
                        f"Custom value <{row['value_ru']}> will become listed value "
                        f"<{new_value_ru}> ({new_value_id})"
                    )
                    row["value_type"] = "listed"
                    row["value_id"] = new_value_id
                    row["value_ru"] = new_value_ru
                    is_changed = True
                    break

            if is_changed:
                write_csv(
                    rows,
                    path_to_file=self.output_dir_with_feature_profiles / file.name,
                    overwrite=True,
                    delimiter=",",
                )

    # TODO: so now a method must be written that updates IDs of values in profiles after a new value was added to FLV
