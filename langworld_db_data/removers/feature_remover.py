from pathlib import Path
from typing import Literal, Union

from langworld_db_data import ObjectWithPaths
from langworld_db_data.constants.paths import FILE_WITH_CATEGORIES, FILE_WITH_NAMES_OF_FEATURES


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

    def remove_feature():
        """
        Consists of removing from features inventory, from listed values inventory
        and from feature profiles (same as in FeatureAdder).
        """
        pass

    def _remove_from_inventory_of_features():
        """
        Two sub-tasks: remove line with target feature and update feature indices that follow it
        """
        pass

    def _remove_from_inventory_of_listed_values():
        """
        Two sub-tasks: remove lines with target feature values and update feature indices
        of values that follow it
        """
        pass

    def _remove_from_feature_profiles_and_update_ids_whose_indices_are_greater_than_one_of_removed_value():
        """
        Two sub-tasks: remove lines with target feature values and update feature indices
        of features and their values that follow it
        """
        pass

    @staticmethod
    def _remove_one_line(
        flag_type: Literal["feature_id", "feature_index", "value_id", "value_index"],
        flag_content: str,
        rows: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        pass
