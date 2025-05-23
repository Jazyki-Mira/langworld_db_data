from pathlib import Path
from typing import Literal

from langworld_db_data import ObjectWithPaths
from langworld_db_data.constants.paths import FILE_WITH_CATEGORIES, FILE_WITH_NAMES_OF_FEATURES
from langworld_db_data.tools.files.csv_xls import read_dicts_from_csv


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

        rows_with_removed_line = self._remove_one_row(
            match_column_name="id", match_content=feature_id, rows=rows
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
    def _remove_one_row_and_return_its_line_number(
        match_column_name: Literal["feature_id", "id"],
        match_content: str,
        rows: list[dict[str, str]],
    ) -> tuple[list[dict[str, str]], int]:
        """
        Removes exactly one row from given rows (be it an inventory or a feature profile)
        which has specified content.
        match_column_name denotes the name of column where search must be performed.
        match_content is argument of type 'str'. The first row which displays it as an argument
        of the kind denoted by match_column_name will be removed.
        For removing more rows, please use _remove_several_rows.
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
    def _remove_several_rows(
        match_column_name: Literal["feature_id", "id"],
        match_content: str,
        rows: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        """
        Removes more than one row from given rows (be it an inventory or a feature profile)
        which has specified content.
        match_column_name denotes the name of column where search must be performed.
        match_content is argument of type 'str'. All the rows which display it as an argument
        of the kind denoted by match_column_name will be removed.
        For removing exactly one row, please use _remove_one_row.
        """
        pass

    @staticmethod
    def _update_indices(
        match_column_name: Literal["feature_id", "id"],
        match_type: Literal["category", "feature"],
        match_content: str,
        rows: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        pass
