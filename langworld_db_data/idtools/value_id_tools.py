from langworld_db_data.constants.literals import ID_SEPARATOR

"""
tools for ID should be able to do:
- feature ID extraction
- value index extraction
- category ID extraction
- feature index extraction (as int)
These also might be useful:
- value ID composition from feature ID and value index
All these are frequently used in methods for adding/removing/moving values.
- value ID incrementation
- value ID decrementation
These are used only in adding and removing values once each, but perhaps
writing corresponding functions may improve the readability of the methods

Perhaps these functions might yield a new class later
"""


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
    feature_id = ID_SEPARATOR.join(_split_value_id(value_id)[0:2])
    return feature_id


def extract_value_index(
    value_id: str,
) -> int:
    """
    Return value index as int

    Value index is the ordinal number of the value within its feature
    """
    return int(_split_value_id(value_id)[2])
