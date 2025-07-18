from typing import Literal, Union

from langworld_db_data import ObjectWithPaths
from langworld_db_data.tools.common.ids.compose import (
    compose_feature_id,
    compose_value_id_from_scratch,
)

FeatureOrValue = Literal["feature", "value"]
CategoryOrFeature = Literal["category", "feature"]


class AdderError(Exception):
    pass


class Adder(ObjectWithPaths):

    def _validate_arguments(
        self,
        feature_or_value: FeatureOrValue,
        args_of_new_feature_or_value: dict[str, Union[str, int, None]],
    ) -> bool:
        pass

    def _check_if_index_to_assign_is_in_list_of_applicable_indices(
        self,
        index_to_validate: int,
        category_or_feature: CategoryOrFeature,
        category_or_feature_id: str,
    ) -> bool:
        pass

    def _get_range_of_currently_existing_indices(
        self,
        category_or_feature: CategoryOrFeature,
        category_or_feature_id: str,
    ) -> tuple[int]:
        pass

    def _make_id_for_new_feature_or_value(
        self,
        category_or_feature: CategoryOrFeature,
        category_or_feature_id: str,
        index_to_assign: int,
    ) -> str:
        pass

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
