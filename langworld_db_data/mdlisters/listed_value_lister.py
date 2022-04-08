from pathlib import Path

from langworld_db_data.constants.paths import (
    FEATURE_PROFILES_DIR,
    FILE_WITH_LISTED_VALUES,
    FILE_WITH_NAMES_OF_FEATURES,
    DISCUSSION_FILE_WITH_LISTED_VALUES,
)
from langworld_db_data.mdlisters.abstract_value_lister import AbstractValueLister
from langworld_db_data.filetools.csv_xls import read_csv, read_dict_from_2_csv_columns


class ListedValueLister(AbstractValueLister):
    def __init__(self, dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR):
        super().__init__(value_type='listed', dir_with_feature_profiles=dir_with_feature_profiles)
    
    def write_grouped_by_feature(
        self, output_file: Path = DISCUSSION_FILE_WITH_LISTED_VALUES
    ):

        feature_ids = [
            row['id'] for row in
            read_csv(FILE_WITH_NAMES_OF_FEATURES, read_as='dicts')
        ]

        rows_with_listed_values = read_csv(FILE_WITH_LISTED_VALUES, read_as='dicts')

        feature_to_value_to_doculects = {
            feature_id: {
                row['id']: [] for row in rows_with_listed_values if row['feature_id'] == feature_id
            }
            for feature_id in feature_ids
        }

        for volume_and_doculect_id in self.filtered_rows_for_volume_doculect_id:
            for row in self.filtered_rows_for_volume_doculect_id[volume_and_doculect_id]:
                feature_to_value_to_doculects[row['feature_id']][row['value_id']].append(volume_and_doculect_id)

        feature_name_for_feature_id = read_dict_from_2_csv_columns(
            FILE_WITH_NAMES_OF_FEATURES,
            key_col='id',
            val_col='ru',
        )

        value_name_for_value_id = read_dict_from_2_csv_columns(
            FILE_WITH_LISTED_VALUES,
            key_col='id',
            val_col='ru'
        )

        content = (
            f'# Значения типа `{self.value_type}`\n'
            'Оглавление файла открывается кнопкой сверху слева рядом с индикатором количества строк.'
        )

        for feature_id in feature_name_for_feature_id:
            content += f'\n\n## {feature_id} — {feature_name_for_feature_id[feature_id]}\n'

            for value_id in feature_to_value_to_doculects[feature_id]:
                content += f'\n- **{value_name_for_value_id[value_id]}** ({value_id}): ' \
                           f'кол-во языков — **{len(feature_to_value_to_doculects[feature_id][value_id])}**'

                # # This is good but leads to a very large file being generated. GitHub refuses to show its content.
                # if not feature_to_value_to_doculects[feature_id][value_id]:
                #     content += '_Нет языков_'
                #
                # else:
                #     for volume_and_doculect_id in feature_to_value_to_doculects[feature_id][value_id]:
                #         volume, doculect_id = volume_and_doculect_id.split(':')
                #         content += (
                #             f'[{self.doculect_ru_for_doculect_id[doculect_id]}]'
                #             f'(../feature_profiles/{doculect_id}.csv)<sub>{volume}</sub>, '
                #         )
                #     content = content[:-2]  # removing last ', '

        # print(content)

        with output_file.open(mode='w+', encoding='utf-8') as fh:
            fh.write(content)

    def write_grouped_by_volume_and_doculect(
            self, output_file: Path
    ):
        pass


if __name__ == '__main__':
    lister = ListedValueLister()
    lister.write_grouped_by_feature()
