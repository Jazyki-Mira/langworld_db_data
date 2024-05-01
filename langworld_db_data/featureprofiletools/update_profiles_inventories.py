from pathlib import Path

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, FILE_WITH_LISTED_VALUES

from langworld_db_data.filetools.csv_xls import read_dicts_from_csv


def rename_value(value_to_rename_id: str, new_value_name: str,
                 feature_profiles_dir: Path, file_with_listed_values: Path):
    """
    Replaces all the instances of a given value name in profiles and features_listed_values on a given value.
    Works with both singular and combined values.
    Argument feature_profiles_dir is transmitted temporarily, for convenience of tests. It will later be replaced with
    FEATURE_PROFILES_DIR. The same goes for file_with_listed_values.
    """
    number_of_replacements = 0
    files_list = list(feature_profiles_dir.iterdir())
    for file in files_list:
        print("Replacements made:" + str(number_of_replacements))
        data_from_file = read_dicts_from_csv(file)
        for line in data_from_file:
            if value_to_rename_id in line["value_id"]:
                print("Found in " + str(file))
                print(line)
                if line["value_id"] == value_to_rename_id:
                    line["value_ru"] = new_value_name
                    number_of_replacements += 1
                elif "&" in line["value_id"]:
                    combined_value_ids = line["value_id"].split("&")
                    combined_value_names = line["value_ru"].split("&")
                    for i in range(len(combined_value_ids)):
                        if combined_value_ids[i] == value_to_rename_id:
                            combined_value_names[i] = new_value_name
                            number_of_replacements += 1
                    line["value_ru"] = "&".join(combined_value_names)
        with open(file, "w", encoding="utf-8") as f:
            for line in data_from_file:
                try:
                    f.write(",".join(str(item) for item in line.items()))
                except TypeError:
                    print("Unable to write line: " + ",".join(str(item) for item in line.items()))
    data_from_file = read_dicts_from_csv(file_with_listed_values)
    for line in data_from_file:
        if line["id"] == value_to_rename_id:
            line["ru"] = new_value_name
            number_of_replacements += 1
    with open(file_with_listed_values, "w", encoding="utf-8") as f:
        for line in data_from_file:
            f.write(",".join([line["id"], line["feature_id"],
                              line["en"], line["ru"]]))
    print("Replacements made:" + str(number_of_replacements))
    if number_of_replacements == 0:
        print("Nothing has been replaced. Maybe you entered a wrong value_to_rename_id.")
