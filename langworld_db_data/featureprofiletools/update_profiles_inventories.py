from pathlib import Path

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, INVENTORIES_DIR
from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv


def rename_value_in_profiles_and_inventories(
    value_to_rename_id: str,
    new_value_name: str,
    input_feature_profiles_dir=FEATURE_PROFILES_DIR,
    output_feature_profiles_dir=FEATURE_PROFILES_DIR,
    input_inventories_dir=INVENTORIES_DIR,
    output_inventories_dir=INVENTORIES_DIR,
) -> None:
    """
    Renames value with given ID in all feature profiles and inventory of listed values.
    Also works with elementary values in multiselect features.
    """
    files = list(input_feature_profiles_dir.glob("*.csv"))
    for file in files_list:
        print(f"Processing {file.name}")
        data_to_write = process_one_feature_profile(
            value_to_rename_id,
            new_value_name,
            file,
        )
        write_csv(
            data_to_write, output_feature_profiles_dir / file.name, overwrite=True, delimiter=","
        )
        print("Successfully written into csv-file")
    data_to_write = process_and_save_features_listed_values(
        value_to_rename_id, new_value_name, input_inventories_dir / "features_listed_values.csv"
    )
    if not output_inventories_dir.exists():
        output_inventories_dir.mkdir(parents=True, exist_ok=True)
    write_csv(
        data_to_write,
        output_inventories_dir / "features_listed_values.csv",
        overwrite=True,
        delimiter=",",
    )


def process_one_feature_profile(
    id_of_value_to_rename: str,
    new_value_name: str,
    filepath: Path,
) -> list[dict[str, str]]:

    number_of_replacements = 0
    data_from_file = read_dicts_from_csv(filepath)
    data_to_write = []
    for line in data_from_file:
        if value_to_rename_id in line["value_id"]:
            line_to_write = line
            if line["value_id"] == value_to_rename_id:
                print(f"Found exact match in {filepath.name}")
                print("Changed " + line["value_ru"] + " to " + new_value_name)
                line_to_write["value_ru"] = new_value_name
                number_of_replacements += 1
            elif "&" in line["value_id"]:
                print("Found match in combined value in " + filepath.name)
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
    print("Replacements made in this file:" + str(number_of_replacements))
    return data_to_write


def process_and_save_features_listed_values(
    value_to_rename_id: str,
    new_value_name: str,
    filepath: Path,
):

    data_from_file = read_dicts_from_csv(filepath)
    data_to_write = []
    for line in data_from_file:
        if value_to_rename_id in line["id"]:
            line_to_write = line
            if line["id"] == value_to_rename_id:
                print("Found exact match in " + filepath.name)
                print("Changed " + line["ru"] + " to " + new_value_name)
                line_to_write["ru"] = new_value_name
            data_to_write.append(line_to_write)
        else:
            data_to_write.append(line)
    return data_to_write
