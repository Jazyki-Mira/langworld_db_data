from pathlib import Path
from typing import Optional

from langworld_db_data.adders.adder import Adder, AdderError, SEPARATOR
from langworld_db_data.constants.paths import FILE_WITH_CATEGORIES, FILE_WITH_NAMES_OF_FEATURES
from langworld_db_data.filetools.csv_xls import read_csv, write_csv
from langworld_db_data.filetools.txt import remove_extra_space

INDEX_THRESHOLD_FOR_REGULAR_FEATURE_IDS = 100


class FeatureAdderError(AdderError):
    pass


class FeatureAdder(Adder):
    def __init__(
            self,
            *,
            file_with_categories: Path = FILE_WITH_CATEGORIES,
            input_file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
            # ability to give a different output file is mostly for testing:
            output_file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
            **kwargs):
        # I know **kwargs removes argument hinting, but to repeat all arguments will make too many lines.
        # All arguments are keyword-only, so the wrong/mistyped argument cannot be passed.
        super().__init__(**kwargs)
        self.file_with_categories = file_with_categories
        self.input_file_with_features = input_file_with_features
        self.output_file_with_features = output_file_with_features

    def add_feature(
            self,
            category_id: str,
            feature_en: str,
            feature_ru: str,
            listed_values_to_add: list[dict],
            index_of_new_feature: Optional[int] = None,
            insert_after_index: Optional[int] = None,
    ):
        
        _ = remove_extra_space
        cat_id, feat_en, feat_ru = _(category_id), _(feature_en), _(feature_ru)

        if not (cat_id and feat_en and feat_ru and listed_values_to_add):
            raise FeatureAdderError(
                f'Some of the values passed are empty: '
                f'{cat_id=}, {feat_ru=}, {feat_en=}, {listed_values_to_add=}'
            )
        
        for item in listed_values_to_add:
            if not ('en' in item and 'ru' in item):
                raise FeatureAdderError(f"Listed value must have keys 'en' and 'ru'. Your value: {item}")

        if cat_id not in [row['id'] for row in read_csv(self.file_with_categories, read_as='dicts')]:
            raise FeatureAdderError(f'Category ID <{cat_id}> not found in file {self.file_with_categories.name}')

        rows_with_features = read_csv(self.input_file_with_features, read_as='dicts')
        if (
                feat_en in [row['en'] for row in rows_with_features]
                or feat_ru.strip() in [row['ru'] for row in rows_with_features]
                # note that this check should not be restricted to one feature category
        ):
            raise FeatureAdderError(f'English or Russian feature name is already present in list of features')

        feature_id_to_add_after = None
        if insert_after_index is not None:
            feature_id_to_add_after = f'{cat_id}{SEPARATOR}{insert_after_index}'

            if feature_id_to_add_after not in [row['id'] for row in rows_with_features]:
                raise FeatureAdderError(
                    f'Cannot add feature after {cat_id}{SEPARATOR}{insert_after_index}: '
                    f'There is no feature with index {index_of_new_feature} in category {cat_id}.')

        id_of_new_feature = self._generate_feature_id(
            category_id=cat_id,
            custom_index_of_new_feature=index_of_new_feature,
        )
        
        print(f'\nAdding feature {id_of_new_feature} ({feature_en} / {feature_ru}) to list of features', end=' ')
        row_to_add = {'id': id_of_new_feature, 'en': feat_en, 'ru': feat_ru}

        if insert_after_index is None:
            print(f'after the last feature in category {cat_id}')
            rows_to_write = (
                [row for row in rows_with_features if row['id'].split(SEPARATOR)[0] <= cat_id]
                + [row_to_add]
                + [row for row in rows_with_features if row['id'].split(SEPARATOR)[0] > cat_id]
            )
        else:
            print(f'after feature {feature_id_to_add_after}')
            rows_to_write = []
            for row in rows_with_features:
                rows_to_write.append(row)
                if row['id'] == feature_id_to_add_after:
                    rows_to_write.append(row_to_add)

        write_csv(
            rows=rows_to_write,
            path_to_file=self.output_file_with_features,
            overwrite=True,
            delimiter=','
        )

        print(f'\nProcessing new values in {id_of_new_feature}')
        value_rows = read_csv(self.input_file_with_listed_values, read_as='dicts')

        for i, new_listed_value in enumerate(listed_values_to_add, start=1):
            value_id = f'{id_of_new_feature}{SEPARATOR}{i}'

            print(f'\nAdding new value (ID {value_id} - {new_listed_value["ru"]}) to file with listed values')
            row_to_add = {
                'id': value_id,
                'feature_id': id_of_new_feature,
                'en': new_listed_value['en'],
                'ru': new_listed_value['ru'],
            }

            if feature_id_to_add_after is None:
                for row_index, row in enumerate(value_rows):
                    if row['feature_id'].split(SEPARATOR)[0] > cat_id:
                        value_rows.insert(row_index, row_to_add)
                        break
            else:
                feature_found = False
                for row_index, row in enumerate(value_rows):

                    if row['feature_id'] == id_of_new_feature:
                        # we are in the block of newly added values, don't have to do anything in these lines
                        continue

                    if row['feature_id'] == feature_id_to_add_after and not feature_found:
                        # found beginning of block of values for relevant feature
                        feature_found = True
                    elif row['feature_id'] != feature_id_to_add_after and feature_found:
                        # found end of block, can insert new value right before current row
                        value_rows.insert(row_index, row_to_add)
                        break

        # for row in value_rows:
        #     print(row)
        write_csv(value_rows, self.output_file_with_listed_values, overwrite=True, delimiter=',')

            # print(f'Adding new value (ID {value_id} - {new_listed_value["ru"]}) to feature profiles')
            #
            # for file in self.input_feature_profiles:
            #     profile_rows = read_csv(file, read_as='dicts')
            #
            #     row_to_add = {
            #         'feature_id': id_of_new_feature, 'feature_name_ru': feat_ru,
            #         'value_type': 'not_stated',
            #         'value_id': value_id,
            #         'value_ru': new_listed_value['ru'],
            #         'comment_ru': '', 'comment_en': '',
            #     }
            #
            #     if insert_after_index is None:
            #         profile_rows_to_write = (
            #                 [row for row in profile_rows if row['feature_id'].split(SEPARATOR)[0] <= cat_id]
            #                 + [row_to_add]
            #                 + [row for row in profile_rows if row['feature_id'].split(SEPARATOR)[0] > cat_id]
            #         )
            #     else:
            #         profile_rows_to_write = []
            #         for row in profile_rows:
            #             rows_to_write.append(row)
            #             if row['feature_id'] == feature_id_to_add_after:
            #                 rows_to_write.append(row_to_add)
            #
            #     write_csv(
            #         profile_rows_to_write,
            #         self.output_dir_with_feature_profiles / file.name,
            #         overwrite=True,
            #         delimiter=','
            #     )

    def _generate_feature_id(
            self,
            category_id: str,
            custom_index_of_new_feature: Optional[int],
    ):
        """
        Generates feature ID. If custom feature index is given, tries to use it.
        Otherwise, takes the largest feature ID that is **less than 100**
        (to reserve indices that are higher than 100 for custom feature indices)
        and produces feature ID with next index (plus one).
        """
        if custom_index_of_new_feature is not None and custom_index_of_new_feature < INDEX_THRESHOLD_FOR_REGULAR_FEATURE_IDS:
            raise FeatureAdderError(
                f'For clarity, manual feature indices must be greater than {INDEX_THRESHOLD_FOR_REGULAR_FEATURE_IDS} '
                f'(you gave {custom_index_of_new_feature}).'
            )

        feature_ids_in_category = [
            row['id'] for row in read_csv(self.input_file_with_features, read_as='dicts')
            if row['id'].startswith(f'{category_id}{SEPARATOR}')
        ]

        if custom_index_of_new_feature is None:
            largest_index_under_100 = max(
                int(feature_id.split(SEPARATOR)[1]) for feature_id in feature_ids_in_category
                if int(feature_id.split(SEPARATOR)[1]) < INDEX_THRESHOLD_FOR_REGULAR_FEATURE_IDS
            )
            return f'{category_id}{SEPARATOR}{largest_index_under_100 + 1}'

        custom_index_str = str(custom_index_of_new_feature)

        if f'{category_id}{SEPARATOR}{custom_index_str}' in feature_ids_in_category:
            raise FeatureAdderError(
                f'Feature index {custom_index_str} already in use in category {category_id}'
            )
        else:
            return f'{category_id}{SEPARATOR}{custom_index_str}'


if __name__ == '__main__':
    pass
