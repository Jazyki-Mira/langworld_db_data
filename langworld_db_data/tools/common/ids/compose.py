from langworld_db_data.constants.literals import ID_SEPARATOR


def compose_feature_id(
    category_id: str,
    feature_index: int,
) -> str:
    
    return f"{category_id}{ID_SEPARATOR}{feature_index}"


def compose_value_id_from_scratch(
    category_id: str,
    feature_index: int,
    value_index: int,
) -> str:
    
    return f"{category_id}{ID_SEPARATOR}{feature_index}{ID_SEPARATOR}{value_index}"


def compose_value_id_based_on_feature_id(
    feature_id: str,
    value_index: int,
) -> str:
    
    return f"{feature_id}{ID_SEPARATOR}{value_index}"
