import zipfile
from functools import partial
from pathlib import Path
from typing import Optional

from tinybear.csv_xls import read_dicts_from_xls
from tinybear.json_toml_yaml import read_json_toml_yaml

from langworld_db_data.constants.literals import (
    ATOMIC_VALUE_SEPARATOR,
    KEY_FOR_ENGLISH_COMMENT,
    KEY_FOR_FEATURE_ID,
    KEY_FOR_RUSSIAN_COMMENT,
    KEY_FOR_RUSSIAN_NAME_OF_FEATURE,
    KEY_FOR_VALUE_ID,
    KEY_FOR_VALUE_TYPE,
)
from langworld_db_data.constants.paths import CONFIG_DIR
from langworld_db_data.tools.featureprofiles import (
    ValueForFeatureProfileDictionary,
)
from langworld_db_data.tools.featureprofiles.feature_profile_writer_from_dictionary import (  # noqa E501
    FeatureProfileWriterFromDictionary,
)


def convert_from_excel(path_to_input_excel: Path) -> Path:
    """Converts Excel "questionnaire" file (which researchers produce)
    into feature profile in CSV. Returns output path for convenience.

    The most notable differences between input Excel and output CSV:

    1. Excel questionnaire has two columns for value name
    (one for 'listed' and one for 'custom'), whereas a CSV file has only one.

    2. In multiselect features, Excel file has multiple lines
    for each elementary value (because of dropdown fields) while CSV file
    has one line with all elementary values joined together.
    """

    # It is important to always use the current YAML file in conversion,
    # so I did not include path to it into parameters to allow overriding it in tests
    file_with_names = CONFIG_DIR / "excel_sheet_and_column_names.yaml"
    sheet_or_column_name_for_id = read_json_toml_yaml(file_with_names)
    # for mypy
    if not isinstance(sheet_or_column_name_for_id, dict):
        raise TypeError(
            f"File with names of Excel sheet and columns {file_with_names} was supposed"
            " to be read as a dictionary. Please check the file."
        )

    rows = read_dicts_from_xls(
        path_to_file=path_to_input_excel,
        sheet_name=sheet_or_column_name_for_id["sheet_name"],
    )

    # We could do without using custom class here, but it improves readability,
    # plus FeatureProfileWriterFromDictionary has a method for writing such dict to CSV.
    value_for_feature_id: dict[str, ValueForFeatureProfileDictionary] = {}

    processed_feature_ids: set[str] = set()
    """A set for keeping track of feature IDs already processed.
    Allows to add another value ID and value name if we encounter more than one row for a multiselect feature.
    """

    for row in rows:
        _get = partial(_get_value_from_row, row_=row, name_for_id=sheet_or_column_name_for_id)

        feature_id = _get(KEY_FOR_FEATURE_ID)
        value_type = _get(KEY_FOR_VALUE_TYPE)
        value_id = _get(KEY_FOR_VALUE_ID)
        value_ru = (
            _get("listed_value_ru").removeprefix(f"{value_id}: ")
            if value_type == "listed"
            else _get("custom_value_ru")
        )

        # if this is a new feature ID, just write the value
        if feature_id not in processed_feature_ids:
            value_for_feature_id[feature_id] = ValueForFeatureProfileDictionary(
                feature_name_ru=_get(KEY_FOR_RUSSIAN_NAME_OF_FEATURE),
                value_type=value_type,
                value_id=value_id,
                value_ru=value_ru,
                comment_ru=_get(KEY_FOR_RUSSIAN_COMMENT),
                comment_en=_get(KEY_FOR_ENGLISH_COMMENT),
                page_numbers=_get("page_numbers"),
            )
            processed_feature_ids.add(feature_id)
        else:
            # otherwise add the value to the existing dictionary entry
            value_for_feature_id[feature_id].value_id += f"{ATOMIC_VALUE_SEPARATOR}{value_id}"
            value_for_feature_id[feature_id].value_ru += f"{ATOMIC_VALUE_SEPARATOR}{value_ru}"

    output_dir = path_to_input_excel.parent.parent / "output_csv"
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    output_path = output_dir / f"{path_to_input_excel.stem}.csv"
    print(f"Saving converted Excel file as {output_path}")
    FeatureProfileWriterFromDictionary.write(
        feature_dict=value_for_feature_id, output_path=output_path
    )
    return output_path


def _get_value_from_row(column_id: str, row_: dict[str, str], name_for_id: dict[str, str]) -> str:
    """Returns value from column with relevant name.
    Name of column is looked up by `attr` in YAML file."""
    return row_[name_for_id[column_id]]


def _unzip_file(zip_path: Path, extract_to: Optional[Path] = None):
    zip_path = Path(zip_path)
    if extract_to is None:
        extract_to = zip_path.parent
    else:
        extract_to = Path(extract_to)
    if not zip_path.exists():
        raise FileNotFoundError(f"Error: {zip_path} does not exist.")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"Extracted '{zip_path}' to '{extract_to}'")


if __name__ == "__main__":
    input_dir = Path(__file__).parent.resolve() / "input_xlsm"  # pragma: no cover

    for file in input_dir.glob("*.zip"):  # pragma: no cover
        print(f"Extracting files from archive {file.name}")
        _unzip_file(file)

    for file in input_dir.glob("*.xlsm"):  # pragma: no cover
        print(f"Converting {file.name}")
        convert_from_excel(file)
