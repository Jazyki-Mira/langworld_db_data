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

    Feature index (not to confuse with feature ID) is the ordinal number of the feature within its category,
    the second component of value ID
    """
    return int(_split_value_id(value_id)[1])


def extract_feature_id(
    value_id: str,
) -> str:
    """
    Return feature ID as str

    Feature ID (not to confuse with feature index) consists of category ID and feature index
    """
    return ID_SEPARATOR.join(_split_value_id(value_id)[0:2])


def extract_value_index(
    value_id: str,
) -> int:
    """
    Return value index as int

    Value index is the ordinal number of the value within its feature, the third component of value ID
    """
    return int(_split_value_id(value_id)[2])


def extract_last_index(
    feature_or_value_id: int,
) -> int:
    """
    Return index that is last in the given ID. Works with both feature and value IDs
    """
    return int(_split_value_id(feature_or_value_id)[-1])
