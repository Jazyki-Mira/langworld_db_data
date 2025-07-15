from typing import Literal

from langworld_db_data import ObjectWithPaths


class Adder(ObjectWithPaths):

    def _validate_arguments() -> bool:
        pass

    def _check_if_index_to_assign_is_in_list_of_applicable_indices(
        self,
        index_to_validate: int,
        category_or_feature: Literal["category", "feature"],
        category_or_feature_id: str,
    ) -> bool:
        pass

    def _get_range_of_currently_existing_indices(
        self,
        category_or_feature: Literal["category", "feature"],
        category_or_feature_id: str,
    ) -> tuple[int]:
        pass

    def _make_id_for_new_feature_or_value(
        self,
        feature_or_value: Literal["feature", "value"],
        new_feature_or_value_id: str,
        index_to_assign: int,
    ) -> str:
        pass

    def _compose_new_row(
        self,
        feature_or_value: Literal["feature", "value"],
        args_of_new_feature_or_value: tuple[str],
    ) -> dict[str, str]:
        pass

    def _get_line_number_where_to_insert(
        self,
        feature_or_value: Literal["feature", "value"],
        new_feature_or_value_id: str,
        category_or_feature: Literal["category", "feature"],
        category_or_feature_id: str,
    ) -> int:
        pass
