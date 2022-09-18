from copy import copy
from pathlib import Path

from langworld_db_data.constants.paths import (
    FEATURE_PROFILES_DIR,
    FILE_WITH_NOT_APPLICABLE_RULES,
)
from langworld_db_data.featureprofiletools.data_structures import ValueForFeatureProfileDictionary
from langworld_db_data.featureprofiletools.feature_profile_reader import FeatureProfileReader
from langworld_db_data.featureprofiletools.feature_profile_writer_from_dictionary import (
    FeatureProfileWriterFromDictionary)
from langworld_db_data.filetools.json_toml_yaml import read_json_toml_yaml


class NotApplicableSetter:
    """A class for setting value type to `not_applicable`
    in feature profiles according to rules listed in YAML file.

    If a certain feature has a certain value ID, all dependent
    features that have value type 'not_stated' (because the curator
    forgot to put 'not_applicable' when filling out the questionnaire)
    will get value type 'not_applicable'.

    Note that this class will not change values in dependent features
    that are wrong (i.e. not of type 'not_stated' and/or have some value text).
    It is a job of a validator to alert about such cases.
    """

    def __init__(
        self,
        dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
        file_with_rules: Path = FILE_WITH_NOT_APPLICABLE_RULES,
        output_dir: Path = FEATURE_PROFILES_DIR,
    ):
        self.feature_profiles = sorted(list(dir_with_feature_profiles.glob('*.csv')))
        self.rules = read_json_toml_yaml(file_with_rules)
        self.output_dir = output_dir

        self.reader = FeatureProfileReader
        self.writer = FeatureProfileWriterFromDictionary

    def replace_not_stated_with_not_applicable_in_all_profiles_according_to_rules(self) -> None:
        for file in self.feature_profiles:
            print(f'\nReading file {file.name}')

            data_from_profile = self.reader.read_feature_profile_as_dict_from_file(file)
            new_data = copy(data_from_profile)

            for feature_id in self.rules:

                # noinspection PyTypeChecker
                print(f"Feature ID {feature_id}, value ID to trigger 'not_applicable' rules for this feature: "
                      f"{self.rules[feature_id]['trigger']}. "
                      f'Value in {file.stem}: {data_from_profile[feature_id].value_id}')

                # noinspection PyTypeChecker
                if data_from_profile[feature_id].value_id == self.rules[feature_id]['trigger']:

                    # noinspection PyTypeChecker
                    for id_of_feature_to_be_changed in self.rules[feature_id]['features_to_get_not_applicable']:
                        print(f'Feature {id_of_feature_to_be_changed} to be set to "not applicable"')

                        # Only changing values that are of 'not_stated' type!
                        # All other value types are wrong, but errors must be triggered in a validator, not here
                        if new_data[id_of_feature_to_be_changed].value_type == 'not_stated':
                            new_data[id_of_feature_to_be_changed] = ValueForFeatureProfileDictionary(
                                feature_name_ru=data_from_profile[id_of_feature_to_be_changed].feature_name_ru,
                                value_type='not_applicable',
                                value_ru='',
                                value_id='',
                                comment_en=data_from_profile[id_of_feature_to_be_changed].comment_en,
                                comment_ru=data_from_profile[id_of_feature_to_be_changed].comment_ru,
                                page_numbers='',
                            )

            self.writer.write(feature_dict=new_data, output_path=self.output_dir / file.name)


if __name__ == '__main__':
    NotApplicableSetter().replace_not_stated_with_not_applicable_in_all_profiles_according_to_rules()
