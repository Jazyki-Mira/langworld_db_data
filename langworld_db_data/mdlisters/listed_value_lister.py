from pathlib import Path

from tinybear.csv_xls import (
    read_column_from_csv,
    read_dict_from_2_csv_columns,
    read_dicts_from_csv,
)

from langworld_db_data.constants.literals import (
    ATOMIC_VALUE_SEPARATOR,
    KEY_FOR_FEATURE_ID,
    KEY_FOR_ID,
    KEY_FOR_MULTISELECT_OPTION,
    KEY_FOR_RUSSIAN,
    KEY_FOR_VALUE_ID,
)
from langworld_db_data.constants.paths import (
    DISCUSSION_FILE_WITH_LISTED_VALUES,
    FEATURE_PROFILES_DIR,
    FILE_WITH_LISTED_VALUES,
    FILE_WITH_NAMES_OF_FEATURES,
)
from langworld_db_data.mdlisters.abstract_value_lister import AbstractValueLister


class ListedValueLister(AbstractValueLister):
    def __init__(
        self,
        dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
        file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
        file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
    ):
        super().__init__(
            value_type="listed",
            dir_with_feature_profiles=dir_with_feature_profiles,
            file_with_features=file_with_features,
        )
        self.file_with_listed_values = file_with_listed_values

    def write_grouped_by_feature(
        self, output_file: Path = DISCUSSION_FILE_WITH_LISTED_VALUES
    ) -> None:
        feature_ids = read_column_from_csv(
            path_to_file=self.file_with_features, column_name=KEY_FOR_ID
        )

        feature_to_value_to_doculects: dict[str, dict[str, list[str]]] = {
            feature_id: {
                row[KEY_FOR_ID]: []
                for row in read_dicts_from_csv(self.file_with_listed_values)
                if row[KEY_FOR_FEATURE_ID] == feature_id
            }
            for feature_id in feature_ids
        }

        feature_is_multiselect_for_feature_id = read_dict_from_2_csv_columns(
            self.file_with_features,
            key_col=KEY_FOR_ID,
            val_col=KEY_FOR_MULTISELECT_OPTION,
        )

        for volume_and_doculect_id in self.filtered_rows_for_volume_doculect_id:
            for row in self.filtered_rows_for_volume_doculect_id[volume_and_doculect_id]:
                if feature_is_multiselect_for_feature_id[row[KEY_FOR_FEATURE_ID]] == "1":
                    for value_id in row[KEY_FOR_VALUE_ID].split(ATOMIC_VALUE_SEPARATOR):
                        feature_to_value_to_doculects[row[KEY_FOR_FEATURE_ID]][value_id].append(
                            volume_and_doculect_id
                        )
                else:
                    feature_to_value_to_doculects[row[KEY_FOR_FEATURE_ID]][
                        row[KEY_FOR_VALUE_ID]
                    ].append(volume_and_doculect_id)

        feature_name_for_feature_id = read_dict_from_2_csv_columns(
            self.file_with_features,
            key_col=KEY_FOR_ID,
            val_col=KEY_FOR_RUSSIAN,
        )

        value_name_for_value_id = read_dict_from_2_csv_columns(
            self.file_with_listed_values, key_col=KEY_FOR_ID, val_col=KEY_FOR_RUSSIAN
        )

        content = (
            f"# Значения типа `{self.value_type}`\nОглавление файла открывается кнопкой"
            " сверху слева рядом с индикатором количества строк."
        )

        for feature_id in feature_name_for_feature_id:
            content += f"\n\n## {feature_id} — {feature_name_for_feature_id[feature_id]}\n"

            for value_id in feature_to_value_to_doculects[feature_id]:
                content += (
                    f"\n- **{value_name_for_value_id[value_id]}** ({value_id}): кол-во"
                    " языков —"
                    f" **{len(feature_to_value_to_doculects[feature_id][value_id])}**"
                )

        with output_file.open(mode="w+", encoding="utf-8") as fh:
            fh.write(content)

    def write_grouped_by_volume_and_doculect(self, output_file: Path) -> None:
        pass


if __name__ == "__main__":
    lister = ListedValueLister()
    lister.write_grouped_by_feature()
