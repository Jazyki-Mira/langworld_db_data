from pathlib import Path
from typing import Literal

from langworld_db_data import ObjectWithPaths
from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.constants.paths import FILE_WITH_CATEGORIES, FILE_WITH_NAMES_OF_FEATURES
from langworld_db_data.tools.files.csv_xls import read_dicts_from_csv, write_csv
from langworld_db_data.tools.value_ids.value_ids import extract_category_id


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
        self._remove_from_inventory_of_listed_values()
        self._remove_from_feature_profiles()

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

        rows_with_removed_line, line_number_of_removed_row = self._remove_one_matching_row_and_return_its_line_number(
            match_column_name="id", match_content=feature_id, rows=rows
        )

        rows_with_removed_line_and_updated_indices = (
            self._update_indices_after_given_line_number_if_necessary(
                match_column_name="id",
                match_content=extract_category_id(feature_id),
                line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
                rows=rows_with_removed_line,
            )
        )

        write_csv(
            rows=rows_with_removed_line_and_updated_indices,
            path_to_file=self.output_file_with_features,
            delimiter=",",
        )

    def _remove_from_inventory_of_listed_values():
        """
        Two sub-tasks: remove lines with target feature values and update feature indices
        of values that follow it
        """
        pass

    def _remove_from_feature_profiles():
        """
        Two sub-tasks: remove lines with target feature values and update feature indices
        of features and their values that follow it
        """
        pass

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
    ) -> tuple[list[dict[str, str]], list[int]]:
        """
        Remove more than one row from given rows (typically from listed values inventory)
        which contain specified ID.

        Return rows without the target row and range of line numbers of the removed rows.
        For example, if asked to remove all A-2 values from the list of A-1-1, A-2-1, A-2-2, A-2-3 and A-3-1,
        return the list of A-1-1 and A-3-1 and line numbers 1 (initial) and 3 (final).
        match_content is argument of type 'str'. All the rows which contain it in their IDs will be removed.
        For removing exactly one row, please use _remove_one_row_and_return_its_line_number.
        """
        range_of_line_numbers_of_removed_rows = []

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
    def _update_indices_after_given_line_number_if_necessary(
        match_column_name: Literal["feature_id", "id"],
        match_content: str,
        line_number_after_which_rows_must_be_updated: int,
        rows: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        pass
