import logging
from copy import deepcopy
from typing import Literal

from langworld_db_data.constants.literals import ID_SEPARATOR
from langworld_db_data.tools.ids.extract import (
    extract_feature_index,
    extract_value_index,
)


def update_indices_after_given_line_number_if_necessary(
    lookup_column: Literal["feature_id", "id"],
    match_value: str,
    id_type_that_must_be_updated: Literal["feature", "value"],
    index_type_that_must_be_updated: Literal["feature", "value"],
    line_number_after_which_rows_must_be_updated: int,
    rows: list[dict[str, str]],
    rows_are_a_feature_profile: bool = False,
) -> list[dict[str, str]]:
    """
    Decrement indices of features or values. Return rows with updated indices or intact rows if update is not necessary.

    Search rows with matching content and decrement feature or value indices in the given column.
    lookup_column denotes the name of column where search must be performed.
    match_value is the sequence to search in the given column in the given rows.
    id_type_that_must_be_updated denotes what kind of ID must be decremented, feature ID or value ID.
    index_type_that_must_be_updated denotes what kind of index must be decremented, feature or value.
    This is needed to specify what kind of change must be done for value IDs
    (naturally, for feature IDs, only feature index can be updated).
    Update is only performed on rows whose line number is equal or greater than line_number_after_which_rows_must_be_updated.
    If rows_are_a_feature_profile is True, the method also scans value types and decrements feature indices in listed value IDs.
    """
    # So far it is only used to decrement indices, but it can be slightly rewritten to do either decrement or increment

    copied_rows = deepcopy(rows)

    changes_made = 0

    for row in copied_rows[line_number_after_which_rows_must_be_updated:]:

        if f"{match_value}{ID_SEPARATOR}" not in row[lookup_column]:
            continue

        current_feature_index = extract_feature_index(row[lookup_column])

        if id_type_that_must_be_updated == "value":
            if index_type_that_must_be_updated == "feature":
                current_value_index = extract_value_index(row["id"])
                row[lookup_column] = (
                    f"{match_value}{ID_SEPARATOR}{current_feature_index - 1}{ID_SEPARATOR}{current_value_index}"
                )

            elif index_type_that_must_be_updated == "value":
                row[lookup_column] = (
                    f"{match_value}{ID_SEPARATOR}{extract_value_index(row[lookup_column]) - 1}"
                )
        elif id_type_that_must_be_updated == "feature":
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
