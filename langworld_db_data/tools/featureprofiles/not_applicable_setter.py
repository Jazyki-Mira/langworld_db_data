from copy import copy
from pathlib import Path

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR
from langworld_db_data.tools.featureprofiles.feature_profile_reader import FeatureProfileReader
from langworld_db_data.tools.featureprofiles.feature_profile_writer_from_dictionary import (  # noqa E501
    FeatureProfileWriterFromDictionary,
)
from langworld_db_data.validators.feature_profile_validator import (
    FeatureProfileValidator,
    NotStatedInsteadOfNotApplicableError,
    ValueTypeValidationError,
)


class NotApplicableSetter:
    """A class for setting value type to `not_applicable` in feature profiles based on feature dependencies.

    This class automatically sets value type to 'not_applicable' for features that should not be applicable
    when certain other features have specific values. The dependency rules are stored in the features.csv file
    in the 'not_applicable_if' column, which specifies which feature values trigger the 'not_applicable' status
    in dependent features.

    For example, if feature A has a value that makes feature B irrelevant, feature B will be automatically
    set to 'not_applicable' if it was previously marked as 'not_stated'.

    Note that this class will not modify features that have already been filled with actual values or
    have been explicitly marked as something other than 'not_stated'. It is the responsibility of the
    validator to check for such cases and alert about potential issues.
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
