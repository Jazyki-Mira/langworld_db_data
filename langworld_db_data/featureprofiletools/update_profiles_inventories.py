from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, FILE_WITH_LISTED_VALUES


def rename_value(value_to_rename_id: str, new_value_name: str,
                 feature_profiles_dir, file_with_listed_values: str):
    """
    Replaces all the instances of a given value name in profiles and features_listed_values on a given value.
    Works with both singular and combined values.
    Argument feature_profiles_dir is transmitted temporarily, for convenience of tests. It will later be replaced with
    FEATURE_PROFILES_DIR. The same goes for file_with_listed_values.
    """
    number_of_replacements = 0
    files_list = list(feature_profiles_dir.iterdir())
    files_list.append(file_with_listed_values)
    for file in files_list:
        with open(file, "r") as f:
            data_from_file = []
            for line in f:
                data_from_file.append(line)
        with open(file, "w") as f:
            for line in data_from_file:
                line = line.split()
                if value_to_rename_id in line[4]:
                    if line[4] == value_to_rename_id:
                        line[4] = new_value_name
                        number_of_replacements += 1
                    elif "&" in line[4]:
                        combined_value_ids = line[3].split("&")
                        combined_value_name = line[4].split("&")
                        for i in range(len(combined_value_ids)):
                            if combined_value_ids[i] == value_to_rename_id:
                                combined_value_name[i] = new_value_name
                                number_of_replacements += 1
                f.write(",".join(line))
    if number_of_replacements == 0:
        print("Nothing has been replaced. Maybe you entered a wrong value_to_rename_id.")
