from typing import Literal

# I could read from CSV file to avoid data duplication, but then it would not work for type hinting
ValueType = Literal["listed", "custom", "not_stated", "explicit_gap", "not_applicable"]

AUX_ROW_MARKER = "_aux"
SEPARATOR = "-"
