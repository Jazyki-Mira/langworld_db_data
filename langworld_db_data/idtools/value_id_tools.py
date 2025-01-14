"""
tools for ID should be able to do:
- feature ID extraction
- value index extraction
These also might be useful:
- value ID composition from feature ID and value index
- ID decomposition into the three components -- category ID, feature index and
value index
All these are frequently used in methods for adding/removing/moving values.
- value ID incrementation
- value ID decrementation
These are used only in adding and removing values once each, but perhaps
writing corresponding methods may improve the readability of the methods

Perhaps these methods might yield a new class later
"""


def extract_feature_id(
    value_id: str,
) -> str:
    pass

def extract_value_index_as_str(
    value_id: str,
) -> str:
    pass

def extract_value_index_as_int(
    value_id: str,
) -> int:
    pass
