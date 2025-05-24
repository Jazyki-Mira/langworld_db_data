from pathlib import Path
from typing import Literal

from langworld_db_data import ObjectWithPaths
from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.constants.paths import FILE_WITH_CATEGORIES, FILE_WITH_NAMES_OF_FEATURES
from langworld_db_data.tools.files.csv_xls import read_dicts_from_csv, write_csv
from langworld_db_data.tools.value_ids.value_ids import (
    extract_category_id,
    extract_feature_id,
    extract_feature_index,
    extract_value_index,
)


class FeatureRemoverError(Exception):
    pass


class FeatureRemover(ObjectWithPaths):
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

    def remove_feature(
        self,
        feature_id: str,
    ):
        """
        Consists of removing from features inventory, from listed values inventory
        and from feature profiles (same as in FeatureAdder).
        """
        self._remove_from_inventory_of_features(
            feature_id=feature_id,
        )
        self._remove_from_inventory_of_listed_values(
            feature_id=feature_id,
        )
        self._remove_from_feature_profiles(
            feature_id=feature_id,
        )

    def _remove_from_inventory_of_features(
        self,
        feature_id: str,
    ):
        """
        Two sub-tasks: remove line with target feature and update feature indices that follow it
        """

        rows = read_dicts_from_csv(
            path_to_file=self.input_file_with_features,
        )

        rows_with_removed_row, line_number_of_removed_row = (
            self._remove_one_matching_row_and_return_its_line_number(
                match_column_name="id", match_content=feature_id, rows=rows
            )
        )

        rows_with_removed_row_and_updated_indices = (
            self._update_indices_after_given_line_number_if_necessary(
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
    ):
        """
        Two sub-tasks: remove lines with target feature values and update feature indices
        of values that follow it
        """
        rows = read_dicts_from_csv(
            path_to_file=self.input_file_with_listed_values,
        )

        rows_with_removed_rows, range_of_line_numbers_of_removed_rows = (
            self._remove_multiple_matching_rows_and_return_range_of_their_line_numbers(
                match_content=feature_id, rows=rows
            )
        )

        line_number_of_first_removed_value = range_of_line_numbers_of_removed_rows[0]

        category_id_where_feature_is_removed = extract_category_id(feature_id)

        rows_with_removed_rows_and_updated_value_indices = (
            self._update_indices_after_given_line_number_if_necessary(
                match_column_name="id",
                match_content=category_id_where_feature_is_removed,
                id_type_that_must_be_updated="value",
                index_type_that_must_be_updated="feature",
                line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
                rows=rows_with_removed_rows,
            )
        )

        rows_with_removed_rows_and_updated_feature_and_value_indices = (
            self._update_indices_after_given_line_number_if_necessary(
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
    ):
        """
        Two sub-tasks: remove lines with target feature values and update feature indices
        of features and their values that follow it
        """
        feature_profiles = self.input_dir_with_feature_profiles.glob("*.csv")

        for feature_profile in feature_profiles:

            rows = read_dicts_from_csv(feature_profile)

            rows_with_removed_row, line_number_of_removed_row = (
                self._remove_one_matching_row_and_return_its_line_number(
                    match_column_name="feature_id", match_content=feature_id, rows=rows
                )
            )

            rows_with_removed_row_and_updated_indices = (
                self._update_indices_after_given_line_number_if_necessary(
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

    @staticmethod
    def _remove_one_matching_row_and_return_its_line_number(
        match_column_name: Literal["feature_id", "id"],
        match_content: str,
        rows: list[dict[str, str]],
    ) -> tuple[list[dict[str, str]], int]:
        """
        Remove exactly one row from given rows (be it an inventory or a feature profile)
        which contains specified ID.

        Return rows without the target row and the line number of the removed row.
        For example, if asked to remove A-2 from the list of A-1, A-2 and A-3,
        return the list of A-1 and A-3 and line number 1.
        match_column_name denotes the name of column where search must be performed.
        match_content is argument of type 'str'. The first row which displays it as an argument
        of the kind denoted by match_column_name will be removed.
        For removing more rows, please use _remove_multiple_rows_and_return_range_of_their_line_numbers.
        """
        # This method is written in such way that in the future it can be made universal
        # for all removers.

        line_number_of_row_to_remove = 0

        for i, row in enumerate(rows):
            if row[match_column_name] == match_content:
                line_number_of_row_to_remove = i
                break

        if line_number_of_row_to_remove == 0:
            raise Exception(
                f"Row with given properties not found. Perhaps match_content is invalid: {match_content}"
            )

        return (rows[:line_number_of_row_to_remove] + rows[line_number_of_row_to_remove + 1 :], i)

    @staticmethod
    def _remove_multiple_matching_rows_and_return_range_of_their_line_numbers(
        match_content: str,
        rows: list[dict[str, str]],
    ) -> tuple[list[dict[str, str]], tuple[int]]:
        """
        Remove more than one row from given rows (typically from listed values inventory)
        which contain specified ID.

        Return rows without the target rows and thea range of line number of the removed rows,
        that is a tuple with line number of the first removed row and the last removed row.
        For example, if asked to remove all A-2 values from the list of A-1-1, A-2-1, A-2-2, A-2-3 and A-3-1,
        return the list of A-1-1 and A-3-1 and line numbers 1 (initial) and 3 (final).
        match_content is argument of type 'str'. All the rows which contain it in their IDs will be removed.
        For removing exactly one row, please use _remove_one_row_and_return_its_line_number.
        """
        # This one is designed specifically for FeatureRemover because ListedValueRemover has only to remove one row at a time

        line_numbers_of_removed_rows = []

        for i, row in enumerate(rows):
            if row["feature_id"] == match_content:
                line_numbers_of_removed_rows.append(i)

        if len(line_numbers_of_removed_rows) == 0:
            raise Exception(
                f"Rows with given properties not found. Perhaps match_content is invalid: {match_content}"
            )

        first_line_number = line_numbers_of_removed_rows[0]
        last_line_number = line_numbers_of_removed_rows[-1]

        return (
            rows[:first_line_number] + rows[last_line_number + 1 :],
            (first_line_number, last_line_number),
        )

    @staticmethod
    def _update_indices_after_given_line_number_if_necessary(
        match_column_name: Literal["feature_id", "id"],
        match_content: str,
        id_type_that_must_be_updated: Literal["feature", "value"],
        index_type_that_must_be_updated: Literal["feature", "value"],
        line_number_after_which_rows_must_be_updated: int,
        rows: list[dict[str, str]],
        rows_are_a_feature_profile: bool = False,
    ) -> list[dict[str, str]]:
        """
        Decrement indices of features or values. Return rows with updated indices or intact rows if update is not necessary.

        Search rows with matching content and decrement feature or value indices in the given column.
        match_column_name denotes the name of column where search must be performed.
        match_content is argument of type 'str'. The first row which displays it as an argument
        of the kind denoted by match_column_name will be removed.
        index_type_that_must_be_updated can be either 'feature' or 'value'.
        Update is only performed on rows whose line number is equal or greater than line_number_after_which_rows_must_be_updated.
        If rows_are_a_feature_profile is True, the method also scans value types and decrements feature indices in listed value IDs.
        """
        # So far it is only used to decrement indices, but it can be slightly rewritten to do either decrement or increment

        nothing_is_changed = True

        for row in rows[line_number_after_which_rows_must_be_updated:]:

            if f"{match_content}{ID_SEPARATOR}" not in row[match_column_name]:
                continue

            current_feature_index = extract_feature_index(row[match_column_name])

            if id_type_that_must_be_updated == "value":
                if index_type_that_must_be_updated == "feature":
                    current_value_index = extract_value_index(row["id"])
                    row[match_column_name] = (
                        f"{match_content}{ID_SEPARATOR}{current_feature_index - 1}{ID_SEPARATOR}{current_value_index}"
                    )

                elif index_type_that_must_be_updated == "value":
                    row[match_column_name] = (
                        f"{match_content}{ID_SEPARATOR}{extract_value_index(row[match_column_name]) - 1}"
                    )
            elif id_type_that_must_be_updated == "feature":
                row[match_column_name] = (
                    f"{match_content}{ID_SEPARATOR}{current_feature_index - 1}"
                )

            if rows_are_a_feature_profile:
                if row["value_type"] == "listed":

                    current_value_index = extract_value_index(row["value_id"])
                    row["value_id"] = (
                        f"{match_content}{ID_SEPARATOR}{current_feature_index - 1}{ID_SEPARATOR}{current_value_index}"
                    )
            nothing_is_changed = False

        if nothing_is_changed:
            print("Warning: no rows have been changed.")
        else:
            print("Successfully updated IDs.")

        return rows
