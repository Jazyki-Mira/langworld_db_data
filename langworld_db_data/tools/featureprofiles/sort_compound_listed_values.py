from pathlib import Path
from typing import Union

from langworld_db_data.constants.literals import ATOMIC_VALUE_SEPARATOR
from langworld_db_data.tools.featureprofiles.feature_profile_reader import FeatureProfileReader
from langworld_db_data.tools.featureprofiles.feature_profile_writer_from_dictionary import (
    FeatureProfileWriterFromDictionary,
)


def sort_compound_listed_values(
    path_to_input_feature_profile: Path, path_to_output_feature_profile: Union[Path, None] = None
) -> None:
    """
    Reads feature profile from CSV file, sorts atomic values within compound values
    by value ID, and writes the result
    (to a new CSV file if specified or updates the original file).

    Sorting elementary values provides a consistent order of values in feature profiles.
    """
    reader = FeatureProfileReader()
    feature_dict = reader.read_feature_profile_as_dict_from_file(
        file=path_to_input_feature_profile
    )
    sorted_feature_dict = feature_dict.copy()

    changes_made = False

    for feature_id, value in feature_dict.items():
        if ATOMIC_VALUE_SEPARATOR in value.value_id:
            # sort atomic values within compound value by value ID
            pairs = list(
                zip(
                    value.value_id.split(ATOMIC_VALUE_SEPARATOR),
                    value.value_ru.split(ATOMIC_VALUE_SEPARATOR),
                )
            )
            sorted_pairs = sorted(pairs, key=lambda x: x[0])
            value.value_id = ATOMIC_VALUE_SEPARATOR.join([pair[0] for pair in sorted_pairs])
            value.value_ru = ATOMIC_VALUE_SEPARATOR.join([pair[1] for pair in sorted_pairs])
            if sorted_pairs != pairs:
                print(
                    f"{path_to_input_feature_profile.name} Sorted compound value in {feature_id}"
                )
                changes_made = True

    if changes_made:
        print(
            f"Writing feature profile with sorted atomic values to "
            f"{path_to_output_feature_profile.name or path_to_input_feature_profile.name}"
        )
        writer = FeatureProfileWriterFromDictionary()
        writer.write(
            feature_dict=sorted_feature_dict,
            output_path=path_to_output_feature_profile or path_to_input_feature_profile,
        )

    return None
