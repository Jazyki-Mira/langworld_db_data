from pathlib import Path
from typing import Optional, Union

from langworld_db_data.adders.adder import Adder, AdderError
from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv

KEY_FOR_FEATURE_ID = "feature_id"
KEY_FOR_VALUE_ID = "id"
KEY_FOR_FEATURE_VALUE_INDEX = "index"
KEY_FOR_FEATURE_VALUE_LINE_NUMBER = "line number"


class ListedValueAdderError(AdderError):
    pass


class ListedValueAdder(Adder):
    def add_listed_value(
        self,
        feature_id: str,
        new_value_en: str,
        new_value_ru: str,
        custom_values_to_rename: Optional[list[str]] = None,
        index_to_assign: Union[int, None] = None,
    ) -> None:
        """Adds listed value to the inventory and marks matching custom values
        in feature profiles as listed. If one or more custom values
        in feature profiles were formulated differently but now
        have to be renamed to be the new `listed` value, these custom values
        can be passed as a list.
        If no id to assign is given, the new value will be appended after
        the last present value, else the new value will receive ID based on the passed index.
        """

        if not (feature_id and new_value_en and new_value_ru):
            raise ListedValueAdderError("None of the passed strings can be empty")

        try:
            id_of_new_value = self._add_to_inventory_of_listed_values(
                feature_id=feature_id,
                new_value_en=new_value_en,
                new_value_ru=new_value_ru,
                index_to_assign=index_to_assign,
            )
        except ValueError as e:
            raise ListedValueAdderError(
                f"Failed to add new value to inventory of listed values. {e}"
            )

        # Somewhere here self._increment_value_ids_in_feature_profiles should be used

        try:
            self._mark_value_as_listed_in_feature_profiles(
                feature_id=feature_id,
                new_value_id=id_of_new_value,
                new_value_ru=new_value_ru,
                custom_values_to_rename=custom_values_to_rename,
            )
        except ValueError as e:
            raise ListedValueAdderError(
                f"Failed to mark custom values (that match value being added) as 'listed' in profiles. {e}"
            )

    def _add_to_inventory_of_listed_values(
        self,
        feature_id: str,
        new_value_en: str,
        new_value_ru: str,
        index_to_assign: Union[int, None],
    ) -> str:
        """
        Add new value to the inventory of listed values. Return ID of new value.

        index_to_assign means number that must be assigned to the new value within the feature, ex. 13 for A-2-13.
        If no index_to_assign is given, the new value will be added as the last one in the feature.
        index_to_assign must be greater than 0.
        """

        rows = read_dicts_from_csv(self.input_file_with_listed_values)

        if not [r for r in rows if r[KEY_FOR_FEATURE_ID] == feature_id]:
            raise ListedValueAdderError(f"Feature ID {feature_id} not found")

        # Collect all indices and line numbers of given feature.
        #
        # Indices are final parts of value IDs in the feature where new value is being added.
        # Collecting is done to get index and line number of final value (if the new value itself is intended final)
        # and to calculate line number for the new value (if it is intended non-final).

        for row in rows:
            if row["en"] == new_value_en or row["ru"] == new_value_ru:
                raise ValueError(f"Row {row} already contains value you are trying to add")

        value_indices_to_inventory_line_numbers = self._get_indices_and_their_line_numbers_for_given_feature_in_inventory_of_listed_values(
            rows=rows,
            feature_id=feature_id,
        )

        # Check if passed index is valid
        last_index_in_feature = value_indices_to_inventory_line_numbers[-1][
            KEY_FOR_FEATURE_VALUE_INDEX
        ]
        # The range of numbers acceptable as index_to_assign consists of
        # all the current indices in the given feature and the next number after
        # the current maximum. To include the maximum, we must add 1 to last_index_in_feature.
        # To include the number right after the maximum, we must again add 1.
        # This results in adding 2 to the rightmost range border.
        acceptable_indices_to_assign = set([None] + list(range(1, last_index_in_feature + 2)))
        if index_to_assign not in acceptable_indices_to_assign:
            raise ValueError(
                f"Invalid index_to assign (must be between 1 and {last_index_in_feature + 1}, "
                f"{index_to_assign} was given)"
            )

        if index_to_assign in (
            None,
            last_index_in_feature + 1,
        ):  # new value is being added after the last one
            id_of_new_value = f"{feature_id}{ID_SEPARATOR}{value_indices_to_inventory_line_numbers[-1][KEY_FOR_FEATURE_VALUE_INDEX] + 1}"
            line_number_of_new_value = (
                value_indices_to_inventory_line_numbers[-1][KEY_FOR_FEATURE_VALUE_LINE_NUMBER] + 1
            )
            rows_with_updated_value_indices = tuple(rows.copy())

        # If value is inserted into range of values, IDs following it must be incremented
        else:  # new value being inserted in the middle
            id_of_new_value = f"{feature_id}{ID_SEPARATOR}{index_to_assign}"

            # Go through values of the feature, ignore indices less than index_to_assign,
            # increment all other indices
            rows_with_updated_value_indices = self._increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(
                rows=rows,
                value_indices_to_inventory_line_numbers=value_indices_to_inventory_line_numbers,
                index_to_assign=index_to_assign,
            )

            for value_index_and_line_number in value_indices_to_inventory_line_numbers:
                if value_index_and_line_number[KEY_FOR_FEATURE_VALUE_INDEX] == index_to_assign:
                    line_number_of_new_value = value_index_and_line_number[
                        KEY_FOR_FEATURE_VALUE_LINE_NUMBER
                    ]

        row_with_new_value = tuple(
            [
                {
                    KEY_FOR_VALUE_ID: id_of_new_value,
                    KEY_FOR_FEATURE_ID: feature_id,
                    "en": new_value_en[0].upper() + new_value_en[1:],
                    "ru": new_value_ru[0].upper() + new_value_ru[1:],
                }
            ]
        )

        rows_with_new_value_inserted = (
            rows_with_updated_value_indices[:line_number_of_new_value]
            + row_with_new_value
            + rows_with_updated_value_indices[line_number_of_new_value:]
        )

        write_csv(
            rows_with_new_value_inserted,
            path_to_file=self.output_file_with_listed_values,
            overwrite=True,
            delimiter=",",
        )

        return id_of_new_value

    @staticmethod
    def _get_indices_and_their_line_numbers_for_given_feature_in_inventory_of_listed_values(
        rows: list[dict[str, str]],
        feature_id: str,
    ) -> tuple[dict[str, int], ...]:
        """
        Gather indices (last parts of value ID) and line numbers of feature into which new value will be inserted.

        This method is used to calculate ID of the value being added and its place in rows of listed values inventory.

        Returns tuple of dictionaries containing all indices and line numbers of values with given feature_id.
        Example:
        ({"index": 1, "line number": 4}, {"index": 2, "line number": 5}, {"index": 3, "line number": 6})
        """

        value_indices_to_inventory_line_numbers: list[dict[str, int]] = []

        for i, row in enumerate(rows):
            if row[KEY_FOR_FEATURE_ID] != feature_id:
                continue

            value_index = int(row[KEY_FOR_VALUE_ID].split(ID_SEPARATOR)[-1])
            value_indices_to_inventory_line_numbers.append(
                {
                    KEY_FOR_FEATURE_VALUE_INDEX: value_index,
                    KEY_FOR_FEATURE_VALUE_LINE_NUMBER: i,
                }
            )

        return tuple(value_indices_to_inventory_line_numbers)

    @staticmethod
    def _increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(
        rows: list[dict[str, str]],
        value_indices_to_inventory_line_numbers: tuple[dict[str, int], ...],
        index_to_assign: int,
    ) -> tuple[dict[str, str], ...]:
        """
        Increases by 1 index of every value that will come after the value passed for insertion.

        Returns tuple of dictionaries with incremented indices and line numbers.
        """

        rows_with_incremented_indices = rows[:]
        for value_index_and_line_number in value_indices_to_inventory_line_numbers:
            if value_index_and_line_number[KEY_FOR_FEATURE_VALUE_INDEX] < index_to_assign:
                continue
            row_where_id_must_be_incremented = value_index_and_line_number[
                KEY_FOR_FEATURE_VALUE_LINE_NUMBER
            ]
            value_id_to_increment = rows_with_incremented_indices[
                row_where_id_must_be_incremented
            ][KEY_FOR_VALUE_ID]
            components_of_value_id_to_increment = value_id_to_increment.split("-")
            rows_with_incremented_indices[row_where_id_must_be_incremented][KEY_FOR_VALUE_ID] = (
                f"{components_of_value_id_to_increment[0]}-{components_of_value_id_to_increment[1]}-"
                f"{int(components_of_value_id_to_increment[2]) + 1}"
            )

        return tuple(rows_with_incremented_indices)

    @staticmethod
    def _increment_value_ids_in_feature_profiles(
        new_value_id: str,
        input_dir: Path,
        output_dir: Path,
    ):  # How should I connect it with properties of the object? It has input and output feature profiles dir
        for file in sorted(list(input_dir.glob("*.csv"))):
            # I see that in the next function is_changed is used, to write only changed files.
            # As a first iteration, I am trying to do without it.
            rows = read_dicts_from_csv(file)

            new_value_id_decomposed = new_value_id.split("-")
            target_feature_id = f"{new_value_id_decomposed[0]}-{new_value_id_decomposed[1]}"
            new_value_index = int(new_value_id_decomposed[-1])
            for row in rows:
                if row["value_type"] != "listed":
                    continue
                if row["feature_id"] != target_feature_id:
                    continue
                current_value_id_decomposed = row["value_id"].split("-")
                current_value_index = current_value_id_decomposed[2]
                if int(current_value_index) < int(new_value_index):
                    print(True)
                    continue
                current_value_id_decomposed[2] = str(int(current_value_id_decomposed[2]) + 1)
                incremented_current_value_id = (
                    f"{current_value_id_decomposed[0]}-"
                    f"{current_value_id_decomposed[1]}-"
                    f"{current_value_id_decomposed[2]}"
                )
                row["value_id"] = incremented_current_value_id

            write_csv(
                rows,
                path_to_file=output_dir / file.name,
                overwrite=True,
                delimiter=",",
            )

    def _mark_value_as_listed_in_feature_profiles(
        self,
        feature_id: str,
        new_value_id: str,
        new_value_ru: str,
        custom_values_to_rename: Optional[list[str]] = None,
    ) -> None:
        for file in self.input_feature_profiles:
            is_changed = False
            rows = read_dicts_from_csv(file)

            for i, row in enumerate(rows):
                if row[KEY_FOR_FEATURE_ID] == feature_id and row["value_type"] == "custom":
                    value_ru = row["value_ru"].strip()
                    value_ru = value_ru[:-1] if value_ru.endswith(".") else value_ru

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
