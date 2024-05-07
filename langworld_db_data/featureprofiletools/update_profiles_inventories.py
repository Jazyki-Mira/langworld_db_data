from pathlib import Path

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, FILE_WITH_LISTED_VALUES

from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv


def rename_value(
    value_to_rename_id: str, new_value_name: str, feature_profiles_dir=FEATURE_PROFILES_DIR,
        file_with_listed_values=FILE_WITH_LISTED_VALUES
):
    """
    Replaces all the instances of a given value name in profiles and features_listed_values on a given value.
    Works with both singular and combined values.
    """
    number_of_replacements = 0
    replacement_made = False
    files_list = list(feature_profiles_dir.glob("*.csv"))
    for file in files_list:
        print("Opening " + file.name)
        data_from_file = []
        data_from_file = read_dicts_from_csv(file)
        for line in data_from_file:
            if value_to_rename_id in line["value_id"]:
                if line["value_id"] == value_to_rename_id:
                    print("Found exact match in " + file.name)
                    print("Changed " + line["value_ru"] + " to " + new_value_name)
                    line["value_ru"] = new_value_name
                    number_of_replacements += 1
                    replacement_made = True
                elif "&" in line["value_id"]:
                    print("Found match in combined value in " + file.name)
                    combined_value_ids = line["value_id"].split("&")
                    combined_value_names = line["value_ru"].split("&")
                    for i in range(len(combined_value_ids)):
                        if combined_value_ids[i] == value_to_rename_id:
                            combined_value_names[i] = new_value_name
                            number_of_replacements += 1
                            replacement_made = True
                    line["value_ru"] = "&".join(combined_value_names)
        print("Replacements made:" + str(number_of_replacements))
        if replacement_made:
            for line in data_from_file:
                print(line)
            replacement_made = False
        write_csv(data_from_file, file, overwrite=True, delimiter=",")
        print("Successfully written into csv-file")
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
