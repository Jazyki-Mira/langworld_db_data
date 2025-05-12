from pathlib import Path
from typing import Optional, Union

from langworld_db_data import ObjectWithPaths
from langworld_db_data.constants.literals import (
    AUX_ROW_MARKER,
    ID_SEPARATOR,
    KEY_FOR_ENGLISH,
    KEY_FOR_ENGLISH_COMMENT,
    KEY_FOR_FEATURE_ID,
    KEY_FOR_ID,
    KEY_FOR_RUSSIAN,
    KEY_FOR_RUSSIAN_COMMENT,
    KEY_FOR_RUSSIAN_NAME_OF_FEATURE,
    KEY_FOR_RUSSIAN_NAME_OF_VALUE,
    KEY_FOR_VALUE_ID,
    KEY_FOR_VALUE_TYPE,
)
from langworld_db_data.constants.paths import FILE_WITH_CATEGORIES, FILE_WITH_NAMES_OF_FEATURES
from langworld_db_data.tools.files.csv_xls import (
    read_column_from_csv,
    read_dicts_from_csv,
    write_csv,
)
from langworld_db_data.tools.files.txt import remove_extra_space

INDEX_THRESHOLD_FOR_REGULAR_FEATURE_IDS = 100


class FeatureAdderError(Exception):
    pass


class FeatureAdder(ObjectWithPaths):
    def __init__(
        self,
        *,
        file_with_categories: Path = FILE_WITH_CATEGORIES,
        input_file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
        # ability to give a different output file is mostly for testing:
        output_file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
        **kwargs,
    ):
        # I know **kwargs removes argument hinting, but to repeat all arguments will
        # make too many lines. All arguments are keyword-only, so the wrong/mistyped
        # argument cannot be passed.
        super().__init__(**kwargs)
        self.file_with_categories = file_with_categories
        self.input_file_with_features = input_file_with_features
        self.output_file_with_features = output_file_with_features

    def add_feature(
        self,
        category_id: str,
        feature_en: str,
        feature_ru: str,
        listed_values_to_add: list[dict[str, str]],
        index_to_assign: Union[int, None],
    ) -> None:
        _ = remove_extra_space
        cat_id, feat_en, feat_ru = _(category_id), _(feature_en), _(feature_ru)

        if not (cat_id and feat_en and feat_ru and listed_values_to_add):
            raise FeatureAdderError(
                "Some of the values passed are empty: "
                f"{cat_id=}, {feat_ru=}, {feat_en=}, {listed_values_to_add=}"
            )

        for item in listed_values_to_add:
            if not (KEY_FOR_ENGLISH in item and KEY_FOR_RUSSIAN in item):
                raise FeatureAdderError(
                    f"Listed value must have keys 'en' and 'ru'. Your value: {item}"
                )

        if cat_id not in read_column_from_csv(
            path_to_file=self.file_with_categories, column_name=KEY_FOR_ID
        ):
            raise FeatureAdderError(
                f"Category ID <{cat_id}> not found in file" f" {self.file_with_categories.name}"
            )

        try:
            feature_id = self._add_feature_to_inventory_of_features(
                category_id=cat_id,
                new_feature_en=feat_en,
                new_feature_ru=feat_ru,
                index_to_assign=index_to_assign,
            )
        except ValueError as e:
            raise FeatureAdderError(f"Failed to add new feature to inventory of features. {e}")

        self._add_values_of_new_feature_to_inventory_of_listed_values(
            category_id=category_id,
            feature_id=feature_id,
            listed_values_to_add=listed_values_to_add,
        )

        self._add_feature_to_feature_profiles(
            new_feature_id=feature_id,
            feature_ru=feat_ru,
        )
    
    def _add_feature_to_inventory_of_features(
        self,
        category_id: str,
        new_feature_en: str,
        new_feature_ru: str,
        index_to_assign: Union[int, None],
    ) -> str:
        """
        Add new feature to the inventory of features. Return ID of new feature.

        index_to_assign means number that must be assigned to the new feature within the category, ex. 13 for A-13.
        If no index_to_assign is given, the new feature will be added as the last one in the category.
        index_to_assign must be greater than 0.
        """
        rows = read_dicts_from_csv(self.input_file_with_features)

        if new_feature_en in [row[KEY_FOR_ENGLISH] for row in rows] or new_feature_ru in [
            row[KEY_FOR_RUSSIAN] for row in rows
        ]:
            # note that this check should not be restricted to one feature category
            raise FeatureAdderError(
                "English or Russian feature name is already present in list of features"
            )

        id_of_new_feature = "R-0"

        print(
            (
                f"\nAdding feature {id_of_new_feature} ({new_feature_en} / {new_feature_ru}) to"
                " list of features"
            ),
            end=" ",
        )

        row_to_add = {
            KEY_FOR_ID: id_of_new_feature,
            KEY_FOR_ENGLISH: new_feature_en,
            KEY_FOR_RUSSIAN: new_feature_ru,
        }

        return id_of_new_feature

    def _add_values_of_new_feature_to_inventory_of_listed_values(
        self,
        category_id: str,
        feature_id: str,
        listed_values_to_add: list[dict[str, str]],
    ) -> None:
        print(f"\nAdding new values in {feature_id} to file with listed values")

        rows_to_add_to_file_with_listed_values = []

        for i, new_listed_value in enumerate(listed_values_to_add, start=1):
            value_id = f"{feature_id}{ID_SEPARATOR}{i}"
            print(f"Value ID {value_id} - {new_listed_value[KEY_FOR_RUSSIAN]} will be added")
            rows_to_add_to_file_with_listed_values.append(
                {
                    KEY_FOR_ID: value_id,
                    KEY_FOR_FEATURE_ID: feature_id,
                    KEY_FOR_ENGLISH: new_listed_value[KEY_FOR_ENGLISH],
                    KEY_FOR_RUSSIAN: new_listed_value[KEY_FOR_RUSSIAN],
                }
            )

        # value_rows_with_new_values_inserted = self.insert_rows(
        #     rows_before_insertion=read_dicts_from_csv(self.input_file_with_listed_values),
        #     rows_to_add=rows_to_add_to_file_with_listed_values,
        #     category_id=category_id,
        #     feature_id_to_add_after=feature_id_to_add_after,
        # )

        # write_csv(
        #     rows=value_rows_with_new_values_inserted,
        #     path_to_file=self.output_file_with_listed_values,
        #     overwrite=True,
        #     delimiter=",",
        # )
    
    def _add_feature_to_feature_profiles(
        self,
        feature_id: str,
        feature_ru: str,
    ) -> None:
        # I think this one will call two further methods -- first for updating value IDs and then for inserting the feature itself
        
        print(
            f"\nAdding feature {feature_id} to feature profiles with value type"
            " 'not_stated'"
        )

        for file in self.input_feature_profiles:
            pass
            # feature_profile_rows_with_new_features_inserted = self.insert_rows(
            #     rows_before_insertion=read_dicts_from_csv(file),
            #     rows_to_add=[
            #         {
            #             KEY_FOR_FEATURE_ID: feature_id,
            #             KEY_FOR_RUSSIAN_NAME_OF_FEATURE: feature_ru,
            #             KEY_FOR_VALUE_TYPE: "not_stated",
            #             KEY_FOR_VALUE_ID: "",
            #             KEY_FOR_RUSSIAN_NAME_OF_VALUE: "",
            #             KEY_FOR_RUSSIAN_COMMENT: "",
            #             KEY_FOR_ENGLISH_COMMENT: "",
            #         }
            #     ],
            #     category_id=category_id,
            #     feature_id_to_add_after=feature_id_to_add_after,
            # )

            # write_csv(
            #     rows=feature_profile_rows_with_new_features_inserted,
            #     path_to_file=self.output_dir_with_feature_profiles / file.name,
            #     overwrite=True,
            #     delimiter=",",
            # )

    @staticmethod
    def insert_rows(
        rows_before_insertion: list[dict[str, str]],
        rows_to_add: list[dict[str, str]],
        category_id: str,
        feature_id_to_add_after: Optional[str],
    ) -> list[dict[str, str]]:
        rows = rows_before_insertion[:]

        if feature_id_to_add_after is None:
            for row_index, row in enumerate(rows):
                if (
                    row[KEY_FOR_FEATURE_ID].split(ID_SEPARATOR)[0] > category_id
                    or row[KEY_FOR_FEATURE_ID] == AUX_ROW_MARKER
                ):
                    return rows[:row_index] + rows_to_add + rows[row_index:]
            else:  # we have reached end of file
                return rows + rows_to_add
        else:
            found_feature_to_add_after = False
            for row_index, row in enumerate(rows):
                if (
                    row[KEY_FOR_FEATURE_ID] == feature_id_to_add_after
                    and not found_feature_to_add_after
                ):
                    # found beginning of block of values for relevant feature
                    found_feature_to_add_after = True
                elif (
                    row[KEY_FOR_FEATURE_ID] != feature_id_to_add_after
                    and found_feature_to_add_after
                ):
                    # found end of block
                    return rows[:row_index] + rows_to_add + rows[row_index:]
            else:
                return rows + rows_to_add


if __name__ == "__main__":
    FeatureAdder.add_feature(
        category_id="",
        feature_en="",
        feature_ru="",
        listed_values_to_add=[],
    )
