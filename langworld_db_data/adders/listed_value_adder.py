from typing import Literal, Optional, Union

from langworld_db_data.adders.adder import Adder, AdderError
from langworld_db_data.constants.literals import SEPARATOR
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
        index_to_assign: Union[int, str] = "last",
    ) -> None:
        """Adds listed value to the inventory and marks matching custom value
        in feature profiles as listed.  If one or more custom values
        in feature profiles were formulated differently but now
        have to be renamed to be the new `listed` value, these custom values
        can be passed as a list.
        If no id to insert after is given, the new value will be appended after
        the last present value, else the new value will be put right after the given one.
        """
        # MASH: all new value properties must be given
        if not (feature_id and new_value_en and new_value_ru):
            raise ListedValueAdderError("None of the passed strings can be empty")

        # MASH: this one creates an ID for the new value and add it to FLV (always at the end of its feature)
        # TODO: add possibility to insert new value after a given value
        id_of_new_value = self._add_to_inventory_of_listed_values(
            feature_id=feature_id,
            new_value_en=new_value_en,
            new_value_ru=new_value_ru,
            index_to_assign=index_to_assign,
        )
        # MASH: this one replaces custom values (if any were given) with the new listed one
        self._mark_value_as_listed_in_feature_profiles(
            feature_id=feature_id,
            new_value_id=id_of_new_value,
            new_value_ru=new_value_ru,
            custom_values_to_rename=custom_values_to_rename,
        )

    def _add_to_inventory_of_listed_values(
        self,
        feature_id: str,
        new_value_en: str,
        new_value_ru: str,
        index_to_assign: Union[int, Literal["put as first", "last"]] = -1,
    ) -> str:
        """
        If a value index to insert after is given, the new value will be put after it.
        To append the new value to the end of the given feature, leave index_to_assign as default.
        To insert the new value at the beginning, make index_to_assign = 0
        """

        rows = read_dicts_from_csv(self.input_file_with_listed_values)

        if not [r for r in rows if r["feature_id"] == feature_id]:
            raise ListedValueAdderError(f"Feature ID {feature_id} not found")

        id_of_new_value = ""
        input_values_diapason = []

        for i, row in enumerate(rows):
            if row["feature_id"] != feature_id:
                continue

            if row["en"] == new_value_en or row["ru"] == new_value_ru:
                raise ListedValueAdderError(
                    f"Row {row} already contains value you are trying to add"
                )

            last_digit_of_value_id = int(row["id"].split(SEPARATOR)[-1])
            input_values_diapason.append(
                {
                    "index": last_digit_of_value_id,
                    "row": i,
                }
            )
        print(input_values_diapason)

        if type(index_to_assign) is int and index_to_assign > input_values_diapason[-1]["index"]:
            raise ListedValueAdderError(
                f"The given ID {feature_id + str(index_to_assign)} exceeds the maximal ID {id_of_new_value}"
            )

        index_of_new_value = 0
        row_of_new_value = 0
        id_of_new_value = ""
        rows_to_increment_value_id = []

        if type(index_to_assign) is int:
            index_to_assign = int(index_to_assign)
            # Without this line, the next functions give warning about variable type which is Union in this function
            # but can only be int in the inner functions
            if index_to_assign == -1:
                output_values_diapason = input_values_diapason
                index_of_new_value = output_values_diapason[-1]["index"] + 1
                row_of_new_value = output_values_diapason[-1]["row"] + 1
                rows_to_increment_value_id = []
            else:
                output_values_diapason, index_of_new_value, row_of_new_value = (
                    self.update_values_diapason_and_get_new_value_properties(
                        values_diapason=input_values_diapason,
                        index_to_assign=index_to_assign,
                    )
                )
                rows_to_increment_value_id = (
                    self._get_list_of_rows_where_value_ids_must_be_incremented(
                        values_diapason=output_values_diapason,
                        index_to_assign=index_to_assign,
                    )
                )

            id_of_new_value = f"{feature_id}{SEPARATOR}{index_of_new_value}"
            print(id_of_new_value)

        elif index_to_assign == "put as first":
            index_of_new_value = 1
            row_of_new_value = input_values_diapason[0]["row"] - 1
            index_to_assign = 0
            output_values_diapason, _, _ = (
                self.update_values_diapason_and_get_new_value_properties(
                    values_diapason=input_values_diapason,
                    index_to_assign=index_to_assign,
                )
            )

            id_of_new_value = f"{feature_id}{SEPARATOR}{index_of_new_value}"

            rows_to_increment_value_id = (
                self._get_list_of_rows_where_value_ids_must_be_incremented(
                    values_diapason=output_values_diapason,
                    index_to_assign=index_to_assign,
                )
            )

        row_with_new_value = [
            {
                "id": id_of_new_value,
                "feature_id": feature_id,
                "en": new_value_en[0].upper() + new_value_en[1:],
                "ru": new_value_ru[0].upper() + new_value_ru[1:],
            }
        ]

        for i, row in enumerate(rows):
            if i + 1 not in rows_to_increment_value_id:
                continue
            value_id_to_increment = row["id"]
            value_id_to_increment_split = value_id_to_increment.split("-")
            row["id"] = (
                f"{value_id_to_increment_split[0]}-{value_id_to_increment_split[1]}-"
                f"{int(value_id_to_increment_split[2]) + 1}"
            )

        rows_with_new_value_inserted = (
            rows[:row_of_new_value] + row_with_new_value + rows[row_of_new_value:]
        )

        write_csv(
            rows_with_new_value_inserted,
            path_to_file=self.output_file_with_listed_values,
            overwrite=True,
            delimiter=",",
        )

        return id_of_new_value

    @staticmethod
    def update_values_diapason_and_get_new_value_properties(
        values_diapason: list,
        index_to_assign: int,
    ) -> tuple[list, int, int]:
        index_of_new_value = 0
        row_of_new_value = 0
        for item in values_diapason:
            if item["index"] < index_to_assign:
                continue
            if item["index"] == index_to_assign:
                index_of_new_value = item["index"]
                row_of_new_value = item["row"]
            item["index"] += 1
            item["row"] += 1
        return values_diapason, index_of_new_value, row_of_new_value

    @staticmethod
    def _get_list_of_rows_where_value_ids_must_be_incremented(
        values_diapason: list,
        index_to_assign: int,
    ):
        rows_to_increment_value_id = []
        for item in values_diapason:
            if item["index"] < index_to_assign:
                continue
            rows_to_increment_value_id.append(item["row"])
        return rows_to_increment_value_id

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
