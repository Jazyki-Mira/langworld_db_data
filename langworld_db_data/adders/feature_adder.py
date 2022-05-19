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
            feature_index: Optional[int] = None
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

        id_of_new_feature = self._generate_feature_id(
            category_id=cat_id,
            custom_feature_index=feature_index,
        )
        
        print(f'\nAdding feature {id_of_new_feature} ({feature_en} / {feature_ru}) to list of features')
        rows_to_write = (
            [row for row in rows_with_features if row['id'].split(SEPARATOR)[0] <= cat_id]
            + [{'id': id_of_new_feature, 'en': feat_en, 'ru': feat_ru}]
            + [row for row in rows_with_features if row['id'].split(SEPARATOR)[0] > cat_id]
        )                    
        write_csv(
            rows=rows_to_write,
            path_to_file=self.output_file_with_features,
            overwrite=True,
            delimiter=','
        )

        # either add at least one listed value right here along with feature creation
        # or change ListedValueAdder to create listed value with ID "X-1" if the feature
        # is present in list of features but does not have any listed values yet

        # Which Adder is going to add lines with 'not_stated' to feature profiles?

        # I think that it makes sense to create some listed values at first run, and
        # ListedValueAdder will deal with simpler cases when the feature is already present
        # and has some listed values

    def _generate_feature_id(
            self,
            category_id: str,
            custom_feature_index: Optional[int],
    ):
        """
        Generates feature ID. If custom feature index is given, tries to use it.
        Otherwise, takes the largest feature ID that is **less than 100**
        (to reserve indices that are higher than 100 for custom feature indices)
        and produces feature ID with next index (plus one).
        """
        if custom_feature_index is not None and custom_feature_index < INDEX_THRESHOLD_FOR_REGULAR_FEATURE_IDS:
            raise FeatureAdderError(
                f'For clarity, manual feature indices must be greater than {INDEX_THRESHOLD_FOR_REGULAR_FEATURE_IDS} '
                f'(you gave {str(custom_feature_index)}).'
            )

        feature_ids_in_category = [
            row['id'] for row in read_csv(self.input_file_with_features, read_as='dicts')
            if row['id'].startswith(f'{category_id}{SEPARATOR}')
        ]

        if custom_feature_index is None:
            largest_index_under_100 = max(
                int(feature_id.split(SEPARATOR)[1]) for feature_id in feature_ids_in_category
                if int(feature_id.split(SEPARATOR)[1]) < INDEX_THRESHOLD_FOR_REGULAR_FEATURE_IDS
            )
            return f'{category_id}{SEPARATOR}{str(largest_index_under_100 + 1)}'

        custom_index_str = str(custom_feature_index)

        if f'{category_id}{SEPARATOR}{custom_index_str}' in feature_ids_in_category:
            raise FeatureAdderError(
                f'Feature index {custom_index_str} already in use in category {category_id}'
            )
        else:
            return f'{category_id}{SEPARATOR}{custom_index_str}'


if __name__ == '__main__':
    pass
