from typing import Literal, Union

from tinybear.csv_xls import read_column_from_csv, read_dicts_from_csv

from langworld_db_data import ObjectWithPaths
from langworld_db_data.tools.common.ids.compose import (
    compose_feature_id,
    compose_value_id_based_on_feature_id,
)
from langworld_db_data.tools.common.ids.extract import (
    extract_feature_index,
    extract_value_index,
)

FeatureOrValue = Literal["feature", "value"]
CategoryOrFeature = Literal["category", "feature"]


class AdderError(Exception):
    pass


class Adder(ObjectWithPaths):

    def _validate_arguments(
        self,
        feature_or_value: FeatureOrValue,
        args_to_validate: dict[str, Union[str, int, None]],
    ) -> None:
        """
        Validate arguments passed for adding new feature or value.

        For both features and values checks have quite similar logic, the main
        difference is that for feature we must also check the passed list of
        values.
        """

        self._check_that_all_obligatory_args_are_not_empty(
            feature_or_value=feature_or_value,
            args_to_validate=args_to_validate,
        )

        self._check_that_category_or_feature_where_to_add_exists(
            feature_or_value=feature_or_value,
            args_to_validate=args_to_validate,
        )

        self._check_that_en_and_ru_are_not_already_used(
            feature_or_value=feature_or_value,
            args_to_validate=args_to_validate,
        )

        # Additional check for adding features only is checking well-formedness of
        # listed values to add
        if feature_or_value == "feature":
            self._check_validity_of_keys_in_passed_listed_values(
                listed_values_to_add=args_to_validate["listed_values_to_add"],
            )

        # Fourth: check validity of index_to_assign
        if args_to_validate["index_to_assign"] is not None:
            category_or_feature = None
            category_or_feature_id = ""

            if feature_or_value == "feature":
                category_or_feature = "category"
                category_or_feature_id = args_to_validate["category_id"]

            elif feature_or_value == "value":
                category_or_feature = "feature"
                category_or_feature_id = args_to_validate["feature_id"]

            if not self._check_if_index_to_assign_is_in_list_of_applicable_indices(
                index_to_validate=args_to_validate["index_to_assign"],
                category_or_feature=category_or_feature,
                category_or_feature_id=category_or_feature_id,
            ):
                raise ValueError(
                    f"Invalid index to assign: {args_to_validate['index_to_assign']}. "
                    "It is either less than 1 or greater than the current allowed maximum."
                )

    def _check_that_all_obligatory_args_are_not_empty(
        self,
        feature_or_value: FeatureOrValue,
        args_to_validate: dict[str, Union[str, int, None]],
    ) -> None:
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

    def _check_that_en_and_ru_are_not_already_used(
        self,
        feature_or_value: FeatureOrValue,
        args_to_validate: dict[str, Union[str, int, None]],
    ) -> None:
        feature_or_value_to_args_that_must_not_be_occupied = {
            "feature": {
                "en": "feature_en",
                "ru": "feature_ru",
                "file_to_check_against": self.input_file_with_features,
            },
            "value": {
                "en": "value_en",
                "ru": "value_ru",
                "file_to_check_against": self.input_file_with_listed_values,
            },
        }

        args_that_must_not_be_occupied = feature_or_value_to_args_that_must_not_be_occupied[
            feature_or_value
        ]
        english_name = args_that_must_not_be_occupied["en"]
        russian_name = args_that_must_not_be_occupied["ru"]
        file_to_check_against = args_that_must_not_be_occupied["file_to_check_against"]
        if args_to_validate[english_name] in read_column_from_csv(
            path_to_file=file_to_check_against,
            column_name="en",
        ) or args_to_validate[russian_name] in read_column_from_csv(
            path_to_file=file_to_check_against, column_name="ru"
        ):
            raise AdderError(
                f"English or Russian {feature_or_value} name is already present in {file_to_check_against.name}: "
                f"{args_to_validate[english_name]}"
            )

    def _check_validity_of_keys_in_passed_listed_values(
        self,
        listed_values_to_add: list[dict[str, str]],
    ) -> None:
        for item in listed_values_to_add:
            if not ("en" in item and "ru" in item):
                raise AdderError(
                    f"Each listed value must have keys 'en' and 'ru'. Your value: {item}"
                )

    def _check_if_index_to_assign_is_in_list_of_applicable_indices(
        self,
        index_to_validate: int,
        category_or_feature: CategoryOrFeature,
        category_or_feature_id: str,
    ) -> bool:

        existing_indices = self._get_tuple_of_currently_available_indices(
            category_or_feature=category_or_feature,
            category_or_feature_id=category_or_feature_id,
        )

        return index_to_validate in existing_indices

    def _get_tuple_of_currently_available_indices(
        self,
        category_or_feature: CategoryOrFeature,
        category_or_feature_id: str,
    ) -> tuple[int]:

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
            if not id.startswith(category_or_feature_id):
                continue
            existing_indices.append(extract_last_index(id))

        # Also append next index after current maximum
        existing_indices.append(existing_indices[-1] + 1)

        return tuple(existing_indices)

    def _make_id_for_new_feature_or_value(
        self,
        category_or_feature: CategoryOrFeature,
        category_or_feature_id: str,
        index_to_assign: int,
    ) -> str:

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

            form_of_row[key] = args[key]

        return form_of_row

    def _get_line_number_where_to_insert(
        self,
        feature_or_value: FeatureOrValue,
        new_feature_or_value_id: str,
        for_feature_profile: bool = False,
    ) -> int:
        pass
