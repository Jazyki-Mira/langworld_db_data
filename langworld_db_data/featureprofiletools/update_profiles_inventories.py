from pathlib import Path

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, INVENTORIES_DIR
from langworld_db_data.filetools.csv_xls import read_dicts_from_csv, write_csv


def rename_value_in_profiles_and_inventories(
    id_of_value_to_rename: str,
    new_value_name: str,
    output_feature_profiles_dir,
    output_inventories_dir,
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
            output_dir=output_feature_profiles_dir
        )

    if not output_inventories_dir.exists():
        output_inventories_dir.mkdir(parents=True, exist_ok=True)
    update_features_listed_values(
        id_of_value_to_rename=id_of_value_to_rename,
        new_value_name=new_value_name,
        input_filepath=input_inventories_dir / "features_listed_values.csv",
        output_filepath=output_inventories_dir / "features_listed_values.csv"
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
        if id_of_value_to_rename in line["value_id"]:
            line_to_write = line.copy()
            if line["value_id"] == id_of_value_to_rename:
                print(f"Found exact match in {input_filepath.name}")
                print("Changed " + line["value_ru"] + " to " + new_value_name)
                line_to_write["value_ru"] = new_value_name
                number_of_replacements += 1
            elif "&" in line["value_id"]:
                print("Found match in combined value in " + input_filepath.name)
                combined_value_ids = line["value_id"].split("&")
                combined_value_names = line["value_ru"].split("&")
                for i in range(len(combined_value_ids)):
                    if combined_value_ids[i] == id_of_value_to_rename:
                        combined_value_names[i] = new_value_name
                        number_of_replacements += 1
                line_to_write["value_ru"] = "&".join(combined_value_names)
                print("Changed " + line["value_ru"] + " to " + line_to_write["value_ru"])
            data_to_write.append(line_to_write)
        else:
            data_to_write.append(line)
    print("Replacements made in this file:" + str(number_of_replacements))
    output_file = output_dir / input_filepath.name
    write_csv(
        rows=data_to_write,
        path_to_file=output_file,
        overwrite=True,
        delimiter=","
              )
    print(f"Successfully written to {output_file}")


def update_features_listed_values(
    id_of_value_to_rename: str,
    new_value_name: str,
    input_filepath: Path,
    output_filepath: Path
) -> None:

    data_from_file = read_dicts_from_csv(input_filepath)
    data_to_write = []
    for line in data_from_file:
        if id_of_value_to_rename in line["id"]:
            line_to_write = line.copy()
            if line["id"] == id_of_value_to_rename:
                print("Found exact match in " + input_filepath.name)
                print("Changed " + line["ru"] + " to " + new_value_name)
                line_to_write["ru"] = new_value_name
            data_to_write.append(line_to_write)
        else:
            data_to_write.append(line)
    write_csv(
        rows=data_to_write,
        path_to_file=output_filepath,
        overwrite=True,
        delimiter=",",
    )
