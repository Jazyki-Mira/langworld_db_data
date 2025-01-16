from copy import copy
from pathlib import Path

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR
from langworld_db_data.featureprofiletools.feature_profile_reader import FeatureProfileReader
from langworld_db_data.featureprofiletools.feature_profile_writer_from_dictionary import (  # noqa E501
    FeatureProfileWriterFromDictionary,
)
from langworld_db_data.validators.feature_profile_validator import (
    FeatureProfileValidator,
    NotStatedInsteadOfNotApplicableError,
    ValueTypeValidationError,
)


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
        output_dir: Path = FEATURE_PROFILES_DIR,
        write_even_if_no_changes: bool = False,
    ):
        self.feature_profiles = sorted(list(dir_with_feature_profiles.glob("*.csv")))
        self.output_dir = output_dir

        self.reader = FeatureProfileReader
        self.validator = FeatureProfileValidator()
        self.writer = FeatureProfileWriterFromDictionary

        self.write_even_if_no_changes = write_even_if_no_changes

    def replace_not_stated_with_not_applicable_in_all_profiles_according_to_rules(
        self,
    ) -> None:
        # Setting the boolean attributes here, so that a validator with different paths
        # could be connected and it would still have the necessary settings
        self.validator.must_throw_error_at_not_applicable_rule_breach = True
        # this is not the subject of this function, so setting to False:
        self.validator.must_throw_error_at_feature_or_value_name_mismatch = False

        print("\nLooking for values of type `not_stated` that should be `not_applicable`")

        for file in self.feature_profiles:
            changes_made = False

            print(f"\n{file.name}")

            profile = self.reader.read_feature_profile_as_dict_from_file(file)
            amended_profile = copy(profile)

            relevant_feature_id_and_value_pairs = (
                (feature_id, value)
                for (feature_id, value) in profile.items()
                if feature_id in self.validator.not_applicable_trigger_values_for_feature_id
            )

            for feature_id, value in relevant_feature_id_and_value_pairs:

                try:
                    self.validator.check_one_feature_that_may_need_not_applicable_type(
                        profile=profile,
                        feature_id=feature_id,
                        file_name_for_error_msg=file.name,
                    )
                except NotStatedInsteadOfNotApplicableError:
                    print(f"{feature_id}: replacing `not_stated` with 'not_applicable'")
                    amended_profile[feature_id].value_type = "not_applicable"
                    changes_made = True
                except ValueTypeValidationError as e:
                    print(f"Type mismatch cannot be fixed automatically. {e}")

            if changes_made or self.write_even_if_no_changes:
                self.writer.write(
                    feature_dict=amended_profile, output_path=self.output_dir / file.name
                )


if __name__ == "__main__":
    NotApplicableSetter().replace_not_stated_with_not_applicable_in_all_profiles_according_to_rules()  # pragma: no cover
