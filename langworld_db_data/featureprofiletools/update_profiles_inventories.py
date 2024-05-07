from pathlib import Path

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, INVENTORIES_DIR
from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv


def rename_value(
    value_to_rename_id: str,
    new_value_name: str,
    input_feature_profiles_dir=FEATURE_PROFILES_DIR,
    output_feature_profiles_dir=FEATURE_PROFILES_DIR,
    input_inventories_dir=INVENTORIES_DIR,
    output_inventories_dir=INVENTORIES_DIR,
):
    """
    Replaces all the instances of a given value name in profiles and features_listed_values on a given value.
    Works with both singular and combined values.
    """
    files_list = list(input_feature_profiles_dir.glob("*.csv"))
    for file in files_list:
        number_of_replacements = 0
        print("Opening " + file.name)
        data_from_file = read_dicts_from_csv(file)
        data_to_write = []
        for line in data_from_file:
            if value_to_rename_id in line["value_id"]:
                line_to_write = line
                if line["value_id"] == value_to_rename_id:
                    print("Found exact match in " + file.name)
                    print("Changed " + line["value_ru"] + " to " + new_value_name)
                    line_to_write["value_ru"] = new_value_name
                    number_of_replacements += 1
                elif "&" in line["value_id"]:
                    print("Found match in combined value in " + file.name)
                    combined_value_ids = line["value_id"].split("&")
                    combined_value_names = line["value_ru"].split("&")
                    for i in range(len(combined_value_ids)):
                        if combined_value_ids[i] == value_to_rename_id:
                            combined_value_names[i] = new_value_name
                            number_of_replacements += 1
                    line_to_write["value_ru"] = "&".join(combined_value_names)
                    print("Changed " + line["value_ru"] + " to " + line_to_write["value_ru"])
                data_to_write.append(line_to_write)
            else:
                data_to_write.append(line)
        print("Replacements made:" + str(number_of_replacements))
        if number_of_replacements > 0:
            for line in data_to_write:
                print(line)
        write_csv(
            data_to_write, output_feature_profiles_dir / file.name, overwrite=True, delimiter=","
        )
        print("Successfully written into csv-file")
