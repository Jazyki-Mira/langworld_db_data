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
KEY_FOR_VALUE_ID = "id"
