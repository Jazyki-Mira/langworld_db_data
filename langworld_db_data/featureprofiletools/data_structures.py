from typing import NamedTuple


class ValueForFeatureProfileDictionary(NamedTuple):
    """Class for a data structure that represents a value
    in a dictionary for reading/writing feature profiles.
    """

    feature_name_ru: str
    value_type: str
    value_id: str
    value_ru: str
    comment_ru: str
    comment_en: str
    page_numbers: str
