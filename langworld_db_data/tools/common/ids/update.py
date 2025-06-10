import logging
from copy import deepcopy
from typing import Literal

from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.tools.common.ids.extract import (
    extract_feature_index,
    extract_value_index,
)

FeatureOrValue = Literal["feature", "value"]


def decrement_indices_after_deletion(
    rows: list[dict[str, str]],
    line_number_after_which_rows_must_be_updated: int,
    lookup_column: Literal["feature_id", "id"],
    match_value: str,
    type_of_id: FeatureOrValue,
    type_of_index: FeatureOrValue,
    rows_are_a_feature_profile: bool = False,
) -> list[dict[str, str]]:
    """
    Decrements feature or value indices in IDs after a deletion operation.

    Args:
        rows: Input rows
        lookup_column: Column name to search for matching rows
        match_value: Value to match in the lookup_column
        type_of_id: Type of ID to update ('feature' or 'value')
        type_of_index: Type of index to decrement ('feature' or 'value')
        line_number_after_which_rows_must_be_updated: Only update rows at or after this line number
        rows_are_a_feature_profile: If True, also updates feature indices in listed value IDs

    Returns:
        List of rows with updated indices. Rows not requiring updates remain unchanged.

    Notes:
        - For value IDs, both feature and value indices can be updated
        - For feature IDs, only feature indices can be updated
        - The function preserves rows that don't require index updates
    """

    copied_rows = deepcopy(rows)

    changes_made = 0

    for row in copied_rows[line_number_after_which_rows_must_be_updated:]:

        if f"{match_value}{ID_SEPARATOR}" not in row[lookup_column]:
            continue

        current_feature_index = extract_feature_index(row[lookup_column])

        if type_of_id == "value":
            if type_of_index == "feature":
                current_value_index = extract_value_index(row["id"])
                row[lookup_column] = (
                    f"{match_value}{ID_SEPARATOR}{current_feature_index - 1}{ID_SEPARATOR}{current_value_index}"
                )

            elif type_of_index == "value":
                row[lookup_column] = (
                    f"{match_value}{ID_SEPARATOR}{extract_value_index(row[lookup_column]) - 1}"
                )
        elif type_of_id == "feature":
            row[lookup_column] = f"{match_value}{ID_SEPARATOR}{current_feature_index - 1}"

        if rows_are_a_feature_profile:
            if row["value_type"] == "listed":

                current_value_index = extract_value_index(row["value_id"])
                row["value_id"] = (
                    f"{match_value}{ID_SEPARATOR}{current_feature_index - 1}{ID_SEPARATOR}{current_value_index}"
                )

        changes_made += 1

    if not changes_made:
        logging.warning("No rows have been changed.")
    else:
        logging.info(f"Successfully updated IDs: {changes_made} changes were made.")

    return copied_rows
