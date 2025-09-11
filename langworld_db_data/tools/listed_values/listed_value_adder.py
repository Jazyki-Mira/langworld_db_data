import logging
logging.basicConfig(level=logging.DEBUG)

from pathlib import Path
from typing import Optional, Union

from tinybear.csv_xls import read_dicts_from_csv, write_csv

from langworld_db_data.constants.literals import ATOMIC_VALUE_SEPARATOR
from langworld_db_data.tools.common.adder import Adder
from langworld_db_data.tools.common.ids.compose import compose_value_id_based_on_feature_id
from langworld_db_data.tools.common.ids.extract import extract_feature_id, extract_value_index

KEY_FOR_FEATURE_VALUE_INDEX = "index"
KEY_FOR_LINE_NUMBER = "line number"


logger = logging.getLogger(__name__)


class ListedValueAdderError(Exception):
    pass


class ListedValueAdder(Adder):

    def add_listed_value(
        self,
        feature_id: str,
        new_value_en: str,
        new_value_ru: str,
        custom_values_to_rename: Optional[list[str]] = None,
        index_to_assign: Union[int, None] = None,
        description_formatted_en: Optional[str] = None,
        description_formatted_ru: Optional[str] = None,
    ) -> None:
        """
        Consists of four major steps:
        1. Validate arguments
        2. Create ID for new value
        3. Add listed value to inventory
        4. Update feature profiles
        """
        args_to_validate = {
            "feature_id": feature_id,
            "value_en": new_value_en,
            "value_ru": new_value_ru,
            "index_to_assign": index_to_assign,
        }
        logger.debug(f"Validating args: {args_to_validate.keys()}.")
        self._validate_args(
            feature_or_value="value",
            args_to_validate=args_to_validate,
        )

        logger.debug("Generating ID for new value.")
        value_id = self._make_id_for_new_feature_or_value(
            category_or_feature="feature",
            category_or_feature_id=feature_id,
            index_to_assign=index_to_assign,
        )

        logger.debug(f"Adding new value with ID {value_id} "
                     "to the inventory of listed values.")
        self._add_listed_value_to_inventory_of_listed_values(
            value_id=value_id,
            feature_id=feature_id,
            new_value_en=new_value_en,
            new_value_ru=new_value_ru,
            description_formatted_en=description_formatted_en,
            description_formatted_ru=description_formatted_ru,
        )

        logger.debug("Rewriting feature profiles with insertion "
                     f"of new value {value_id} where necessary.")
        self._update_value_ids_and_types_in_feature_profiles_if_necessary(
            feature_id=feature_id,
            value_id=value_id,
            value_ru=new_value_ru,
            custom_values_to_rename=custom_values_to_rename,
        )

    def _add_listed_value_to_inventory_of_listed_values(
        self,
        value_id: str,
        feature_id: str,
        new_value_en: str,
        new_value_ru: str,
        description_formatted_en: Optional[str] = None,
        description_formatted_ru: Optional[str] = None,
    ) -> None:

        args = {
            "id": value_id,
            "feature_id": feature_id,
            "en": new_value_en,
            "ru": new_value_ru,
            "description_formatted_en": description_formatted_en,
            "description_formatted_ru": description_formatted_ru,
        }

        logger.debug("Generating row with new value for the inventory.")
        new_row = self._compose_new_row(
            feature_or_value="value",
            args=args,
        )
        logger.debug(f"New row: {new_row}.")

        logger.debug("Finding line number in the inventory where "
                     "the new row will be inserted.")
        line_number_to_insert_into = self._get_line_number_where_to_insert(
            feature_or_value="value",
            new_feature_or_value_id=value_id,
        )

        logger.debug(f"Inserting new row at line number {line_number_to_insert_into}.")
        self._insert_new_row_at_given_line_number(
            new_row=new_row,
            line_number_to_insert_into=line_number_to_insert_into,
            file_to_insert_into=self.input_file_with_listed_values,
            feature_or_value="value",
        )

        logger.debug("Aligning indices of values within the same feature "
                     "which are equal or greater than the index "
                     "of new value.")
        self._align_indices_of_features_or_values_that_come_after_inserted_one(
            input_filepath=self.output_file_with_listed_values,
            output_filepath=self.output_file_with_listed_values,
            line_number_of_insertion=line_number_to_insert_into,
        )

    def _update_value_ids_and_types_in_feature_profiles_if_necessary(
        self,
        feature_id: str,
        value_id: str,
        value_ru: str,
        custom_values_to_rename: Optional[list[str]] = None,
    ) -> None:
        """
        Calculate line number of the feature to which we are
        adding the new value. It is guaranteed that in all feature
        profiles this line number will be the same.

        Iterate through all feature profiles and check only the
        rows with this exact line number. Increment value ID of
        this feature or replace custom value with the listed
        value that we are adding, if necessary.
        """
        line_number_of_row_to_check = self._find_line_number_of_feature_in_feature_profile(
            feature_profile=self.input_feature_profiles[0],
            feature_id=feature_id,
        )

        for feature_profile in self.input_feature_profiles:

            self._update_value_id_and_type_in_one_feature_profile_if_necessary(
                feature_profile=feature_profile,
                line_number_of_row_to_check=line_number_of_row_to_check,
                value_id=value_id,
                value_ru=value_ru,
                custom_values_to_rename=custom_values_to_rename,
            )

    def _find_line_number_of_feature_in_feature_profile(
        self,
        feature_profile: Path,
        feature_id: str,
    ) -> int:
        """
        This is done in order to reduce iterations through
        feature profile rows that are irrelevant to adding
        the specific new listed value.
        """
        rows = read_dicts_from_csv(path_to_file=feature_profile)

        for i, row in enumerate(rows):
            if row["feature_id"] != feature_id:
                continue

            return i

    def _update_value_id_and_type_in_one_feature_profile_if_necessary(
        self,
        feature_profile: Path,
        line_number_of_row_to_check: int,
        value_id: str,
        value_ru: str,
        custom_values_to_rename: Optional[list[str]] = None,
    ) -> None:
        """
        General method for updating value IDs in feature profiles.

        First, expand the list of custom values to rename: add Russian name
        of new value to it, then generate variants of each of the present
        custom values with / without full stop and with / without
        capitalization of the first letter, add all variants to the list and
        remove repetitions.

        Then we work only with feature to which we are adding a new value.

        Second, if in the given feature profile this feature has a listed
        value, then perhaps its ID needs to be incremented. Do it if
        necessary.

        Third, if in the given feature profile this feature has a custom
        value, then it mae be necessary to replace it with the new listed
        value.
        """
        # Add value_ru and its variants with capital letter and
        # with / without full stop to the list of custom names
        if custom_values_to_rename is None:
            custom_values_to_rename = []
        custom_values_to_rename_with_all_their_variants = []
        custom_values_to_rename.append(value_ru)
        for value in custom_values_to_rename:
            variants_of_value = self._generate_variants_of_russian_value_name(value)
            for variant in variants_of_value:
                custom_values_to_rename_with_all_their_variants.append(variant)

        # Remove repetitions in custom_values_to_rename
        custom_values_to_rename_with_all_their_variants = list(
            set(custom_values_to_rename_with_all_their_variants)
        )

        rows = read_dicts_from_csv(feature_profile)

        is_multiselect = ATOMIC_VALUE_SEPARATOR in rows[line_number_of_row_to_check]["value_id"]

        if rows[line_number_of_row_to_check]["value_type"] == "listed":

            if is_multiselect:
                rows[line_number_of_row_to_check] = (
                    self._increment_value_id_in_line_number_to_check_if_necessary(
                        row=rows[line_number_of_row_to_check],
                        value_id=value_id,
                    )
                )

            rows[line_number_of_row_to_check] = (
                self._increment_value_id_in_line_number_to_check_if_necessary(
                    row=rows[line_number_of_row_to_check],
                    value_id=value_id,
                )
            )

        elif rows[line_number_of_row_to_check]["value_type"] == "custom":

            rows[line_number_of_row_to_check] = (
                self._mark_value_type_as_listed_and_rename_it_if_necessary(
                    row=rows[line_number_of_row_to_check],
                    new_value_ru=value_ru,
                    value_id=value_id,
                    custom_values_to_rename=custom_values_to_rename_with_all_their_variants,
                )
            )

        write_csv(
            rows=rows,
            path_to_file=self.output_dir_with_feature_profiles / feature_profile.name,
            delimiter=",",
            overwrite=True,
        )

    def _increment_value_id_in_line_number_to_check_if_necessary(
        self,
        row: dict[str, str],
        value_id: str,
    ) -> dict[str, str]:
        """
        If value ID of the given row is equal to the ID of new value
        or is greater than it, then it must be incremented.
        """
        value_id_of_row_to_check = row["value_id"]
        value_index_to_check = int(extract_value_index(value_id_of_row_to_check))
        if value_index_to_check >= int(extract_value_index(value_id)):
            row["value_id"] = compose_value_id_based_on_feature_id(
                feature_id=extract_feature_id(value_id_of_row_to_check),
                value_index=value_index_to_check + 1,
            )

        return row
    
    def _increment_value_id_in_line_number_to_check_if_necessary_for_multiselect_values(
        self,
        row: dict[str, str],
        value_id: str,
    ) -> dict[str, str]:
        
        value_id_of_row_to_check = row["value_id"]
        atomic_value_ids = value_id_of_row_to_check.split(ATOMIC_VALUE_SEPARATOR)
        logger.debug(f"The value IDs {atomic_value_ids} will be checked.")
        for i in range(len(atomic_value_ids)):
            value_index_of_atomic_id = int(extract_value_index(atomic_value_ids[i]))
            logger.debug(f"Value ID {atomic_value_ids[i]} has value index {value_index_of_atomic_id}.")
            if value_index_of_atomic_id >= int(extract_value_index(value_id)):
                atomic_value_ids[i] = compose_value_id_based_on_feature_id(
                    feature_id=extract_feature_id(atomic_value_ids[i]),
                    value_index=value_index_of_atomic_id + 1,
                )
                logger.debug(f"New atomic ID is {atomic_value_ids[i]}.")

        logger.debug(f"New list of atomic value IDs is {atomic_value_ids}.")
        row["value_id"] = ATOMIC_VALUE_SEPARATOR.join(atomic_value_ids)

        return row

    def _mark_value_type_as_listed_and_rename_it_if_necessary(
        self,
        row: dict[str, str],
        new_value_ru: str,
        value_id: str,
        custom_values_to_rename: list[str],
    ) -> dict[str, str]:
        """
        If Russian name of value in given row is in the list
        of custom names that must be turned into listed, replace
        this name with the new Russian name of value, change its type
        to listed and enter its ID.
        """
        if row["value_ru"].strip() in custom_values_to_rename:

            row["value_ru"] = new_value_ru
            row["value_id"] = value_id
            row["value_type"] = "listed"

        return row

    def _generate_variants_of_russian_value_name(
        self,
        value_name: str,
    ) -> set[str]:
        """
        Create set of the following variants of Russian name of value:
        - starts with capital letter, ends with full stop,
        - starts with capital letter, does not end with full stop,
        - starts with small letter, ends with full stop,
        - starts with small letter, does not end with full stop.

        Set was chosen as output type because order of variants is not
        important.
        """
        value_name = value_name.strip()

        if value_name[0].isupper():
            converse_variant_of_value_name = f"{value_name[0].lower()}{value_name[1:]}"
        else:
            converse_variant_of_value_name = f"{value_name[0].upper()}{value_name[1:]}"

        variants = [value_name, converse_variant_of_value_name]

        if value_name.endswith("."):
            variants.append(value_name[:-1])
            variants.append(converse_variant_of_value_name[:-1])
        else:
            variants.append(f"{value_name}.")
            variants.append(f"{converse_variant_of_value_name}.")

        return set(variants)


if __name__ == "__main__":
    ListedValueAdder().add_listed_value(
        feature_id="",
        new_value_en="",
        new_value_ru="",
    )  # pragma: no cover
