from pathlib import Path

from langworld_db_data.constants.paths import (
    DISCUSSION_FILE_BY_DOCULECT,
    DISCUSSION_FILE_BY_FEATURE,
    FEATURE_PROFILES_DIR,
    FILE_WITH_DOCULECTS,
    FILE_WITH_NAMES_OF_FEATURES,
)
from langworld_db_data.filetools.csv_xls import read_csv, read_dict_from_2_csv_columns


class CustomValueLister:
    def __init__(self, dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR):
        self.doculect_ru_for_doculect_id = read_dict_from_2_csv_columns(
            FILE_WITH_DOCULECTS, 'id', 'name_ru'
        )

        self.feature_ru_for_feature_id = read_dict_from_2_csv_columns(
            FILE_WITH_NAMES_OF_FEATURES, 'id', 'ru'
        )

        self.encyclopedia_volume_for_doculect_id = read_dict_from_2_csv_columns(
            FILE_WITH_DOCULECTS, 'id', 'encyclopedia_volume_id'
        )

        # replace empty values with zeroes for sorting
        for key in self.encyclopedia_volume_for_doculect_id:
            if not self.encyclopedia_volume_for_doculect_id[key]:
                self.encyclopedia_volume_for_doculect_id[key] = '0'

        self.custom_rows_for_volume_doculect_id = {}

        list_of_files = sorted(
            list(dir_with_feature_profiles.glob('*.csv')),
            key=lambda f: (int(self.encyclopedia_volume_for_doculect_id[f.stem]), f.stem)
        )

        for file in list_of_files:
            key = f'{self.encyclopedia_volume_for_doculect_id[file.stem]}:{file.stem}'
            self.custom_rows_for_volume_doculect_id[key] = [
                row for row in read_csv(file, read_as='dicts')
                if row['value_type'] == 'custom'
            ]

    def write_grouped_by_volume_and_doculect(
            self, output_file: Path = DISCUSSION_FILE_BY_DOCULECT
    ):
        content = (
            '# Значения типа `custom` с группировкой по томам и языкам\n'
            'Оглавление файла открывается кнопкой сверху слева рядом с индикатором количества строк.\n\n'
            'Файл с группировкой по **признакам** лежит [здесь](custom_values_by_feature.md).\n'
        )
        current_volume = ''

        for volume_doculect_id in self.custom_rows_for_volume_doculect_id:
            if not self.custom_rows_for_volume_doculect_id[volume_doculect_id]:
                continue

            volume, doculect_id = volume_doculect_id.split(':')[0], volume_doculect_id.split(':')[1]
            if volume != current_volume:
                content += f'## Том {volume}\n'
                current_volume = volume

            content += (
                f'### [{self.doculect_ru_for_doculect_id[doculect_id]}]'
                f'(../feature_profiles/{doculect_id}.csv)\n\n'
            )
            for row in self.custom_rows_for_volume_doculect_id[volume_doculect_id]:
                content += (
                    f'- **{row["feature_id"]}** ({self.feature_ru_for_feature_id[row["feature_id"]]}): '
                    f'{row["value_ru"]}'
                )
                if row['comment_ru']:
                    content += f'\n\n\t_Комментарий: {row["comment_ru"]}_'
                content += '\n'
            content += '\n'

        # print(content)
        with output_file.open(mode='w+', encoding='utf-8') as fh:
            fh.write(content)

    def write_grouped_by_feature(
        self, output_file: Path = DISCUSSION_FILE_BY_FEATURE
    ):
        rows_with_custom_values = []

        for volume_doculect_id in self.custom_rows_for_volume_doculect_id:
            if self.custom_rows_for_volume_doculect_id[volume_doculect_id]:
                rows_with_custom_values += [
                    [
                        volume_doculect_id.split(':')[1],
                        row['feature_id'],
                        row['value_ru'],
                        row['comment_ru']
                    ]
                    for row in self.custom_rows_for_volume_doculect_id[volume_doculect_id]
                ]

        rows_sorted_by_feature = sorted(
            rows_with_custom_values,
            key=lambda row: (
                row[1].split('-')[0], # feature letter
                int(row[1].split('-')[1]),  # feature number
                row[2])
        )

        content = (
            '# Значения типа `custom` с группировкой по признакам\n'
            'Оглавление файла открывается кнопкой сверху слева рядом с индикатором количества строк.\n\n'
            'Файл с группировкой по **томам и языкам** лежит [здесь](custom_values_by_volume_and_doculect_sample.md).\n'
        )

        current_feature = ''
        current_value = ''

        for row in rows_sorted_by_feature:
            feature = row[1]
            if feature != current_feature:
                content += f'\n## {feature}: {self.feature_ru_for_feature_id[feature]}\n'
                current_feature = feature
                current_value = ''

            value = row[2]

            if value.lower() != current_value.lower():
                content += (
                    f'\n- {row[2]}: '
                    f'[{self.doculect_ru_for_doculect_id[row[0]]}]'
                    f'(../feature_profiles/{row[0]}.csv)'
                )
                current_value = value
            else:
                content += f', [{self.doculect_ru_for_doculect_id[row[0]]}](../feature_profiles/{row[0]}.csv)'

        # print(content)

        with output_file.open(mode='w+', encoding='utf-8') as fh:
            fh.write(content)


if __name__ == '__main__':
    lister = CustomValueLister()
    lister.write_grouped_by_volume_and_doculect()
    lister.write_grouped_by_feature()
