from pathlib import Path
from typing import Literal, Union

from tinybear.csv_xls import read_column_from_csv, read_dicts_from_csv, write_csv

from langworld_db_data import ObjectWithPaths
from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.tools.common.ids.compose import (
    compose_feature_id,
    compose_value_id_based_on_feature_id,
    compose_value_id_from_scratch,
)
from langworld_db_data.tools.common.ids.extract import (
    extract_category_id,
    extract_feature_id,
    extract_feature_index,
    extract_value_index,
)

FeatureOrValue = Literal["feature", "value"]
CategoryOrFeature = Literal["category", "feature"]


class AdderError(Exception):
    pass


class Adder(ObjectWithPaths):
    """
    In this class, all methods are applicable to both feature adding
    and listed value adding into both inventories and feature profiles.
    It contains the following methods:

    - Argument validation, works with all args of features and listed values
    that must be checked before adding. This method consists of calling several
    specific methods that check, for example, presence and uniqueness of passed
    characteristics of feature / listed value.

    - Getting tuple of existing indices. Necessary for automatic generation of
    feature / listed value ID and checking validity of passed index to assign.

    - Creating ID for new feature / listed value.

    - Composing a well-formed row with all relevant information. Inside this method,
    there are three so-called 'forms': one for features inventory, one for listed
    values inventory and one for feature profiles. The method takes the right form
    and fills it with characteristics of new feature / listed value.

    - Calculating line number where feature / value must be inserted in a specific
    document, be it an inventory or a feature profile.

    - Inserting the ready row into the calculated position in the document.

    - Indices alignment, replesented by two distinct methods. One is used when we
    add a new feature into features inventory or a feature profile AND when we add
    a new value into an existing feature in listed values inventory. Another one is
    used when we add a new feature and its first value must be inserted into the
    listed values inventory.
    """

    def _validate_args(
        self,
        feature_or_value: FeatureOrValue,
        args_to_validate: dict[str, Union[str, int, None]],
    ) -> None:
        """
        Validate arguments passed for adding new feature / listed value.

        Both features and values checks have quite similar logic:

        - All obligatory args must be present.

        - The category / feature, where the new feature / listed
        value will be added, must exist.

        - English and Russian names of feature / listed value must
        not be already present in inventories.

        - If a numeric index to assign is passed, it must also be
        checked, e.g. 32 is an invalid index if we are adding a
        feature to a category which has only 5 features. This
        validator also detects zero and negative numbers.

        For adding feature, we must also check well-formedness of
        the passed list of values.
        """

        self._check_that_all_obligatory_args_are_not_empty(
            feature_or_value=feature_or_value,
            args_to_validate=args_to_validate,
        )

        self._check_that_category_or_feature_where_to_add_exists(
            feature_or_value=feature_or_value,
            args_to_validate=args_to_validate,
        )

        self._check_that_en_and_ru_are_not_already_used_within_the_same_category_ro_feature(
            feature_or_value=feature_or_value,
            args_to_validate=args_to_validate,
        )

        self._check_validity_of_index_to_assign(
            feature_or_value=feature_or_value,
            args_to_validate=args_to_validate,
        )

        if feature_or_value == "feature":
            self._check_validity_of_keys_in_passed_listed_values(
                listed_values_to_add=args_to_validate["listed_values_to_add"],
            )

    def _check_that_all_obligatory_args_are_not_empty(
        self,
        feature_or_value: FeatureOrValue,
        args_to_validate: dict[str, Union[str, int, None]],
    ) -> None:
        """
        For a feature, we check the following args:
        - category ID,
        - English name,
        - Russian name,
        - list of values.

        For a listed value, we check:
        - feature ID,
        - English name,
        - Russian name.
        """
        feature_or_value_to_args_that_must_not_be_empty = {
            "feature": ("category_id", "feature_en", "feature_ru", "listed_values_to_add"),
            "value": ("feature_id", "value_en", "value_ru"),
        }

        args_that_must_not_be_empty = feature_or_value_to_args_that_must_not_be_empty[
            feature_or_value
        ]
        for arg in args_that_must_not_be_empty:
            if not args_to_validate[arg]:
                raise AdderError(
                    f"None of the following arguments - "
                    f"{feature_or_value_to_args_that_must_not_be_empty[feature_or_value]=}"
                    f" - must be empty, but an empty {arg} was given"
                )

    def _check_that_category_or_feature_where_to_add_exists(
        self,
        feature_or_value: FeatureOrValue,
        args_to_validate: dict[str, Union[str, int, None]],
    ) -> None:

        feature_or_value_to_arg_that_must_exist = {
            "feature": {
                "level_of_check": "Category",
                "file_to_check_against": self.file_with_categories,
                "arg": "category_id",
            },
            "value": {
                "level_of_check": "Feature",
                "file_to_check_against": self.input_file_with_features,
                "arg": "feature_id",
            },
        }

        level_of_check = feature_or_value_to_arg_that_must_exist[feature_or_value][
            "level_of_check"
        ]
        file_to_check_against = feature_or_value_to_arg_that_must_exist[feature_or_value][
            "file_to_check_against"
        ]
        name_of_arg_that_must_exist = feature_or_value_to_arg_that_must_exist[feature_or_value][
            "arg"
        ]
        arg_that_must_exist = args_to_validate[name_of_arg_that_must_exist]

        if arg_that_must_exist not in read_column_from_csv(
            path_to_file=file_to_check_against,
            column_name="id",
        ):
            raise AdderError(
                f"{level_of_check} ID {arg_that_must_exist} not found in file"
                f" {file_to_check_against.name}"
            )

    def _check_that_en_and_ru_are_not_already_used_within_the_same_category_ro_feature(
        self,
        feature_or_value: FeatureOrValue,
        args_to_validate: dict[str, Union[str, int, None]],
    ) -> None:
        """
        In the right inventory, read the columns with English
        and Russian names and try to find the passed names in
        them.
        """
        feature_or_value_to_args_that_must_not_be_occupied = {
            "feature": {
                "en": "feature_en",
                "ru": "feature_ru",
                "file_to_check_against": self.input_file_with_features,
                "upper_domain_id": "category_id",
                "function_for_getting_id_of_upper_domain": extract_category_id,
            },
            "value": {
                "en": "value_en",
                "ru": "value_ru",
                "file_to_check_against": self.input_file_with_listed_values,
                "upper_domain_id": "feature_id",
                "function_for_getting_id_of_upper_domain": extract_feature_id,
            },
        }

        args_that_must_not_be_occupied = feature_or_value_to_args_that_must_not_be_occupied[
            feature_or_value
        ]
        english_name = args_that_must_not_be_occupied["en"]
        russian_name = args_that_must_not_be_occupied["ru"]
        file_to_check_against = args_that_must_not_be_occupied["file_to_check_against"]
        extract_id_of_upper_domain = args_that_must_not_be_occupied["function_for_getting_id_of_upper_domain"]
        upper_domain_id = args_that_must_not_be_occupied["upper_domain_id"]

        rows = read_dicts_from_csv(path_to_file=file_to_check_against)
        for row in rows:
            if extract_id_of_upper_domain(row["id"]) != args_to_validate[upper_domain_id]:
                continue

            if row["en"] == args_to_validate[english_name] or row["ru"] == args_to_validate[russian_name]:
                raise AdderError(
                    f"English or Russian {feature_or_value} name is already present in {file_to_check_against.name}: "
                    f"{args_to_validate[english_name]}"
                )

    def _check_validity_of_keys_in_passed_listed_values(
        self,
        listed_values_to_add: list[dict[str, str]],
    ) -> None:
        """
        The list of values must contain only dicts
        each of which contains only two keys, 'en' and
        'ru' for English and Russian name of the new
        value. Any other structure causes an error.
        """
        for item in listed_values_to_add:
            if not ("en" in item and "ru" in item):
                raise AdderError(
                    f"Each listed value must have keys 'en' and 'ru'. Your value: {item}"
                )

    def _check_validity_of_index_to_assign(
        self,
        feature_or_value: FeatureOrValue,
        args_to_validate: dict[str, Union[str, int, None]],
    ) -> None:
        """
        In each category / feature, a list of valid indices includes
        indices of all of its features / listed values and the index
        next to the currently present biggest index, e.g. if category
        A has only features with IDs A-1, A-2 and A-3, thein its
        list of valid (= currently avaliable) indices is [1, 2, 3, 4]
        because we must also be able to add a new feature right after A-3.
        This method checks only numeric index_to_assign and does nothing
        if it is None. For a numeric index, it checks whether this
        index belongs to the tuple of valid indices and raises error
        if it does not.
        """
        if args_to_validate["index_to_assign"] is None:
            return None

        category_or_feature = None
        category_or_feature_id = ""

        if feature_or_value == "feature":
            category_or_feature = "category"
            category_or_feature_id = args_to_validate["category_id"]

        elif feature_or_value == "value":
            category_or_feature = "feature"
            category_or_feature_id = args_to_validate["feature_id"]
        
        print(category_or_feature)

        if not self._check_if_index_to_assign_is_in_list_of_applicable_indices(
            index_to_validate=args_to_validate["index_to_assign"],
            category_or_feature=category_or_feature,
            category_or_feature_id=category_or_feature_id,
        ):
            raise ValueError(
                f"Invalid index to assign: {args_to_validate['index_to_assign']}. "
                "It is either less than 1 or greater than the current allowed maximum."
            )

    def _check_if_index_to_assign_is_in_list_of_applicable_indices(
        self,
        index_to_validate: int,
        category_or_feature: CategoryOrFeature,
        category_or_feature_id: str,
    ) -> bool:
        avaliable_indices = self._get_tuple_of_currently_available_indices(
            category_or_feature=category_or_feature,
            category_or_feature_id=category_or_feature_id,
        )
        print(avaliable_indices)
        print(index_to_validate)

        return index_to_validate in avaliable_indices

    def _get_tuple_of_currently_available_indices(
        self,
        category_or_feature: CategoryOrFeature,
        category_or_feature_id: str,
    ) -> tuple[int]:
        """
        Read features / listed values inventory, collect
        indices of all features / listed values in the given
        category / feature, and add the index that is next after
        the current maximum.

        This method is used in validating index_to_assign and
        generating index for feature / listed value if no
        index_to_assign is passed.
        """
        if category_or_feature == "category":
            file_to_check_against = self.input_file_with_features
            extract_last_index = extract_feature_index
        elif category_or_feature == "feature":
            file_to_check_against = self.input_file_with_listed_values
            extract_last_index = extract_value_index

        existing_indices = []

        rows = read_dicts_from_csv(
            path_to_file=file_to_check_against,
        )
        for row in rows:
            id = row["id"]
            if not id.startswith(f"{category_or_feature_id}{ID_SEPARATOR}"):
                continue
            existing_indices.append(extract_last_index(id))

        # Also append next index after current maximum
        existing_indices.append(existing_indices[-1] + 1)

        return tuple(existing_indices)

    def _make_id_for_new_feature_or_value(
        self,
        category_or_feature: CategoryOrFeature,
        category_or_feature_id: str,
        index_to_assign: Union[int, None],
    ) -> str:
        """
        Compose ID for a feature / listed value with
        numeric index_to_assign or without it.
        """
        if index_to_assign is None:
            existing_indices = self._get_tuple_of_currently_available_indices(
                category_or_feature=category_or_feature,
                category_or_feature_id=category_or_feature_id,
            )
            last_available_index = existing_indices[-1]
            if category_or_feature == "category":
                id_of_new_feature_or_value = compose_feature_id(
                    category_id=category_or_feature_id,
                    feature_index=last_available_index,
                )
            elif category_or_feature == "feature":
                id_of_new_feature_or_value = compose_value_id_based_on_feature_id(
                    feature_id=category_or_feature_id,
                    value_index=last_available_index,
                )
        else:
            if category_or_feature == "category":
                id_of_new_feature_or_value = compose_feature_id(
                    category_id=category_or_feature_id,
                    feature_index=index_to_assign,
                )
            elif category_or_feature == "feature":
                id_of_new_feature_or_value = compose_value_id_based_on_feature_id(
                    feature_id=category_or_feature_id,
                    value_index=index_to_assign,
                )
        return id_of_new_feature_or_value

    def _compose_new_row(
        self,
        feature_or_value: FeatureOrValue,
        args: dict[str, str],
        for_feature_profile: bool = False,
    ) -> dict[str, str]:
        """
        Take relevant form of row and fill it with
        args of new feature / value
        """
        feature_or_value_to_form_of_row = {
            "feature": {
                "for_inventory": {
                    "id": "",
                    "en": "",
                    "ru": "",
                    "description_formatted_en": "",
                    "description_formatted_ru": "",
                    "is_multiselect": "",
                    "not_applicable_if": "",
                    "schema_sections": "",
                },
                "for_feature_profile": {
                    "feature_id": "",
                    "feature_name_ru": "",
                    "value_type": "not_stated",
                    "value_id": "",
                    "value_ru": "",
                    "comment_ru": "",
                    "comment_en": "",
                    "page_numbers": "",
                },
            },
            "value": {
                "for_inventory": {
                    "id": "",
                    "feature_id": "",
                    "en": "",
                    "ru": "",
                    "description_formatted_en": "",
                    "description_formatted_ru": "",
                }
            },
        }

        if for_feature_profile:
            form_of_row = feature_or_value_to_form_of_row[feature_or_value]["for_feature_profile"]
        elif not for_feature_profile:
            form_of_row = feature_or_value_to_form_of_row[feature_or_value]["for_inventory"]

        for key in form_of_row.keys():
            if key not in args.keys():
                continue

            if args[key] is None:
                continue

            form_of_row[key] = args[key]

        return form_of_row

    def _get_line_number_where_to_insert(
        self,
        feature_or_value: FeatureOrValue,
        new_feature_or_value_id: str,
        for_feature_profile: bool = False,
    ) -> int:
        """
        Find line number in given CSV file where the new
        feature / listed value must be inserted.

        This method tries to find a row that contains exactly the given
        feature / listed value ID. If it does not succeed, it acts as if
        the new feature / listed value must be appended to the end of its
        category / feature. It finds line number of last value in this
        feature or, alternatively, last feature in this category, adds 1
        to it and returns the number as a result.
        """

        # Default values of two important arguments:
        lookup_column = "id"
        category_or_feature_id_of_new_feature_or_value = extract_category_id(
            new_feature_or_value_id
        )
        # Some of them might change depending on whether we work with a value or feature and
        # whether it must be inserted into a feature profile or into an inventory
        if feature_or_value == "value":
            rows = read_dicts_from_csv(path_to_file=self.input_file_with_listed_values)
            category_or_feature_id_of_new_feature_or_value = extract_feature_id(
                new_feature_or_value_id
            )
        elif for_feature_profile:
            feature_profiles = list(self.input_dir_with_feature_profiles.glob("*.csv"))
            rows = read_dicts_from_csv(path_to_file=feature_profiles[0])
            lookup_column = "feature_id"
        else:
            rows = read_dicts_from_csv(path_to_file=self.input_file_with_features)

        exact_line_number_is_found = False

        for i, row in enumerate(rows):

            if row[lookup_column] == new_feature_or_value_id:
                line_number_where_row_will_be_inserted = i
                exact_line_number_is_found = True
                break

            if category_or_feature_id_of_new_feature_or_value in row[lookup_column]:
                line_number_where_row_will_be_inserted = i

        if not exact_line_number_is_found:
            # In this case we have feature or value that must be appended at the end
            # of feature or category, but the previous loop returns line number of last
            # value in feature or last feature in category, respectively.
            # We should add right AFTER this line number, that is why the returned
            # line number is NOT exact and must be incremented.
            line_number_where_row_will_be_inserted += 1

        return line_number_where_row_will_be_inserted

    def _insert_new_row_at_given_line_number(
        self,
        new_row: dict[str, str],
        line_number_to_insert_into: int,
        file_to_insert_into: Path,
        feature_or_value: FeatureOrValue,
        for_feature_profile: bool = False,
    ) -> None:

        rows_before_insertion = read_dicts_from_csv(path_to_file=file_to_insert_into)
        rows_after_insertion = (
            rows_before_insertion[:line_number_to_insert_into]
            + [new_row]
            + rows_before_insertion[line_number_to_insert_into:]
        )

        if feature_or_value == "value":
            output_file = self.output_file_with_listed_values
        elif for_feature_profile:
            file_name = file_to_insert_into.name
            output_file = self.output_dir_with_feature_profiles / file_name
        else:
            output_file = self.output_file_with_features

        write_csv(
            rows=rows_after_insertion,
            path_to_file=output_file,
            delimiter=",",
            overwrite=True,
        )

    def _align_indices_of_features_or_values_that_come_after_inserted_one(
        self,
        input_filepath: Path,
        output_filepath: Path,
        line_number_of_insertion: int,
        for_feature_profile: bool = False,
    ) -> None:
        """
        When we add feature / listed value not to the end of
        category / feature, we have to align indices of
        features / listed values within the same category / feature
        which come after the inserted one. Their final indices
        must be incremented.

        This method does NOT work in cases when we add a new value
        into listed values inventory and the value belongs to a brand
        new feature not yet represented in the listed values
        inventory. For this case, please use
        _increment_feature_indices_of_values_following_the_inserted_value_that_belongs_to_brand_new_feature.
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
            if current_id != reference_id:
                continue

            elements_of_current_id = current_id.split("-")
            for i in range(1, len(elements_of_current_id)):
                elements_of_current_id[i] = int(elements_of_current_id[i])
            elements_of_current_id[-1] += 1
            for i in range(1, len(elements_of_current_id)):
                elements_of_current_id[i] = str(elements_of_current_id[i])
            current_id_after_alignment = "-".join(elements_of_current_id)
            row[lookup_column] = current_id_after_alignment
            reference_id = current_id_after_alignment

        write_csv(rows=rows, path_to_file=output_filepath, delimiter=",", overwrite=True)

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
        print(reference_id)

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
