import logging
logging.basicConfig(level=logging.DEBUG)

from typing import Union

from tinybear.csv_xls import (
    read_column_from_csv,
    read_dicts_from_csv,
    write_csv,
)
from tinybear.txt import remove_extra_space

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
from langworld_db_data.tools.common.adder import Adder
from langworld_db_data.tools.common.ids.extract import (
    extract_category_id,
    extract_feature_index,
    extract_value_index,
)

KEY_FOR_FEATURE_INDEX = "index"
KEY_FOR_LINE_NUMBER = "line number"


logger = logging.getLogger(__name__)


class FeatureAdderError(Exception):
    pass


class FeatureAdder(Adder):

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
        category_id, feature_en, feature_ru = _(category_id), _(feature_en), _(feature_ru)

        args_to_validate = {
            "category_id": category_id,
            "feature_en": feature_en,
            "feature_ru": feature_ru,
            "listed_values_to_add": listed_values_to_add,
            "index_to_assign": index_to_assign,
        }
        logger.debug(f"Validating args: {args_to_validate.keys()}")
        self._validate_args(
            feature_or_value="feature",
            args_to_validate=args_to_validate,
        )

        logger.debug("Generating ID for new feature.")
        feature_id = self._make_id_for_new_feature_or_value(
            category_or_feature="category",
            category_or_feature_id=category_id,
            index_to_assign=index_to_assign,
        )

        logger.debug(f"Adding new feature with ID {feature_id} "
                     "to the inventory of features.")
        self._add_feature_to_inventory_of_features(
            feature_id=feature_id,
            category_id=category_id,
            new_feature_en=feature_en,
            new_feature_ru=feature_ru,
        )

        logger.debug(f"Adding values of new feature with ID {feature_id} "
                     "to the inventory of listed_values.")
        self._add_values_of_new_feature_to_inventory_of_listed_values(
            feature_id=feature_id,
            listed_values_to_add=listed_values_to_add,
        )

        logger.debug(f"Adding new feature with ID {feature_id} "
                     "to feature profiles.")
        self._add_feature_to_feature_profiles(
            feature_id=feature_id,
            feature_ru=feature_ru,
        )

    def _add_feature_to_inventory_of_features(
        self,
        feature_id: str,
        category_id: str,
        new_feature_en: str,
        new_feature_ru: str,
    ) -> None:
        """
        Add new feature to the inventory of features. Return ID of new feature.

        index_to_assign means number that must be assigned to the new feature within the category, ex. 13 for A-13.
        If no index_to_assign is given, the new feature will be added as the last one in the category.
        index_to_assign must be greater than 0.
        """

        args = {
            "id": feature_id,
            "category_id": category_id,
            "en": new_feature_en,
            "ru": new_feature_ru,
        }

        logger.debug("Generating row with new feature for the inventory.")
        new_row = self._compose_new_row(
            feature_or_value="feature",
            args=args,
        )
        logger.debug(f"New row: {new_row}.")

        logger.debug("Finding line number in the inventory where "
                     "the new row will be inserted.")
        line_number_to_insert_into = self._get_line_number_where_to_insert(
            feature_or_value="feature",
            new_feature_or_value_id=feature_id,
        )

        logger.debug(f"Inserting new row at line number {line_number_to_insert_into}.")
        self._insert_new_row_at_given_line_number(
            new_row=new_row,
            line_number_to_insert_into=line_number_to_insert_into,
            file_to_insert_into=self.input_file_with_features,
            feature_or_value="feature",
        )

        logger.debug("Aligning indices of features within the same category "
                     "which are equal or greater than the index "
                     "of new feature.")
        self._align_indices_of_features_or_values_that_come_after_inserted_one(
            input_filepath=self.output_file_with_features,
            output_filepath=self.output_file_with_features,
            line_number_of_insertion=line_number_to_insert_into,
        )

        # rows = read_dicts_from_csv(self.input_file_with_features)

        # if new_feature_en in [row[KEY_FOR_ENGLISH] for row in rows] or new_feature_ru in [
        #     row[KEY_FOR_RUSSIAN] for row in rows
        # ]:
        #     # note that this check should not be restricted to one feature category
        #     raise FeatureAdderError(
        #         "English or Russian feature name is already present in list of features"
        #     )

        # # To figure out the ID of the new feature (if index_to_assign is None)
        # # and to figure out the position of the new feature in inventory
        # # we should get feature indices and line numbers from rows.
        # # The same procedure is done by ListedValueAdder with a specific method.

        # feature_indices_to_inventory_line_numbers: list[dict[str, int]] = []

        # for i, row in enumerate(rows):
        #     if not category_id in row[KEY_FOR_ID]:
        #         continue

        #     feature_index = extract_feature_index(row[KEY_FOR_ID])
        #     feature_indices_to_inventory_line_numbers.append(
        #         {
        #             KEY_FOR_FEATURE_INDEX: feature_index,
        #             KEY_FOR_LINE_NUMBER: i,
        #         }
        #     )

        # # Check if passed index is valid
        # last_index_in_category = feature_indices_to_inventory_line_numbers[-1][
        #     KEY_FOR_FEATURE_INDEX
        # ]
        # # The range of numbers acceptable as index_to_assign consists of
        # # all the current indices in the given category and the next number after
        # # the current maximum. To include the maximum, we must add 1 to last_index_in_category.
        # # To include the number right after the maximum, we must again add 1.
        # # This results in adding 2 to the rightmost range border.
        # acceptable_indices_to_assign = set([None] + list(range(1, last_index_in_category + 2)))
        # # Here we add None to the list because None is the default value for appending
        # # feature to the end of category
        # if index_to_assign not in acceptable_indices_to_assign:
        #     raise ValueError(
        #         f"Invalid index_to_assign (must be between 1 and {last_index_in_category + 1}, "
        #         f"{index_to_assign} was given)"
        #     )

        # if index_to_assign in (
        #     None,
        #     last_index_in_category + 1,
        # ):  # new feature is being added after the last one
        #     id_of_new_feature = (
        #         f"{category_id}{ID_SEPARATOR}"
        #         f"{feature_indices_to_inventory_line_numbers[-1][KEY_FOR_FEATURE_INDEX] + 1}"
        #     )
        #     line_number_of_new_feature = (
        #         feature_indices_to_inventory_line_numbers[-1][KEY_FOR_LINE_NUMBER] + 1
        #     )
        #     rows_with_updated_feature_indices = tuple(rows.copy())

        # else:  # new feature being inserted in the middle
        #     id_of_new_feature = f"{category_id}{ID_SEPARATOR}{index_to_assign}"

        #     # Go through features of the category, ignore indices less than index_to_assign,
        #     # increment all other indices
        #     rows_with_updated_feature_indices = (
        #         self._increment_ids_whose_indices_are_equal_or_greater_than_index_to_assign(
        #             rows=rows,
        #             feature_indices_to_inventory_line_numbers=tuple(
        #                 feature_indices_to_inventory_line_numbers
        #             ),
        #             index_to_assign=index_to_assign,
        #         )
        #     )

        #     for feature_index_and_line_number in feature_indices_to_inventory_line_numbers:
        #         if feature_index_and_line_number[KEY_FOR_FEATURE_INDEX] == index_to_assign:
        #             line_number_of_new_feature = feature_index_and_line_number[KEY_FOR_LINE_NUMBER]

        # row_with_new_feature = tuple(
        #     [
        #         {
        #             KEY_FOR_ID: id_of_new_feature,
        #             KEY_FOR_ENGLISH: new_feature_en[0].upper() + new_feature_en[1:],
        #             KEY_FOR_RUSSIAN: new_feature_ru[0].upper() + new_feature_ru[1:],
        #             "description_formatted_en": "",
        #             "description_formatted_ru": "",
        #             "is_multiselect": "",
        #             "not_applicable_if": "",
        #             "schema_sections": "",
        #         }
        #     ]
        # )

        # rows_with_new_value_inserted = (
        #     rows_with_updated_feature_indices[:line_number_of_new_feature]
        #     + row_with_new_feature
        #     + rows_with_updated_feature_indices[line_number_of_new_feature:]
        # )

        # write_csv(
        #     rows_with_new_value_inserted,
        #     path_to_file=self.output_file_with_features,
        #     overwrite=True,
        #     delimiter=",",
        # )

        # print(
        #     (
        #         f"\nAdding feature {id_of_new_feature} ({new_feature_en} / {new_feature_ru}) to"
        #         " list of features"
        #     ),
        #     end=" ",
        # )


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


if __name__ == "__main__":
    FeatureAdder().add_feature(
        category_id="", feature_en="", feature_ru="", listed_values_to_add=[]
    )  # pragma: no cover
