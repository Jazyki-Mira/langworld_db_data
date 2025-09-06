from pathlib import Path
from typing import Literal, Union

from tinybear.csv_xls import read_column_from_csv, read_dicts_from_csv, write_csv

from langworld_db_data import ObjectWithPaths
from langworld_db_data.tools.common.ids.compose import (
    compose_feature_id,
    compose_value_id_based_on_feature_id,
    compose_value_id_from_scratch,
)
from langworld_db_data.tools.common.ids.extract import (
    extract_category_id,
    extract_feature_id,
    extract_feature_index,
    extract_last_index,
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

        if feature_or_value == "feature":
            self._check_validity_of_keys_in_passed_listed_values(
                listed_values_to_add=args_to_validate["listed_values_to_add"],
            )

        self._check_validity_of_index_to_assign(
            feature_or_value=feature_or_value,
            args_to_validate=args_to_validate,
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

    def _check_validity_of_index_to_assign(
        self,
        feature_or_value: FeatureOrValue,
        args_to_validate: dict[str, Union[str, int, None]],
    ) -> None:

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
        """
        Find line number in given CSV file where the new calue or feature must be inserted.

        This method tries to find a row that contains exactly the given value or feature
        ID. If it does not succeed, it acts as if the new value or feature must be appended
        to  the end of its feature or category respectively. It finds line number of last value
        in this feature or, alternatively, last feature in this category, adds 1 to it and
        returns the number as a result.
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
