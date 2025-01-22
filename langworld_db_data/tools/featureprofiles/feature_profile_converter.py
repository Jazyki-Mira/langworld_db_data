from functools import partial
from pathlib import Path

from langworld_db_data.constants.literals import ATOMIC_VALUE_SEPARATOR
from langworld_db_data.constants.paths import CONFIG_DIR
from langworld_db_data.tools.featureprofiles.data_structures import (
    ValueForFeatureProfileDictionary,
)
from langworld_db_data.tools.featureprofiles.feature_profile_writer_from_dictionary import (  # noqa E501
    FeatureProfileWriterFromDictionary,
)
from langworld_db_data.tools.files.csv_xls import read_dicts_from_csv, read_dicts_from_xls
from langworld_db_data.tools.files.json_toml_yaml import read_json_toml_yaml


class FeatureProfileConverter:
    """Contains methods for converting Excel "questionnaire" file
    (which researchers produce) into feature profile in CSV and vice versa.

    The most notable differences between input Excel and output CSV:

    1. Excel questionnaire has two columns for value name
    (one for 'listed' and one for 'custom'), whereas a CSV file has only one.

    2. In multiselect features, Excel file has multiple lines
    for each elementary value (because of dropdown fields) while CSV file
    has one line with all elementary values joined together.
    """

    def csv_to_excel(self, path_to_input_csv: Path) -> Path:
        """Converts CSV feature profile into Excel "questionnaire" file
        that researchers feel comfortable working with.

        Return output path for convenience.
        """

        rows = read_dicts_from_csv(path_to_file=path_to_input_csv)
        rows_for_excel = []

        for row in rows:
            rows_for_excel += self._generate_excel_rows_from_one_csv_row(row)
        # FIXME add last row with editor's name

        # FIXME write to Excel
        output_path = path_to_input_csv.parent / f"{path_to_input_csv.stem}.xlsm"
        print(f"Saving converted CSV file as Excel file {output_path}")
        return output_path

    def excel_to_csv(self, path_to_input_excel: Path) -> Path:
        """Convert Excel "questionnaire" file (which researchers produce)
        into feature profile in CSV.

        Return output path for convenience.
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
            _get = partial(
                self._get_value_from_row, row_=row, name_for_id=sheet_or_column_name_for_id
            )

            feature_id = _get("feature_id")
            value_type = _get("value_type")
            value_id = _get("value_id")
            value_ru = (
                _get("listed_value_ru").removeprefix(f"{value_id}: ")
                if value_type == "listed"
                else _get("custom_value_ru")
            )

            # if this is a new feature ID, just write the value
            if feature_id not in processed_feature_ids:
                value_for_feature_id[feature_id] = ValueForFeatureProfileDictionary(
                    feature_name_ru=_get("feature_name_ru"),
                    value_type=value_type,
                    value_id=value_id,
                    value_ru=value_ru,
                    comment_ru=_get("comment_ru"),
                    comment_en=_get("comment_en"),
                    page_numbers=_get("page_numbers"),
                )
                processed_feature_ids.add(feature_id)
            else:
                # otherwise add the value to the existing dictionary entry
                value_for_feature_id[feature_id].value_id += f"&{value_id}"
                value_for_feature_id[feature_id].value_ru += f"&{value_ru}"

        output_path = path_to_input_excel.parent / f"{path_to_input_excel.stem}.csv"
        print(f"Saving converted Excel file as {output_path}")
        FeatureProfileWriterFromDictionary.write(
            feature_dict=value_for_feature_id, output_path=output_path
        )
        return output_path

    @staticmethod
    def _generate_excel_rows_from_one_csv_row(row: dict[str, str]) -> list[list[str]]:
        """Generate one or more rows for Excel from one CSV row.
        The amount of rows is equal to the amount of atomic values in CSV row.

        For uniformity, returns list of lists (rows) in all cases.
        """
        if ATOMIC_VALUE_SEPARATOR not in row["value_id"]:
            # simple case: CSV row yields one row in Excel
            return [
                [
                    row["feature_id"],
                    row["feature_name_ru"],
                    row["value_type"],
                    row["value_id"],
                    (
                        f'{row["value_id"]}: {row["value_ru"]}'
                        if row["value_type"] == "listed"
                        else ""
                    ),
                    row["value_ru"] if row["value_type"] == "custom" else "",
                    row["comment_ru"],
                    row["comment_en"],
                    row["page_numbers"],
                ]
            ]

        # complex case: CSV row must yield multiple rows in Excel
        value_ids = row["value_id"].split(ATOMIC_VALUE_SEPARATOR)
        value_names_en = row["value_en"].split(ATOMIC_VALUE_SEPARATOR)
        value_names_ru = row["value_ru"].split(ATOMIC_VALUE_SEPARATOR)

        rows_for_excel = []
        for value_id, value_name_en, value_name_ru in zip(
            value_ids, value_names_en, value_names_ru
        ):
            row_for_excel = [
                row["feature_id"],
                row["feature_name_ru"],
                row["value_type"],
                value_id,
                f"{value_id}: {value_name_ru}",  # no need to check for value type: it's "listed"
                "",  # value is not custom, so this will be empty
                row["comment_ru"],
                row["comment_en"],
                row["page_numbers"],
            ]
            rows_for_excel.append(row_for_excel)

        return rows_for_excel

    @staticmethod
    def _get_value_from_row(
        column_id: str, row_: dict[str, str], name_for_id: dict[str, str]
    ) -> str:
        """Returns value from column with relevant name.
        Name of column is looked up by `attr` in YAML file."""
        return row_[name_for_id[column_id]]


if __name__ == "__main__":
    for file in (Path(__file__).parent.resolve() / "input").glob("*.xlsm"):
        print(f"Converting {file.name}")
        FeatureProfileConverter().excel_to_csv(file)
