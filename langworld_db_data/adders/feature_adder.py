from pathlib import Path
from typing import Union

from langworld_db_data import ObjectWithPaths
from langworld_db_data.constants.literals import (
    ID_SEPARATOR,
    KEY_FOR_ENGLISH,
    KEY_FOR_ENGLISH_COMMENT,
    KEY_FOR_FEATURE_ID,
    KEY_FOR_ID,
    KEY_FOR_RUSSIAN,
    KEY_FOR_RUSSIAN_COMMENT,
    KEY_FOR_RUSSIAN_NAME_OF_FEATURE,
    KEY_FOR_RUSSIAN_NAME_OF_VALUE,
    KEY_FOR_VALUE_ID,
    KEY_FOR_VALUE_TYPE,
)
from langworld_db_data.constants.paths import FILE_WITH_CATEGORIES, FILE_WITH_NAMES_OF_FEATURES
from langworld_db_data.tools.files.csv_xls import (
    read_column_from_csv,
    read_dicts_from_csv,
    write_csv,
)
from langworld_db_data.tools.files.txt import remove_extra_space
from langworld_db_data.tools.value_ids.extract import (
    extract_category_id,
    extract_feature_index,
    extract_value_index,
)

KEY_FOR_FEATURE_INDEX = "index"
KEY_FOR_LINE_NUMBER = "line number"


class FeatureAdderError(Exception):
    pass


class FeatureAdder(ObjectWithPaths):
    def __init__(
        self,
        *,
        file_with_categories: Path = FILE_WITH_CATEGORIES,
        input_file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
        # ability to give a different output file is mostly for testing:
        output_file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
        **kwargs,
    ):
        # I know **kwargs removes argument hinting, but to repeat all arguments will
        # make too many lines. All arguments are keyword-only, so the wrong/mistyped
        # argument cannot be passed.
        super().__init__(**kwargs)
        self.file_with_categories = file_with_categories
        self.input_file_with_features = input_file_with_features
        self.output_file_with_features = output_file_with_features

    def add_feature(
        self,
        category_id: str,
        feature_en: str,
        feature_ru: str,
        listed_values_to_add: list[dict[str, str]],
        index_to_assign: Union[int, None] = None,
    ) -> None:
        """
        Add new feature to the feature inventory, listed value inventory and feature profiles.

        index_to_assign means number that must be assigned to the new feature within the category, ex. 13 for A-13.
        If no index_to_assign is given, the new feature will be added as the last one in the category.
        index_to_assign must be greater than 0.
        """

        _ = remove_extra_space
        cat_id, feat_en, feat_ru = _(category_id), _(feature_en), _(feature_ru)

        if not (cat_id and feat_en and feat_ru and listed_values_to_add):
            raise FeatureAdderError(
                "Some of the values passed are empty: "
                f"{cat_id=}, {feat_ru=}, {feat_en=}, {listed_values_to_add=}"
            )

        for item in listed_values_to_add:
            if not (KEY_FOR_ENGLISH in item and KEY_FOR_RUSSIAN in item):
                raise FeatureAdderError(
                    f"Listed value must have keys 'en' and 'ru'. Your value: {item}"
                )

        if cat_id not in read_column_from_csv(
            path_to_file=self.file_with_categories, column_name=KEY_FOR_ID
        ):
            raise FeatureAdderError(
                f"Category ID <{cat_id}> not found in file" f" {self.file_with_categories.name}"
            )

        try:
            feature_id = self._add_feature_to_inventory_of_features(
                category_id=cat_id,
                new_feature_en=feat_en,
                new_feature_ru=feat_ru,
                index_to_assign=index_to_assign,
            )
        except ValueError as e:
            raise FeatureAdderError(f"Failed to add new feature to inventory of features. {e}")

        self._add_values_of_new_feature_to_inventory_of_listed_values(
            feature_id=feature_id,
            listed_values_to_add=listed_values_to_add,
        )

        self._add_feature_to_feature_profiles(
            feature_id=feature_id,
            feature_ru=feat_ru,
        )

    def _add_feature_to_inventory_of_features(
        self,
        category_id: str,
        new_feature_en: str,
        new_feature_ru: str,
        index_to_assign: Union[int, None] = None,
    ) -> str:
        """
        Add new feature to the inventory of features. Return ID of new feature.

        index_to_assign means number that must be assigned to the new feature within the category, ex. 13 for A-13.
        If no index_to_assign is given, the new feature will be added as the last one in the category.
        index_to_assign must be greater than 0.
        """
        rows = read_dicts_from_csv(self.input_file_with_features)

        if new_feature_en in [row[KEY_FOR_ENGLISH] for row in rows] or new_feature_ru in [
            row[KEY_FOR_RUSSIAN] for row in rows
        ]:
            # note that this check should not be restricted to one feature category
            raise FeatureAdderError(
                "English or Russian feature name is already present in list of features"
            )

        # To figure out the ID of the new feature (if index_to_assign is None)
        # and to figure out the position of the new feature in inventory
        # we should get feature indices and line numbers from rows.
        # The same procedure is done by ListedValueAdder with a specific method.

        feature_indices_to_inventory_line_numbers: list[dict[str, int]] = []

        for i, row in enumerate(rows):
            if not category_id in row[KEY_FOR_ID]:
                continue

            feature_index = extract_feature_index(row[KEY_FOR_ID])
            feature_indices_to_inventory_line_numbers.append(
                {
                    KEY_FOR_FEATURE_INDEX: feature_index,
                    KEY_FOR_LINE_NUMBER: i,
                }
            )

        # Check if passed index is valid
        last_index_in_category = feature_indices_to_inventory_line_numbers[-1][
            KEY_FOR_FEATURE_INDEX
        ]
        # The range of numbers acceptable as index_to_assign consists of
        # all the current indices in the given category and the next number after
        # the current maximum. To include the maximum, we must add 1 to last_index_in_category.
        # To include the number right after the maximum, we must again add 1.
        # This results in adding 2 to the rightmost range border.
        acceptable_indices_to_assign = set([None] + list(range(1, last_index_in_category + 2)))
        # Here we add None to the list because None is the default value for appending
        # feature to the end of category
        if index_to_assign not in acceptable_indices_to_assign:
            raise ValueError(
                f"Invalid index_to_assign (must be between 1 and {last_index_in_category + 1}, "
                f"{index_to_assign} was given)"
            )

        if index_to_assign in (
            None,
            last_index_in_category + 1,
        ):  # new feature is being added after the last one
            id_of_new_feature = (
                f"{category_id}{ID_SEPARATOR}"
                f"{feature_indices_to_inventory_line_numbers[-1][KEY_FOR_FEATURE_INDEX] + 1}"
            )
            line_number_of_new_feature = (
                feature_indices_to_inventory_line_numbers[-1][KEY_FOR_LINE_NUMBER] + 1
            )
            rows_with_updated_feature_indices = tuple(rows.copy())

        else:  # new feature being inserted in the middle
            id_of_new_feature = f"{category_id}{ID_SEPARATOR}{index_to_assign}"

            # Go through features of the category, ignore indices less than index_to_assign,
            # increment all other indices
            rows_with_updated_feature_indices = (
                self._increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(
                    rows=rows,
                    feature_indices_to_inventory_line_numbers=tuple(
                        feature_indices_to_inventory_line_numbers
                    ),
                    index_to_assign=index_to_assign,
                )
            )

            for feature_index_and_line_number in feature_indices_to_inventory_line_numbers:
                if feature_index_and_line_number[KEY_FOR_FEATURE_INDEX] == index_to_assign:
                    line_number_of_new_feature = feature_index_and_line_number[KEY_FOR_LINE_NUMBER]

        row_with_new_feature = tuple(
            [
                {
                    KEY_FOR_ID: id_of_new_feature,
                    KEY_FOR_ENGLISH: new_feature_en[0].upper() + new_feature_en[1:],
                    KEY_FOR_RUSSIAN: new_feature_ru[0].upper() + new_feature_ru[1:],
                    "description_formatted_en": "",
                    "description_formatted_ru": "",
                    "is_multiselect": "",
                    "not_applicable_if": "",
                    "schema_sections": "",
                }
            ]
        )

        rows_with_new_value_inserted = (
            rows_with_updated_feature_indices[:line_number_of_new_feature]
            + row_with_new_feature
            + rows_with_updated_feature_indices[line_number_of_new_feature:]
        )

        write_csv(
            rows_with_new_value_inserted,
            path_to_file=self.output_file_with_features,
            overwrite=True,
            delimiter=",",
        )

        print(
            (
                f"\nAdding feature {id_of_new_feature} ({new_feature_en} / {new_feature_ru}) to"
                " list of features"
            ),
            end=" ",
        )

        return id_of_new_feature

    def _add_values_of_new_feature_to_inventory_of_listed_values(
        self,
        feature_id: str,
        listed_values_to_add: list[dict[str, str]],
    ) -> None:
        """
        Add values of the new feature to the inventory of listed values.
        """

        id_of_category_where_feature_is_inserted = extract_category_id(feature_id)

        rows_to_add_to_file_with_listed_values = []

        for i, new_listed_value in enumerate(listed_values_to_add, start=1):
            value_id = f"{feature_id}{ID_SEPARATOR}{i}"
            print(f"Value ID {value_id} - {new_listed_value[KEY_FOR_RUSSIAN]} will be added")
            rows_to_add_to_file_with_listed_values.append(
                {
                    KEY_FOR_ID: value_id,
                    KEY_FOR_FEATURE_ID: feature_id,
                    KEY_FOR_ENGLISH: new_listed_value[KEY_FOR_ENGLISH],
                    KEY_FOR_RUSSIAN: new_listed_value[KEY_FOR_RUSSIAN],
                    "description_formatted_en": "",
                    "description_formatted_ru": "",
                }
            )

        rows_before_insertion = read_dicts_from_csv(self.input_file_with_listed_values)

        line_number_where_insertion_starts = 0

        line_number_to_insert_before_is_found = False

        for i, row in enumerate(rows_before_insertion):
            if (
                extract_category_id(row[KEY_FOR_FEATURE_ID])
                != id_of_category_where_feature_is_inserted
            ):
                continue  # ignore all other categories

            if row[KEY_FOR_ID] == rows_to_add_to_file_with_listed_values[0][KEY_FOR_ID]:
                line_number_where_insertion_starts = i
                line_number_to_insert_before_is_found = True

            feature_index_of_current_row = extract_feature_index(row[KEY_FOR_FEATURE_ID])
            value_index_of_current_row = extract_value_index(row[KEY_FOR_ID])

            if feature_index_of_current_row >= extract_feature_index(feature_id):
                # if feature index of the current value row is equal or more than the index of feature we are adding
                # then increment feature index of the current row in both feature ID and value ID
                row[KEY_FOR_FEATURE_ID] = (
                    f"{id_of_category_where_feature_is_inserted}{ID_SEPARATOR}{feature_index_of_current_row + 1}"
                )
                row[KEY_FOR_ID] = (
                    f"{row[KEY_FOR_FEATURE_ID]}{ID_SEPARATOR}{value_index_of_current_row}"
                )

            if not line_number_to_insert_before_is_found:
                line_number_where_insertion_starts = i + 1
                # This is necessary in case when new values are added to the end of the category.
                # If we leave line_number_where_insertion_starts to be equal to i,
                # then adding values will start at penultimate position of the feature
                # resulting in e.g. order C-3-1, C-3-2, C-3-3, C-2-5

        rows_after_insertion = (
            rows_before_insertion[:line_number_where_insertion_starts]
            + rows_to_add_to_file_with_listed_values
            + rows_before_insertion[line_number_where_insertion_starts:]
        )

        write_csv(
            rows=rows_after_insertion,
            path_to_file=self.output_file_with_listed_values,
            overwrite=True,
            delimiter=",",
        )

        print(f"\nAdding new values in {feature_id} to file with listed values")

    def _add_feature_to_feature_profiles(
        self,
        feature_id: str,
        feature_ru: str,
    ) -> None:
        """
        Add feature to feature profiles. not_stated will be the value of the vew feature in each profile.
        """

        id_of_category_where_feature_is_inserted = extract_category_id(feature_id)

        row_to_add = {
            KEY_FOR_FEATURE_ID: feature_id,
            KEY_FOR_RUSSIAN_NAME_OF_FEATURE: feature_ru,
            KEY_FOR_VALUE_TYPE: "not_stated",
            KEY_FOR_VALUE_ID: "",
            KEY_FOR_RUSSIAN_NAME_OF_VALUE: "",
            KEY_FOR_RUSSIAN_COMMENT: "",
            KEY_FOR_ENGLISH_COMMENT: "",
        }

        for file in self.input_feature_profiles:

            rows_before_insertion = read_dicts_from_csv(file)

            line_number_where_row_will_be_inserted = 0

            line_number_to_insert_before_is_found = False

            for i, row in enumerate(rows_before_insertion):
                if (
                    extract_category_id(row[KEY_FOR_FEATURE_ID])
                    != id_of_category_where_feature_is_inserted
                ):
                    continue

                if row[KEY_FOR_FEATURE_ID] == row_to_add[KEY_FOR_FEATURE_ID]:
                    line_number_where_row_will_be_inserted = i
                    line_number_to_insert_before_is_found = True

                feature_index_of_current_row = extract_feature_index(row[KEY_FOR_FEATURE_ID])

                if feature_index_of_current_row >= extract_feature_index(feature_id):
                    # Same as in the previous method
                    row[KEY_FOR_FEATURE_ID] = (
                        f"{id_of_category_where_feature_is_inserted}{ID_SEPARATOR}{feature_index_of_current_row + 1}"
                    )

                    if row[KEY_FOR_VALUE_TYPE] == "listed":
                        row[KEY_FOR_VALUE_ID] = (
                            f"{row[KEY_FOR_FEATURE_ID]}{ID_SEPARATOR}{extract_value_index(row[KEY_FOR_VALUE_ID])}"
                        )

                if not line_number_to_insert_before_is_found:
                    line_number_where_row_will_be_inserted = i + 1

            rows_after_insertion = (
                rows_before_insertion[:line_number_where_row_will_be_inserted]
                + [row_to_add]
                + rows_before_insertion[line_number_where_row_will_be_inserted:]
            )

            write_csv(
                rows=rows_after_insertion,
                path_to_file=self.output_dir_with_feature_profiles / file.name,
                overwrite=True,
                delimiter=",",
            )

        print(f"\nAdding feature {feature_id} to feature profiles with value type" " 'not_stated'")

    @staticmethod
    def _increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(
        rows: list[dict[str, str]],
        feature_indices_to_inventory_line_numbers: tuple[dict[str, int], ...],
        index_to_assign: int,
    ) -> tuple[dict[str, str], ...]:
        """
        Increases by 1 index of every feature that will come after the feature passed for insertion.

        Returns tuple of dictionaries with incremented indices and line numbers.
        """

        rows_with_incremented_indices = rows[:]
        for feature_index_and_line_number in feature_indices_to_inventory_line_numbers:
            if feature_index_and_line_number[KEY_FOR_FEATURE_INDEX] < index_to_assign:
                continue
            row_where_id_must_be_incremented = feature_index_and_line_number[KEY_FOR_LINE_NUMBER]
            feature_id_to_increment = rows_with_incremented_indices[
                row_where_id_must_be_incremented
            ][KEY_FOR_ID]
            rows_with_incremented_indices[row_where_id_must_be_incremented][KEY_FOR_ID] = (
                f"{extract_category_id(feature_id_to_increment)}{ID_SEPARATOR}"
                f"{extract_feature_index(feature_id_to_increment) + 1}"
            )

        return tuple(rows_with_incremented_indices)

    # @staticmethod
    # def insert_rows(
    #     rows_before_insertion: list[dict[str, str]],
    #     rows_to_add: list[dict[str, str]],
    #     category_id: str,
    #     feature_id_to_add_after: Optional[str],
    # ) -> list[dict[str, str]]:
    #     rows = rows_before_insertion[:]

    #     if feature_id_to_add_after is None:
    #         for row_index, row in enumerate(rows):
    #             if (
    #                 row[KEY_FOR_FEATURE_ID].split(ID_SEPARATOR)[0] > category_id
    #                 or row[KEY_FOR_FEATURE_ID] == AUX_ROW_MARKER
    #             ):
    #                 return rows[:row_index] + rows_to_add + rows[row_index:]
    #         else:  # we have reached end of file
    #             return rows + rows_to_add
    #     else:
    #         found_feature_to_add_after = False
    #         for row_index, row in enumerate(rows):
    #             if (
    #                 row[KEY_FOR_FEATURE_ID] == feature_id_to_add_after
    #                 and not found_feature_to_add_after
    #             ):
    #                 # found beginning of block of values for relevant feature
    #                 found_feature_to_add_after = True
    #             elif (
    #                 row[KEY_FOR_FEATURE_ID] != feature_id_to_add_after
    #                 and found_feature_to_add_after
    #             ):
    #                 # found end of block
    #                 return rows[:row_index] + rows_to_add + rows[row_index:]
    #         else:
    #             return rows + rows_to_add


if __name__ == "__main__":
    FeatureAdder().add_feature(
        category_id="",
        feature_en="",
        feature_ru="",
        listed_values_to_add=[],
    )
