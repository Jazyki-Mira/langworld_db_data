from langworld_db_data.featureprofiletools.update_profiles_inventories import rename_value

from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES

from tests.test_helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard

DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES = (
    DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / "update_profiles_inventories"
)

DIR_WITH_INPUT_FILES = (
    DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "input"
)

DIR_WITH_OUTPUT_GOLD_STANDARD_FILES = (
    DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "output_gold_standard"
)


# Currently I am working with values only, but I put features_listed_values.csv in this folder where features.csv will
# be added later.


def test_rename_value():
    # First change files in tmp up to their default variants
    filepaths_list = DIR_WITH_INPUT_FILES.glob('*.csv')

    file_lines = []
    for filepath in filepaths_list:
        print("Opening " + filepath.name)
        with open(DIR_WITH_INPUT_FILES / filepath.name, "r", encoding="utf-8") as f:
            for line in f:
                file_lines.append(line)
        with open(DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / filepath.name, "w", encoding="utf-8") as f:
            for line in file_lines:
                f.write(line)
    print("Successfully put files into their default versions")
                
    rename_value(
        value_to_rename_id="A-9-2",
        new_value_name="Представлены исключительно дифтонги",
        feature_profiles_dir=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES,
        file_with_listed_values=DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / "features_listed_values.csv"
    )
    
    output_filenames_list = DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES.glob('*.csv')
    file_lines_in_result = []  # How the function changed files
    file_lines_reference = []  # How files should have been changed
    for filename in output_filenames_list:
        with open(DIR_WITH_TEST_UPDATE_PROFILES_INVENTORIES / filename, "r", encoding="utf-8"):
            for line in f:
                file_lines_in_result.append(line)
        with open(DIR_WITH_OUTPUT_GOLD_STANDARD_FILES / filename, "r", encoding="utf-8"):
            for line in f:
                file_lines_reference.append(line)
    assert file_lines_in_result == file_lines_reference
