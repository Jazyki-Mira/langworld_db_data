from typing import Literal

# I could read from CSV file to avoid data duplication, but then it would not work for
# type hinting
ValueType = Literal["listed", "custom", "not_stated", "explicit_gap", "not_applicable"]

AUX_ROW_MARKER = "_aux"

ID_SEPARATOR = "-"
"""Sign that separates category ID from feature ID from value ID."""
ATOMIC_VALUE_SEPARATOR = "&"
"""Sign that separates atomic values within a compound value."""

# For dicts
KEY_FOR_FEATURE_ID = "feature_id"
KEY_FOR_ID = "id"
KEY_FOR_ENGLISH = "en"  # applies to both features and values
KEY_FOR_RUSSIAN = "ru"  # applies to both features and values
KEY_FOR_MULTISELECT_OPTION = "is_multiselect"
KEY_FOR_VALUE_TYPE = "value_type"
KEY_FOR_RUSSIAN_OF_VALUE = "value_ru"
KEY_FOR_RUSSIAN_COMMENT = "comment_ru"
KEY_FOR_ENGLISH_COMMENT = "comment_en"
KEY_FOR_VALUE_ID = "value_id"
KEY_FOR_RUSSIAN_OF_FEATURE = "feature_name_ru"
KEY_FOR_FORMATTED_ENGLISH_DESCRIPTION = "description_formatted_en"
KEY_FOR_FORMATTED_RUSSIAN_DESCRIPTION = "description_formatted_ru"
KEY_FOR_RUSSIAN_NAME = "name_ru"
# add "*.csv"? And delimiter=","?
# take a closer look at cldf_dataset_writer, it may need some local constants
# delete encoding="utf-8"? Is sometimes used in value listers. Though I think in "files" its mention is logical gor there are many other encodings used there
