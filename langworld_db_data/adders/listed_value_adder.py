from typing import Optional, Union

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
        index_to_insert_after: Union[int, str] = "last",
    ) -> None:
        """Adds listed value to the inventory and marks matching custom value
        in feature profiles as listed.  If one or more custom values
        in feature profiles were formulated differently but now
        have to be renamed to be the new `listed` value, these custom values
        can be passed as a list.
        If no id to insert after is given, the new value will be put after
        the last present value, else the new value will be put right after the given one.
        """
        # MASH: all new value properties must be given
        if not (feature_id and new_value_en and new_value_ru):
            raise ListedValueAdderError("None of the passed strings can be empty")

        # MASH: this one creates an ID for the new value and add it to FLV (always at the end of its feature)
        # TODO: add possibility to insert new value after a given value
        id_of_new_value = self._add_to_inventory_of_listed_values(
            feature_id=feature_id, new_value_en=new_value_en, new_value_ru=new_value_ru,
            index_to_insert_after=index_to_insert_after,
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
        index_to_insert_after: Union[int, str] = "last",
    ) -> str:
        rows = read_dicts_from_csv(self.input_file_with_listed_values)

        # MASH: check if feature ID exists
        if not [r for r in rows if r["feature_id"] == feature_id]:
            raise ListedValueAdderError(f"Feature ID {feature_id} not found")

        index_of_last_row_for_given_feature = 0
        last_digit_of_value_id = 0
        id_of_new_value = ""

        for i, row in enumerate(rows):
            if (
                row["feature_id"] != feature_id
            ):  # MASH: throws away everything beyond the given feature ID
                continue

            if row["en"] == new_value_en or row["ru"] == new_value_ru:
                raise ListedValueAdderError(
                    f"Row {row} already contains value you are trying to add"
                )  # MASH: this one appears if some existing value names are passed

            # Keep updating those with each row. This means that at the last row of the
            # feature they will reach the required values.
            index_of_last_row_for_given_feature = i

            last_digit_of_value_id = int(
                row["id"].split(SEPARATOR)[-1]
            )  # MASH: bites off the last number in value id
            id_of_new_value = feature_id + SEPARATOR + str(last_digit_of_value_id + 1)
            # MASH: so initially this one is refreshed several times before the final variant
        
        print(index_to_insert_after)
        if (type(index_to_insert_after) is int and
                index_to_insert_after > last_digit_of_value_id):
            raise ListedValueAdderError(
                f"The given ID {feature_id + str(index_to_insert_after)} exceeds the maximal ID {id_of_new_value}"
            )

        row_with_new_value = [
            {
                "id": id_of_new_value,
                "feature_id": feature_id,
                "en": new_value_en[0].upper() + new_value_en[1:],
                "ru": new_value_ru[0].upper() + new_value_ru[1:],
            }
        ]  # MASH: this dict is wrapped into list because in the next block it is concatenated with slices of
        # the former listed values list

        rows_with_new_value_inserted = (
            rows[: index_of_last_row_for_given_feature + 1]
            + row_with_new_value
            + rows[index_of_last_row_for_given_feature + 1 :]
        )

        # MASH: and finally the new listed values list is written into the output file
        write_csv(
            rows_with_new_value_inserted,
            path_to_file=self.output_file_with_listed_values,
            overwrite=True,
            delimiter=",",
        )

        return id_of_new_value

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

    # TODO: so now I should write a method that updates IDs of values in profiles after a new value was added to FLV
