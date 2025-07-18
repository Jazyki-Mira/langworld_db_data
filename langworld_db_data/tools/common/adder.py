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
    ) -> bool:
        """
        Validate arguments passed for adding new feature or value.

        For both features and values checks have quite similar logic, the main
        difference is that for feature we must also check the passed list of
        values.
        """

        # First: check that all obligatory args are not empty
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

        # Second: check the presence of category where the new feature
        # will be added or of feature where the new value will be added
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

        # Third: check that English and Russian names of new feature/value are
        # not already used by some other feature/value
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

        # Additional check for adding features only is checking well-formedness of
        # listed values to add
        if feature_or_value == "feature":
            for item in args_to_validate["listed_values_to_add"]:
                if not ("en" in item and "ru" in item):
                    raise AdderError(
                        f"{feature_or_value.title()} must have keys 'en' and 'ru'. Your value: {item}"
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
        args_of_new_feature_or_value: tuple[str],
        for_feature_profile: bool = False,
    ) -> dict[str, str]:
        pass

    def _get_line_number_where_to_insert(
        self,
        feature_or_value: FeatureOrValue,
        new_feature_or_value_id: str,
        for_feature_profile: bool = False,
    ) -> int:
        pass
