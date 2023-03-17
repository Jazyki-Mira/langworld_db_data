from pathlib import Path

from langworld_db_data.constants.paths import (
    FEATURE_PROFILES_DIR,
    FILE_WITH_LISTED_VALUES,
)


class AdderError(Exception):
    pass


class Adder:
    def __init__(
        self,
        *,
        input_file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
        input_dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
        # This is mainly for testing: there should be an option to give different paths.
        # In a default scenario, these paths will be the same, meaning the file will be updated in place.
        output_file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
        output_dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
    ):
        self.input_file_with_listed_values = input_file_with_listed_values
        self.input_feature_profiles = sorted(
            list(input_dir_with_feature_profiles.glob("*.csv"))
        )

        self.output_file_with_listed_values = output_file_with_listed_values
        self.output_dir_with_feature_profiles = output_dir_with_feature_profiles
