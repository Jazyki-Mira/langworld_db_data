from pathlib import Path

from langworld_db_data import ObjectWithPaths
from langworld_db_data.constants.literals import KEY_FOR_ID
from langworld_db_data.constants.paths import (
    FEATURE_PROFILES_DIR,
    FILE_WITH_CATEGORIES,
    FILE_WITH_LISTED_VALUES,
    FILE_WITH_NAMES_OF_FEATURES,
)
from langworld_db_data.tools.files.csv_xls import (
    read_column_from_csv,
    read_dicts_from_csv,
    remove_multiple_matching_rows_and_return_range_of_their_line_numbers,
    remove_one_matching_row_and_return_its_line_number,
    update_indices_after_given_line_number_if_necessary,
    write_csv,
)
from langworld_db_data.tools.value_ids.value_ids import extract_category_id


class FeatureRemoverError(Exception):
    pass


class FeatureRemover(ObjectWithPaths):
    def __init__(
        self,
        *,
        file_with_categories: Path = FILE_WITH_CATEGORIES,
        input_file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
        output_file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
        input_file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
        output_file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
        input_dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
        output_dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
    ):
        self.file_with_categories = file_with_categories
        self.input_file_with_features = input_file_with_features
        self.output_file_with_features = output_file_with_features
        self.input_file_with_listed_values = input_file_with_listed_values
        self.output_file_with_listed_values = output_file_with_listed_values
        self.input_dir_with_feature_profiles = input_dir_with_feature_profiles
        self.output_dir_with_feature_profiles = output_dir_with_feature_profiles

    def remove_feature(
        self,
        feature_id: str,
    ) -> None:
        """
        Remove feature from features inventory, from listed values inventory
        and from feature profiles.
        """

        if feature_id not in read_column_from_csv(
            path_to_file=self.input_file_with_features, column_name=KEY_FOR_ID
        ):
            raise FeatureRemoverError(
                f"Feature ID <{feature_id}> not found in file"
                f" {self.input_file_with_features.name}"
            )

        self._remove_from_inventory_of_features(feature_id=feature_id)
        self._remove_from_inventory_of_listed_values(feature_id=feature_id)
        self._remove_from_feature_profiles(feature_id=feature_id)

    def _remove_from_inventory_of_features(
        self,
        feature_id: str,
    ) -> None:

        rows = read_dicts_from_csv(
            path_to_file=self.input_file_with_features,
        )

        rows_with_removed_row, line_number_of_removed_row = (
            remove_one_matching_row_and_return_its_line_number(
                match_column_name="id", match_content=feature_id, rows=rows
            )
        )

        rows_with_removed_row_and_updated_indices = (
            update_indices_after_given_line_number_if_necessary(
                match_column_name="id",
                match_content=extract_category_id(feature_id),
                id_type_that_must_be_updated="feature",
                index_type_that_must_be_updated="feature",
                line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
                rows=rows_with_removed_row,
            )
        )

        write_csv(
            rows=rows_with_removed_row_and_updated_indices,
            path_to_file=self.output_file_with_features,
            overwrite=True,
            delimiter=",",
        )

    def _remove_from_inventory_of_listed_values(
        self,
        feature_id: str,
    ) -> None:

        rows = read_dicts_from_csv(
            path_to_file=self.input_file_with_listed_values,
        )

        rows_with_removed_rows, range_of_line_numbers_of_removed_rows = (
            remove_multiple_matching_rows_and_return_range_of_their_line_numbers(
                match_content=feature_id, rows=rows
            )
        )

        line_number_of_first_removed_value = range_of_line_numbers_of_removed_rows[0]

        category_id_where_feature_is_removed = extract_category_id(feature_id)

        rows_with_removed_rows_and_updated_value_indices = (
            update_indices_after_given_line_number_if_necessary(
                match_column_name="id",
                match_content=category_id_where_feature_is_removed,
                id_type_that_must_be_updated="value",
                index_type_that_must_be_updated="feature",
                line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
                rows=rows_with_removed_rows,
            )
        )

        rows_with_removed_rows_and_updated_feature_and_value_indices = (
            update_indices_after_given_line_number_if_necessary(
                match_column_name="feature_id",
                match_content=category_id_where_feature_is_removed,
                id_type_that_must_be_updated="feature",
                index_type_that_must_be_updated="feature",
                line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
                rows=rows_with_removed_rows_and_updated_value_indices,
            )
        )

        write_csv(
            rows=rows_with_removed_rows_and_updated_feature_and_value_indices,
            path_to_file=self.output_file_with_listed_values,
            overwrite=True,
            delimiter=",",
        )

    def _remove_from_feature_profiles(
        self,
        feature_id: str,
    ) -> None:

        feature_profiles = self.input_dir_with_feature_profiles.glob("*.csv")

        for feature_profile in feature_profiles:

            rows = read_dicts_from_csv(feature_profile)

            rows_with_removed_row, line_number_of_removed_row = (
                remove_one_matching_row_and_return_its_line_number(
                    match_column_name="feature_id", match_content=feature_id, rows=rows
                )
            )

            rows_with_removed_row_and_updated_indices = (
                update_indices_after_given_line_number_if_necessary(
                    match_column_name="feature_id",
                    match_content=extract_category_id(feature_id),
                    id_type_that_must_be_updated="feature",
                    index_type_that_must_be_updated="feature",
                    line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
                    rows=rows_with_removed_row,
                    rows_are_a_feature_profile=True,
                )
            )

            write_csv(
                rows=rows_with_removed_row_and_updated_indices,
                path_to_file=self.output_dir_with_feature_profiles / feature_profile.name,
                overwrite=True,
                delimiter=",",
            )
