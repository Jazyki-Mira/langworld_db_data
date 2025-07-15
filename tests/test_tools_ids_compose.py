from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.tools.common.ids.compose import (
    compose_feature_id,
    compose_value_id_based_on_feature_id,
    compose_value_id_from_scratch,
)


def test_compose_feature_id():

    assert (
        compose_feature_id(
            category_id="ABC",
            feature_index="794",
        )
        == f"ABC{ID_SEPARATOR}794"
    )


def test_compose_value_id_based_on_feature_id():

    assert (
        compose_value_id_based_on_feature_id(
            feature_id=f"Alligator{ID_SEPARATOR}5",
            value_index=88,
        )
        == f"Alligator{ID_SEPARATOR}5{ID_SEPARATOR}88"
    )


def test_compose_value_id_from_scratch():

    assert (
        compose_value_id_from_scratch(
            category_id="Alligator",
            feature_index=5,
            value_index=88,
        )
        == f"Alligator{ID_SEPARATOR}5{ID_SEPARATOR}88"
    )
