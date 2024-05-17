from pathlib import Path

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, INVENTORIES_DIR
from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv


def rename_value_in_profiles_and_inventories(
    id_of_value_to_rename: str,
    new_value_name: str,
    output_feature_profiles_dir=FEATURE_PROFILES_DIR,
    output_inventories_dir=INVENTORIES_DIR,
    input_feature_profiles_dir=FEATURE_PROFILES_DIR,
    input_inventories_dir=INVENTORIES_DIR,
) -> None:
    """
    Renames value with given ID in all feature profiles and inventory of listed values.
    Also works with elementary values in multiselect features.
    """
    files = list(input_feature_profiles_dir.glob("*.csv"))
    for file in files:
        print(f"Processing {file.name}")
        update_one_feature_profile(
            id_of_value_to_rename=id_of_value_to_rename,
            new_value_name=new_value_name,
            input_filepath=file,
            output_dir=output_feature_profiles_dir,
        )

    if not output_inventories_dir.exists():
        output_inventories_dir.mkdir(parents=True, exist_ok=True)
    update_features_listed_values(
        id_of_value_to_rename=id_of_value_to_rename,
        new_value_name=new_value_name,
        input_filepath=input_inventories_dir / "features_listed_values.csv",
        output_filepath=output_inventories_dir / "features_listed_values.csv",
    )


def update_one_feature_profile(
    id_of_value_to_rename: str,
    new_value_name: str,
    input_filepath: Path,
    output_dir: Path,
) -> None:

    number_of_replacements = 0
    data_from_file = read_dicts_from_csv(input_filepath)
    data_to_write = []
    for line in data_from_file:
        if id_of_value_to_rename not in line["value_id"]:
            data_to_write.append(line)
            continue
        line_to_write = line.copy()
        # After this clause, only lines with the target value are considered (they may contain other values too)
        if "&" in line["value_id"]:
            print("Found match in combined value in " + input_filepath.name)
            combined_value_ids = line["value_id"].split("&")
            target_value_index = combined_value_ids.index(id_of_value_to_rename)
            combined_value_names = line["value_ru"].split("&")
            combined_value_names.pop(target_value_index)
            combined_value_names.insert(target_value_index, new_value_name)
            line_to_write["value_ru"] = "&".join(combined_value_names)
            data_to_write.append(line_to_write)
            print("Changed " + line["value_ru"] + " to " + line_to_write["value_ru"])
            continue
        # After this clause, only those lines are considered which contain the target value only
        print(f"Found exact match in {input_filepath.name}")
        line_to_write["value_ru"] = new_value_name
        number_of_replacements += 1
        data_to_write.append(line_to_write)
        print("Changed " + line["value_ru"] + " to " + new_value_name)
    print("Replacements made in this file:" + str(number_of_replacements))
    output_file = output_dir / input_filepath.name
    write_csv(rows=data_to_write,
              path_to_file=output_file,
              overwrite=True,
              delimiter=","
              )
    print(f"Successfully written to {output_file}")


def update_features_listed_values(
    id_of_value_to_rename: str, new_value_name: str, input_filepath: Path, output_filepath: Path
) -> None:

    data_from_file = read_dicts_from_csv(input_filepath)
    data_to_write = []
    for line in data_from_file:
        if id_of_value_to_rename not in line["id"]:
            data_to_write.append(line)
            continue
        line_to_write = line.copy()
        print("Found exact match in " + input_filepath.name)
        print("Changed " + line["ru"] + " to " + new_value_name)
        line_to_write["ru"] = new_value_name
        data_to_write.append(line_to_write)
    write_csv(
        rows=data_to_write,
        path_to_file=output_filepath,
        overwrite=True,
        delimiter=",",
    )
