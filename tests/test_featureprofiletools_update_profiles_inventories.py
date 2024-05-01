import pytest

from langworld_db_data.featureprofiletools.update_profiles_inventories import rename_value
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES

DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES = (
    DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / "update_profiles_inventories"
)

DIR_WITH_DEFAULT_FILES = DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "default"

DIR_WITH_FILES_CHANGED = DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "changed"

DIR_WITH_TEMPORARY_FILES = DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "tmp"

DIR_WITH_DEFAULT_FEATURE_PROFILES = DIR_WITH_DEFAULT_FILES / "feature_profiles"

DIR_WITH_DEFAULT_INVENTORIES = DIR_WITH_DEFAULT_FILES / "inventories"

PATH_TO_FILE_WITH_DEFAULT_FEATURES_LISTED_VALUES = (
    DIR_WITH_DEFAULT_INVENTORIES / "features_listed_values.csv"
)

# Currently I am working with values only, but I put features_listed_values.csv in this folder where features.csv will
# be added later.


def test_rename_value():
    # First change files in tmp up to their default variants
    filenames_list = DIR_WITH_DEFAULT_FEATURE_PROFILES.glob("*.csv")
    file_lines = []
    for filename in filenames_list:
        print(filename)
        with open(DIR_WITH_DEFAULT_FEATURE_PROFILES / filename, "r", encoding="utf-8") as f:
            for line in f:
                file_lines.append(line)
        with open(DIR_WITH_TEMPORARY_FILES / filename, "w", encoding="utf-8") as f:
            for line in file_lines:
                f.write(line)
    with open(PATH_TO_FILE_WITH_DEFAULT_FEATURES_LISTED_VALUES, "r", encoding="utf-8") as f:
        for line in f:
            file_lines.append(line)
    with open(DIR_WITH_TEMPORARY_FILES / "features_listed_values.csv", "w", encoding="utf-8") as f:
        for line in file_lines:
            f.write(line)

    rename_value(
        value_to_rename_id="A-9-2",
        new_value_name="Представлены исключительно дифтонги",
        feature_profiles_dir=DIR_WITH_TEMPORARY_FILES,
        file_with_listed_values=DIR_WITH_TEMPORARY_FILES / "features_listed_values.csv",
    )

    temporary_filenames_list = DIR_WITH_TEMPORARY_FILES.glob("*.csv")
    file_lines_in_result = []  # How the function changed files
    file_lines_reference = []  # How files should have been changed
    for filename in temporary_filenames_list:
        with open(DIR_WITH_TEMPORARY_FILES / filename, "r", encoding="utf-8"):
            for line in f:
                file_lines_in_result.append(line)
        with open(DIR_WITH_FILES_CHANGED / filename, "r", encoding="utf-8"):
            for line in f:
                file_lines_reference.append(line)
    assert file_lines_in_result == file_lines_reference
