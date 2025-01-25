from abc import ABC, abstractmethod
from pathlib import Path

from langworld_db_data.constants.literals import (
    KEY_FOR_ID,
    KEY_FOR_RUSSIAN,
    KEY_FOR_RUSSIAN_NAME,
    KEY_FOR_VALUE_TYPE,
    ValueType,
)
from langworld_db_data.constants.paths import FILE_WITH_DOCULECTS, FILE_WITH_NAMES_OF_FEATURES
from langworld_db_data.tools.files.csv_xls import read_dict_from_2_csv_columns, read_dicts_from_csv


class AbstractValueLister(ABC):
    def __init__(
        self,
        value_type: ValueType,
        dir_with_feature_profiles: Path,
        file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
    ):
        self.value_type = value_type
        self.file_with_features = file_with_features

        self.doculect_ru_for_doculect_id = read_dict_from_2_csv_columns(
            FILE_WITH_DOCULECTS, KEY_FOR_ID, KEY_FOR_RUSSIAN_NAME
        )

        self.feature_ru_for_feature_id = read_dict_from_2_csv_columns(
            self.file_with_features, KEY_FOR_ID, KEY_FOR_RUSSIAN
        )

        self.encyclopedia_volume_for_doculect_id = read_dict_from_2_csv_columns(
            FILE_WITH_DOCULECTS, KEY_FOR_ID, "encyclopedia_volume_id"
        )

        # replace empty values with zeroes for sorting
        for key in self.encyclopedia_volume_for_doculect_id:
            if not self.encyclopedia_volume_for_doculect_id[key]:
                self.encyclopedia_volume_for_doculect_id[key] = "0"

        self.filtered_rows_for_volume_doculect_id = {}

        list_of_files = sorted(
            list(dir_with_feature_profiles.glob("*.csv")),
            key=lambda f: (
                int(self.encyclopedia_volume_for_doculect_id[f.stem]),
                f.stem,
            ),
        )

        for file in list_of_files:
            key = f"{self.encyclopedia_volume_for_doculect_id[file.stem]}:{file.stem}"
            rows = read_dicts_from_csv(file)
            self.filtered_rows_for_volume_doculect_id[key] = [
                row for row in rows if row[KEY_FOR_VALUE_TYPE] == self.value_type
            ]

    @abstractmethod
    def write_grouped_by_feature(self, output_file: Path) -> None:
        pass

    @abstractmethod
    def write_grouped_by_volume_and_doculect(self, output_file: Path) -> None:
        pass
