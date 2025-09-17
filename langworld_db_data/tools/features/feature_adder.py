import logging

logging.basicConfig(level=logging.DEBUG)

from pathlib import Path
from typing import Union

from tinybear.csv_xls import (
    read_dicts_from_csv,
    write_csv,
)
from tinybear.txt import remove_extra_space

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
from langworld_db_data.tools.common.ids.compose import (
    compose_feature_id,
    compose_value_id_based_on_feature_id,
    compose_value_id_from_scratch,
)
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

        logger.debug(f"Adding new feature with ID {feature_id} " "to the inventory of features.")
        self._add_feature_to_inventory_of_features(
            feature_id=feature_id,
            category_id=category_id,
            new_feature_en=feature_en,
            new_feature_ru=feature_ru,
        )

        logger.debug(
            f"Adding values of new feature with ID {feature_id} "
            "to the inventory of listed_values."
        )
        self._add_values_of_new_feature_to_inventory_of_listed_values(
            feature_id=feature_id,
            listed_values_to_add=listed_values_to_add,
        )

        logger.debug(f"Adding new feature with ID {feature_id} to feature profiles.")
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

        logger.debug("Finding line number in the inventory where " "the new row will be inserted.")
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

        logger.debug(
            "Aligning indices of features within the same category "
            "which are equal or greater than the index "
            "of new feature."
        )
        self._align_indices_of_features_or_values_that_come_after_inserted_one(
            input_filepath=self.output_file_with_features,
            output_filepath=self.output_file_with_features,
            line_number_of_insertion=line_number_to_insert_into,
        )

    def _add_values_of_new_feature_to_inventory_of_listed_values(
        self,
        feature_id: str,
        listed_values_to_add: list[dict[str, str]],
    ) -> None:
        """
        Add values of the new feature to the inventory of listed values.
        """

        # First we need to insert the first value and then add other
        # values, if any, the same way as when we use ListedValueAdder.
        # Method for inserting first value is realized in Adder and will
        # move into FeatureAdder. Perhaps its is justified to move methods
        # for adding listed values into inventory from ListedValueAdder to
        # Adder, so that both FeatureAdder and ListedValueAdder would
        # inherit them.

        self._add_first_listed_value(
            feature_id=feature_id,
            first_value=listed_values_to_add[0],
        )
        logger.debug(
            "Successfully inserted the first value of new feature and aligned indices "
            "for values of subsequent features within the same category."
        )

        if len(listed_values_to_add) > 1:

            i = 2
            logger.debug("There are some more values to add.")
            logger.debug(f"Opening {self.output_file_with_listed_values}.")
            for listed_value in listed_values_to_add[1:]:
                logger.debug(i)
                value_id = self._make_id_for_new_feature_or_value(
                    category_or_feature="feature",
                    category_or_feature_id=feature_id,
                    index_to_assign=i,
                )
                logger.debug(f"New ID of listed value {listed_value['ru']} is {value_id}.")
                self._add_listed_value_to_inventory_of_listed_values(
                    value_id=value_id,
                    feature_id=feature_id,
                    new_value_en=listed_value["en"],
                    new_value_ru=listed_value["ru"],
                )
                i += 1

        # id_of_category_where_feature_is_inserted = extract_category_id(feature_id)

        # rows_to_add_to_file_with_listed_values = []

        # for i, new_listed_value in enumerate(listed_values_to_add, start=1):
        #     value_id = f"{feature_id}{ID_SEPARATOR}{i}"
        #     logger.info(f"Value ID {value_id} - {new_listed_value[KEY_FOR_RUSSIAN]} will be added")
        #     rows_to_add_to_file_with_listed_values.append(
        #         {
        #             KEY_FOR_ID: value_id,
        #             KEY_FOR_FEATURE_ID: feature_id,
        #             KEY_FOR_ENGLISH: new_listed_value[KEY_FOR_ENGLISH],
        #             KEY_FOR_RUSSIAN: new_listed_value[KEY_FOR_RUSSIAN],
        #             "description_formatted_en": "",
        #             "description_formatted_ru": "",
        #         }
        #     )

        # rows_before_insertion = read_dicts_from_csv(self.input_file_with_listed_values)

        # line_number_where_insertion_starts = 0

        # line_number_to_insert_before_is_found = False

        # for i, row in enumerate(rows_before_insertion):
        #     if (
        #         extract_category_id(row[KEY_FOR_FEATURE_ID])
        #         != id_of_category_where_feature_is_inserted
        #     ):
        #         continue  # ignore all other categories

        #     if row[KEY_FOR_ID] == rows_to_add_to_file_with_listed_values[0][KEY_FOR_ID]:
        #         line_number_where_insertion_starts = i
        #         line_number_to_insert_before_is_found = True

        #     feature_index_of_current_row = extract_feature_index(row[KEY_FOR_FEATURE_ID])
        #     value_index_of_current_row = extract_value_index(row[KEY_FOR_ID])

        #     if feature_index_of_current_row >= extract_feature_index(feature_id):
        #         # if feature index of the current value row is equal or more than the index of feature we are adding
        #         # then increment feature index of the current row in both feature ID and value ID
        #         row[KEY_FOR_FEATURE_ID] = (
        #             f"{id_of_category_where_feature_is_inserted}{ID_SEPARATOR}{feature_index_of_current_row + 1}"
        #         )
        #         row[KEY_FOR_ID] = (
        #             f"{row[KEY_FOR_FEATURE_ID]}{ID_SEPARATOR}{value_index_of_current_row}"
        #         )

        #     if not line_number_to_insert_before_is_found:
        #         line_number_where_insertion_starts = i + 1
        #         # This is necessary in case when new values are added to the end of the category.
        #         # If we leave line_number_where_insertion_starts to be equal to i,
        #         # then adding values will start at penultimate position of the feature
        #         # resulting in e.g. order C-3-1, C-3-2, C-3-3, C-2-5

        # rows_after_insertion = (
        #     rows_before_insertion[:line_number_where_insertion_starts]
        #     + rows_to_add_to_file_with_listed_values
        #     + rows_before_insertion[line_number_where_insertion_starts:]
        # )

        # write_csv(
        #     rows=rows_after_insertion,
        #     path_to_file=self.output_file_with_listed_values,
        #     overwrite=True,
        #     delimiter=",",
        # )

        logger.info(f"Adding new values in {feature_id} to file with listed values")

    def _add_first_listed_value(
        self,
        feature_id: str,
        first_value: dict[str, str],
    ) -> None:

        id_of_first_listed_value = compose_value_id_based_on_feature_id(
            feature_id=feature_id,
            value_index=1,
        )
        logger.debug(
            f"New value with ID {id_of_first_listed_value} will be added " "to the inventory."
        )

        args_of_first_value = {
            "id": id_of_first_listed_value,
            "feature_id": feature_id,
            "en": first_value["en"],
            "ru": first_value["ru"],
        }
        row_with_first_value = self._compose_new_row(
            feature_or_value="value",
            args=args_of_first_value,
        )
        logger.debug(f"Its row: {row_with_first_value}.")

        line_number_of_first_value = self._get_line_number_where_to_insert(
            feature_or_value="value",
            new_feature_or_value_id=id_of_first_listed_value,
        )
        logger.debug(f"It will be inserted into line number {line_number_of_first_value}.")

        self._insert_new_row_at_given_line_number(
            new_row=row_with_first_value,
            line_number_to_insert_into=line_number_of_first_value,
            file_to_insert_into=self.input_file_with_listed_values,
            feature_or_value="value",
        )
        self._increment_feature_indices_of_values_following_the_inserted_value_that_belongs_to_brand_new_feature(
            input_filepath=self.output_file_with_listed_values,
            output_filepath=self.output_file_with_listed_values,
            line_number_of_insertion=line_number_of_first_value,
        )

    def _increment_feature_indices_of_values_following_the_inserted_value_that_belongs_to_brand_new_feature(
        self,
        input_filepath: Path,
        output_filepath: Path,
        line_number_of_insertion: int,
        for_feature_profile: bool = False,
    ) -> None:
        """
        When we add a new feature we have to insert its first
        value into the listed values inventory. If the feature is
        not final in its category, then its first value will
        cause IDs of all subsequent values within the same category
        to increment their feature indices. E.g. if we have a category
        A consisting of features A-1 and A-2 (which has values A-2-1
        and A-2-2) and we want to add a new A-2 feature, then in listed
        values its value A-2-1 will cause the existing values A-2-1
        and A-2-2 to become A-3-1 and A-3-2. This is what this method
        does.

        For any other index increments, please use
        _align_indices_of_features_or_values_that_come_after_inserted_one.
        """
        lookup_column = "id"
        if for_feature_profile:
            lookup_column = "feature_id"

        rows = read_dicts_from_csv(
            path_to_file=input_filepath,
        )

        reference_id = rows[line_number_of_insertion][lookup_column]

        for row in rows[line_number_of_insertion + 1 :]:
            current_id = row[lookup_column]
            current_category_id = extract_category_id(current_id)
            if current_category_id != extract_category_id(reference_id):
                continue

            current_feature_index = extract_feature_index(current_id)
            current_feature_index_after_alignment = current_feature_index + 1
            row[lookup_column] = compose_value_id_from_scratch(
                category_id=current_category_id,
                feature_index=current_feature_index_after_alignment,
                value_index=extract_value_index(current_id),
            )
            row["feature_id"] = compose_feature_id(
                category_id=current_category_id,
                feature_index=current_feature_index_after_alignment,
            )

        write_csv(rows=rows, path_to_file=output_filepath, delimiter=",", overwrite=True)

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

        logger.info(
            f"Adding feature {feature_id} to feature profiles with value type" " 'not_stated'"
        )


if __name__ == "__main__":
    FeatureAdder().add_feature(
        category_id="", feature_en="", feature_ru="", listed_values_to_add=[]
    )  # pragma: no cover
