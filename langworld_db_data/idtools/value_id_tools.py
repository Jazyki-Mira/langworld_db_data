from langworld_db_data.constants.literals import ID_SEPARATOR


def _split_value_id(
    value_id: str,
) -> list[str]:
    return value_id.split(ID_SEPARATOR)


def extract_category_id(
    value_id: str,
) -> str:
    return _split_value_id(value_id)[0]


def extract_feature_index(
    value_id: str,
) -> int:
    """
    Return feature index as int

    Feature index is the ordinal number of the feature within its category
    """
    return int(_split_value_id(value_id)[1])


def extract_feature_id(
    value_id: str,
) -> str:
    return ID_SEPARATOR.join(_split_value_id(value_id)[0:2])


def extract_value_index(
    value_id: str,
) -> int:
    """
    Return value index as int

    Value index is the ordinal number of the value within its feature
    """
    return int(_split_value_id(value_id)[2])
