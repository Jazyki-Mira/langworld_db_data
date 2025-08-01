from pathlib import Path

from pycldf import StructureDataset
from tinybear.csv_xls import (
    read_dict_from_2_csv_columns,
    read_dicts_from_csv,
)

from langworld_db_data.constants.literals import (
    ATOMIC_VALUE_SEPARATOR,
    KEY_FOR_ENGLISH,
    KEY_FOR_ENGLISH_COMMENT,
    KEY_FOR_FEATURE_ID,
    KEY_FOR_ID,
    KEY_FOR_MULTISELECT_OPTION,
    KEY_FOR_RUSSIAN,
    KEY_FOR_RUSSIAN_COMMENT,
    KEY_FOR_RUSSIAN_NAME,
    KEY_FOR_RUSSIAN_NAME_OF_VALUE,
    KEY_FOR_VALUE_ID,
    KEY_FOR_VALUE_TYPE,
)
from langworld_db_data.constants.paths import (
    CLDF_DIR,
    FEATURE_PROFILES_DIR,
    FILE_WITH_DOCULECTS,
    FILE_WITH_LISTED_VALUES,
    FILE_WITH_NAMES_OF_FEATURES,
)

KEY_FOR_ID_IN_CLDF = "ID"
KEY_FOR_RUSSIAN_NAME_IN_CLDF = "Name_RU"


class CLDFDatasetWriter:
    def __init__(
        self,
        dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
        file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
        file_with_doculects: Path = FILE_WITH_DOCULECTS,
        file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
    ):
        self.listed_values = read_dicts_from_csv(file_with_listed_values)
        self.value_en_for_value_id = read_dict_from_2_csv_columns(
            file_with_listed_values, key_col=KEY_FOR_ID, val_col=KEY_FOR_ENGLISH
        )

        self.doculects = read_dicts_from_csv(file_with_doculects)
        self.features = read_dicts_from_csv(file_with_features)
        self.is_multiselect_for_feature_id = read_dict_from_2_csv_columns(
            file_with_features, key_col=KEY_FOR_ID, val_col=KEY_FOR_MULTISELECT_OPTION
        )
        self.feature_profiles = sorted(list(dir_with_feature_profiles.glob("*.csv")))

    def write(self) -> None:
        dataset = StructureDataset.in_dir(CLDF_DIR)

        for component_name in ("CodeTable", "LanguageTable", "ParameterTable"):
            dataset.add_component(component_name)
            dataset.add_columns(component_name, KEY_FOR_RUSSIAN_NAME_IN_CLDF)

        for column_name in ("Value_RU", "Comment_RU"):
            dataset.add_columns("ValueTable", column_name)

        for column_name in ("ISO639P3code", "Glottocode"):
            dataset["LanguageTable", column_name].separator = "; "

        # CodeTable
        listed_values = [
            {
                KEY_FOR_ID_IN_CLDF: row[KEY_FOR_ID],
                "Parameter_ID": row[KEY_FOR_FEATURE_ID],
                "Name": row[KEY_FOR_ENGLISH],
                "Description": "",
                # custom columns:
                KEY_FOR_RUSSIAN_NAME_IN_CLDF: row[KEY_FOR_RUSSIAN],
            }
            for row in self.listed_values
        ]

        # ParameterTable
        features = [
            {
                KEY_FOR_ID_IN_CLDF: row[KEY_FOR_ID],
                "Name": row[KEY_FOR_ENGLISH],
                "Description": "",
                # custom columns:
                KEY_FOR_RUSSIAN_NAME_IN_CLDF: row[KEY_FOR_RUSSIAN],
            }
            for row in self.features
        ]

        languages = [
            {
                KEY_FOR_ID_IN_CLDF: row[KEY_FOR_ID],
                "Name": row["name_en"],
                "Macroarea": "",
                "Latitude": row["latitude"],
                "Longitude": row["longitude"],
                "Glottocode": row["glottocode"].split(", "),
                "ISO639P3code": row["iso_639_3"].split(", "),
                # custom columns:
                KEY_FOR_RUSSIAN_NAME_IN_CLDF: row[KEY_FOR_RUSSIAN_NAME],
            }
            for row in self.doculects
        ]

        value_table_rows = []
        value_table_row_id = 1

        for file in self.feature_profiles:
            language_id = file.stem
            # not sure how best to handle explicit_gap yet.
            relevant_rows = [
                row
                for row in read_dicts_from_csv(file)
                if row[KEY_FOR_VALUE_TYPE] in ("listed", "custom")
            ]

            for relevant_row in relevant_rows:
                # handling multiselect listed values
                if (
                    relevant_row[KEY_FOR_VALUE_TYPE] == "listed"
                    and self.is_multiselect_for_feature_id[relevant_row[KEY_FOR_FEATURE_ID]] == "1"
                ):
                    for value_id, value_ru in zip(
                        relevant_row[KEY_FOR_VALUE_ID].split(ATOMIC_VALUE_SEPARATOR),
                        relevant_row[KEY_FOR_RUSSIAN_NAME_OF_VALUE].split(ATOMIC_VALUE_SEPARATOR),
                    ):
                        value_table_rows.append(
                            {
                                KEY_FOR_ID_IN_CLDF: value_table_row_id,
                                "Language_ID": language_id,
                                "Parameter_ID": relevant_row[KEY_FOR_FEATURE_ID],
                                "Value": self.value_en_for_value_id[value_id],
                                "Value_RU": value_ru,
                                "Code_ID": value_id,
                                "Comment": relevant_row[KEY_FOR_ENGLISH_COMMENT],
                                "Comment_RU": relevant_row[KEY_FOR_RUSSIAN_COMMENT],
                                "Source": "",
                            }
                        )
                        value_table_row_id += 1
                # handling other values
                else:
                    value_table_rows.append(
                        {
                            KEY_FOR_ID_IN_CLDF: value_table_row_id,
                            "Language_ID": language_id,
                            "Parameter_ID": relevant_row[KEY_FOR_FEATURE_ID],
                            # English value will be empty for values that are not yet
                            # in the inventory
                            "Value": self.value_en_for_value_id.get(
                                relevant_row[KEY_FOR_VALUE_ID], ""
                            ),
                            "Value_RU": relevant_row[KEY_FOR_RUSSIAN_NAME_OF_VALUE],
                            "Code_ID": relevant_row[KEY_FOR_VALUE_ID],
                            "Comment": relevant_row[KEY_FOR_ENGLISH_COMMENT],
                            "Comment_RU": relevant_row[KEY_FOR_RUSSIAN_COMMENT],
                            "Source": "",
                        }
                    )
                    value_table_row_id += 1

        dataset.write(
            ValueTable=value_table_rows,
            LanguageTable=languages,
            CodeTable=listed_values,
            ParameterTable=features,
        )


if __name__ == "__main__":
    CLDFDatasetWriter().write()
