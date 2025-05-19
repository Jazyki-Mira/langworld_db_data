from pathlib import Path
from typing import Dict, Optional

from langworld_db_data.constants.paths import (
    FEATURE_PROFILES_DIR,
    FILE_WITH_LISTED_VALUES,
)
from langworld_db_data.tools.featureprofiles.feature_profile_reader import FeatureProfileReader
from langworld_db_data.tools.featureprofiles.feature_profile_writer_from_dictionary import (
    FeatureProfileWriterFromDictionary,
)

VALUE_ABSENCE_ID_MAP = {
    "A-6": {
        "absense_id_in_old_feature": "A-6-1",
        "new_feature_for_presence_marking": "A-5",
        "absense_id_in_new_feature": "A-5-2",
    },
    "A-8": {
        "absense_id_in_old_feature": "A-8-1",
        "new_feature_for_presence_marking": "A-7",
        "absense_id_in_new_feature": "A-7-2",
    },
    "A-10": {
        "absense_id_in_new_feature": "A-10-1",
        "new_feature_for_presence_marking": "A-9",
        "absense_id_in_old_feature": "A-9-2",
    },
}


def get_value_name_for_id(value_id: str) -> Optional[str]:
    """Get value name from features_listed_values.csv for a given value ID."""
    with open(FILE_WITH_LISTED_VALUES, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            id_, _, en_name, _, _, _ = line.strip().split(",")
            if id_ == value_id:
                return en_name
    return None


class AbsenceValueHandler:
    """A class to handle absence values in feature profiles.

    For each feature profile, this class will:
    1. Check for absence values in A-6, A-8, A-10
    2. If found, set corresponding presence feature to absence value
    3. Set the original feature to not_applicable
    """

    def __init__(self, dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR):
        self.feature_profiles = sorted(list(dir_with_feature_profiles.glob("*.csv")))
        self.reader = FeatureProfileReader()
        self.writer = FeatureProfileWriterFromDictionary

    def process_feature_profile(self, file: Path) -> bool:
        """Process a single feature profile file.

        Args:
            file: Path to the feature profile file

        Returns:
            bool: True if any changes were made, False otherwise
        """
        changes_made = False
        print(f"\nProcessing {file.name}")

        profile = self.reader.read_feature_profile_as_dict_from_file(file)
        amended_profile = profile.copy()

        for feature_id, mapping in VALUE_ABSENCE_ID_MAP.items():
            # Check if current feature has absence value
            if (
                profile[feature_id].value_type == "listed"
                and profile[feature_id].value_id == mapping["absence_id"]
            ):

                print(f"Found absence value in {feature_id}")
                changes_made = True

                # Set presence feature to absence value
                presence_feature = mapping["presence_feature"]
                presence_value_id = mapping["presence_id"]

                value_name = get_value_name_for_id(presence_value_id)
                if not value_name:
                    print(f"Warning: Could not find value name for ID {presence_value_id}")
                    continue

                print(f"Setting {presence_feature} to {presence_value_id} ({value_name})")
                amended_profile[presence_feature].value_type = "listed"
                amended_profile[presence_feature].value_id = presence_value_id
                amended_profile[presence_feature].value_name = value_name

                # Set current feature to not_applicable
                print(f"Setting {feature_id} to not_applicable")
                amended_profile[feature_id].value_type = "not_applicable"
                amended_profile[feature_id].value_id = ""
                amended_profile[feature_id].value_name = ""

        if changes_made:
            self.writer.write(feature_dict=amended_profile, output_path=file)
            print(f"Changes made in {file.name}")

        return changes_made

    def process_all_profiles(self) -> None:
        """Process all feature profiles in the directory."""
        for file in self.feature_profiles:
            self.process_feature_profile(file)


if __name__ == "__main__":
    handler = AbsenceValueHandler()
    handler.process_all_profiles()
