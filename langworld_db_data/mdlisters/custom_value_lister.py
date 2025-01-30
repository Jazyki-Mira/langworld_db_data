from pathlib import Path

from langworld_db_data.constants.literals import (
    ID_SEPARATOR,
    KEY_FOR_FEATURE_ID,
    KEY_FOR_RUSSIAN_COMMENT,
    KEY_FOR_RUSSIAN_NAME_OF_VALUE,
)
from langworld_db_data.constants.paths import (
    DISCUSSION_FILE_WITH_CUSTOM_VALUES_BY_DOCULECT,
    DISCUSSION_FILE_WITH_CUSTOM_VALUES_BY_FEATURE,
    FEATURE_PROFILES_DIR,
)
from langworld_db_data.mdlisters.abstract_value_lister import AbstractValueLister


class CustomValueLister(AbstractValueLister):
    def __init__(self, dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR):
        super().__init__(value_type="custom", dir_with_feature_profiles=dir_with_feature_profiles)

    def write_grouped_by_volume_and_doculect(
        self, output_file: Path = DISCUSSION_FILE_WITH_CUSTOM_VALUES_BY_DOCULECT
    ) -> None:
        content = (
            "# Значения типа `custom` с группировкой по томам и языкам\nОглавление"
            " файла открывается кнопкой сверху слева рядом с индикатором количества"
            " строк.\n\nФайл с группировкой по **признакам** лежит"
            " [здесь](custom_values_by_feature.md).\n"
        )
        current_volume = ""

        for volume_doculect_id in self.filtered_rows_for_volume_doculect_id:
            if not self.filtered_rows_for_volume_doculect_id[volume_doculect_id]:
                continue

            volume, doculect_id = (
                volume_doculect_id.split(":")[0],
                volume_doculect_id.split(":")[1],
            )
            if volume != current_volume:
                content += f"## Том {volume}\n"
                current_volume = volume

            content += (
                f"### [{self.doculect_ru_for_doculect_id[doculect_id]}]"
                f"(../feature_profiles/{doculect_id}.csv)\n\n"
            )
            for row in self.filtered_rows_for_volume_doculect_id[volume_doculect_id]:
                content += (
                    f"- **{row[KEY_FOR_FEATURE_ID]}**"
                    f" ({self.feature_ru_for_feature_id[row[KEY_FOR_FEATURE_ID]]}):"
                    f" {row[KEY_FOR_RUSSIAN_NAME_OF_VALUE]}"
                )
                if row[KEY_FOR_RUSSIAN_COMMENT]:
                    content += f"\n\n\t_Комментарий: {row[KEY_FOR_RUSSIAN_COMMENT]}_"
                content += "\n"
            content += "\n"

        # print(content)
        with output_file.open(mode="w+", encoding="utf-8") as fh:
            fh.write(content)

    def write_grouped_by_feature(
        self, output_file: Path = DISCUSSION_FILE_WITH_CUSTOM_VALUES_BY_FEATURE
    ) -> None:
        rows_with_custom_values = []

        for volume_doculect_id in self.filtered_rows_for_volume_doculect_id:
            if self.filtered_rows_for_volume_doculect_id[volume_doculect_id]:
                rows_with_custom_values += [
                    [
                        volume_doculect_id.split(":")[1],
                        row[KEY_FOR_FEATURE_ID],
                        row[KEY_FOR_RUSSIAN_NAME_OF_VALUE],
                        row[KEY_FOR_RUSSIAN_COMMENT],
                    ]
                    for row in self.filtered_rows_for_volume_doculect_id[volume_doculect_id]
                ]

        rows_sorted_by_feature = sorted(
            rows_with_custom_values,
            key=lambda row: (
                row[1].split(ID_SEPARATOR)[0],  # feature letter
                int(row[1].split(ID_SEPARATOR)[1]),  # feature number
                row[2],
            ),
        )

        content = (
            "# Значения типа `custom` с группировкой по признакам\nОглавление файла"
            " открывается кнопкой сверху слева рядом с индикатором количества"
            " строк.\n\nФайл с группировкой по **томам и языкам** лежит"
            " [здесь](custom_values_by_volume_and_doculect.md).\n"
        )

        current_feature = ""
        current_value = ""

        for row in rows_sorted_by_feature:
            feature = row[1]
            if feature != current_feature:
                content += f"\n## {feature}: {self.feature_ru_for_feature_id[feature]}\n"
                current_feature = feature
                current_value = ""

            value = row[2]

            if value.lower() != current_value.lower():
                content += (
                    f"\n- {row[2]}: "
                    f"[{self.doculect_ru_for_doculect_id[row[0]]}]"
                    f"(../feature_profiles/{row[0]}.csv)"
                )
                current_value = value
            else:
                content += (
                    f", [{self.doculect_ru_for_doculect_id[row[0]]}]"
                    f"(../feature_profiles/{row[0]}.csv)"
                )

        # print(content)

        with output_file.open(mode="w+", encoding="utf-8") as fh:
            fh.write(content)


if __name__ == "__main__":
    lister = CustomValueLister()
    lister.write_grouped_by_volume_and_doculect()
    lister.write_grouped_by_feature()
