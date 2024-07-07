import re
from pathlib import Path

from langworld_db_data.constants.literals import (
    ATOMIC_VALUE_SEPARATOR,
    AUX_ROW_MARKER,
    ID_SEPARATOR,
)
from langworld_db_data.constants.paths import (
    FEATURE_PROFILES_DIR,
    FILE_WITH_LISTED_VALUES,
    FILE_WITH_NAMES_OF_FEATURES,
    FILE_WITH_VALUE_TYPES,
)
from langworld_db_data.featureprofiletools.data_structures import ValueForFeatureProfileDictionary
from langworld_db_data.featureprofiletools.feature_profile_reader import FeatureProfileReader
from langworld_db_data.filetools.csv_xls import (
    check_csv_for_malformed_rows,
    check_csv_for_repetitions_in_column,
    read_dict_from_2_csv_columns,
)
from langworld_db_data.validators.validator import Validator, ValidatorError


class FeatureProfileValidatorError(ValidatorError):
    pass


class ValueTypeValidationError(FeatureProfileValidatorError):
    pass


class CustomInsteadOfNotApplicableError(ValueTypeValidationError):
    pass


class ExplicitGapInsteadOfNotApplicableError(ValueTypeValidationError):
    pass


class ListedInsteadOfNotApplicableError(ValueTypeValidationError):
    pass


class NotStatedInsteadOfNotApplicableError(ValueTypeValidationError):
    pass


class FeatureProfileValidator(Validator):
    def __init__(
        self,
        dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
        file_with_features: Path = FILE_WITH_NAMES_OF_FEATURES,
        file_with_listed_values: Path = FILE_WITH_LISTED_VALUES,
        file_with_value_types: Path = FILE_WITH_VALUE_TYPES,
        must_throw_error_at_feature_or_value_name_mismatch: bool = True,
        must_throw_error_at_not_applicable_rule_breach: bool = False,
    ):
        self.reader = FeatureProfileReader()
        self.valid_value_types = self._read_ids(file_with_value_types)

        self.feature_profiles = sorted(list(dir_with_feature_profiles.glob("*.csv")))

        for file in self.feature_profiles:
            check_csv_for_malformed_rows(file)
            for column_name in ("feature_id", "feature_name_ru"):
                check_csv_for_repetitions_in_column(file, column_name=column_name)

        self.feature_ru_for_feature_id = read_dict_from_2_csv_columns(
            file_with_features, key_col="id", val_col="ru"
        )
        self.feature_is_multiselect_for_feature_id = read_dict_from_2_csv_columns(
            file_with_features, key_col="id", val_col="is_multiselect"
        )
        self.not_applicable_trigger_values_for_feature_id: dict[str, list[str]] = {
            feature_id: trigger_values.split(", ")
            for feature_id, trigger_values in read_dict_from_2_csv_columns(
                file_with_features, key_col="id", val_col="not_applicable_if"
            ).items()
            if trigger_values  # we don't need features that don't depend on other features
        }
        self.value_ru_for_value_id = read_dict_from_2_csv_columns(
            file_with_listed_values, key_col="id", val_col="ru"
        )

        self.must_throw_error_at_feature_or_value_name_mismatch = (
            must_throw_error_at_feature_or_value_name_mismatch
        )
        self.must_throw_error_at_not_applicable_rule_breach = (
            must_throw_error_at_not_applicable_rule_breach
        )

    def validate(self) -> None:
        print(f"\nChecking feature profiles ({len(self.feature_profiles)} files)")
        for feature_profile in self.feature_profiles:
            self.validate_one_file(feature_profile)

    def validate_one_file(self, file: Path) -> None:
        try:
            data_from_profile = self.reader.read_feature_profile_as_dict_from_file(file)
        except ValueError as e:
            raise FeatureProfileValidatorError(e)

        file_name_for_error_msg = f"File {file.stem}"

        self._check_consistency_of_each_row(
            data_from_profile=data_from_profile,
            file_name_for_error_msg=file_name_for_error_msg,
        )

        try:
            self.check_all_features_that_may_need_not_applicable_type(
                profile=data_from_profile,
                file_name_for_error_msg=file_name_for_error_msg,
            )
        except ValueTypeValidationError as e:
            if self.must_throw_error_at_not_applicable_rule_breach:
                raise FeatureProfileValidatorError(e)
            else:
                print(e)

    def _check_consistency_of_each_row(
        self,
        data_from_profile: dict[str, ValueForFeatureProfileDictionary],
        file_name_for_error_msg: str,
    ) -> None:
        """Check whether each row in the profile contains accepted value for each value type."""
        for i, feature_id in enumerate(data_from_profile.keys(), start=1):
            if feature_id == AUX_ROW_MARKER:
                continue

            # possible absence of feature ID in file is caught when reading
            # data_from_profile
            data_row = data_from_profile[feature_id]

            row_name_for_error_msg = f"row {i + 1}"
            if data_row.value_type not in self.valid_value_types:
                raise FeatureProfileValidatorError(
                    f"{file_name_for_error_msg} contains invalid value type in {row_name_for_error_msg}"
                )

            if data_row.value_type == "custom":
                if data_row.value_id:
                    raise FeatureProfileValidatorError(
                        f"{file_name_for_error_msg} must not contain value ID"
                        f" {data_row.value_id} in {row_name_for_error_msg} or value type must be"
                        ' "listed"'
                    )
                if not data_row.value_ru:
                    raise FeatureProfileValidatorError(
                        f"{file_name_for_error_msg} does not contain value text "
                        f"in {row_name_for_error_msg}"
                    )

            elif data_row.value_type in (
                "not_stated",
                "not_applicable",
                "explicit_gap",
            ):
                if data_row.value_id or data_row.value_ru:
                    raise FeatureProfileValidatorError(
                        f"{file_name_for_error_msg} must not contain value ID or value text "
                        f"in {row_name_for_error_msg} or value type must be different"
                    )

            elif data_row.value_type == "listed":
                if self.feature_is_multiselect_for_feature_id[feature_id] == "1":
                    # validate each pair of value ID and value name
                    for value_id, value_ru in zip(
                        data_row.value_id.split(ATOMIC_VALUE_SEPARATOR),
                        data_row.value_ru.split(ATOMIC_VALUE_SEPARATOR),
                    ):
                        self._check_listed_value_id_is_valid_and_matches_value_name(
                            feature_id=feature_id,
                            value_id=value_id,
                            value_ru=value_ru,
                            file_name_for_error_msg=file_name_for_error_msg,
                            row_name_for_error_msg=row_name_for_error_msg,
                        )
                else:
                    self._check_listed_value_id_is_valid_and_matches_value_name(
                        feature_id=feature_id,
                        value_id=data_row.value_id,
                        value_ru=data_row.value_ru,
                        file_name_for_error_msg=file_name_for_error_msg,
                        row_name_for_error_msg=row_name_for_error_msg,
                    )

            if data_row.feature_name_ru != self.feature_ru_for_feature_id[feature_id]:
                message = (
                    f"{file_name_for_error_msg}, {row_name_for_error_msg}: feature name"
                    f" {data_row.feature_name_ru} in {row_name_for_error_msg} does not match name of"
                    " this feature in inventory"
                    f" ({self.feature_ru_for_feature_id[feature_id]})"
                )
                if self.must_throw_error_at_feature_or_value_name_mismatch:
                    raise FeatureProfileValidatorError(message)
                else:
                    print(message)

    def check_all_features_that_may_need_not_applicable_type(
        self,
        profile: dict[str, ValueForFeatureProfileDictionary],
        file_name_for_error_msg: str,
    ) -> None:
        """
        Check that features are `not_applicable` if there are corresponding
        "trigger" values in feature(s) they depend on.
        """
        for feature_id_to_check in self.not_applicable_trigger_values_for_feature_id:

            if profile[feature_id_to_check].value_type == "not_applicable":
                # No further checks needed if value type is already `not_applicable`
                # TODO BTW we should also check profiles for having `not_applicable`
                #  where it can't be `not_applicable` (i.e. the other way round)
                continue

            self.check_one_feature_that_may_need_not_applicable_type(
                profile=profile,
                feature_id=feature_id_to_check,
                file_name_for_error_msg=file_name_for_error_msg,
            )

    def check_one_feature_that_may_need_not_applicable_type(
        self,
        profile: dict[str, ValueForFeatureProfileDictionary],
        feature_id: str,
        file_name_for_error_msg: str,
    ):
        feature_id_to_check = feature_id  # for better understanding of code below
        value_being_inspected = profile[feature_id_to_check]
        value_type = value_being_inspected.value_type

        # Get value(s) of other feature(s) that would trigger `not_applicable`
        # in feature being currently inspected (the list will be empty if this feature
        # does not depend on any other feature)
        for n_a_trigger_value_id in self.not_applicable_trigger_values_for_feature_id[
            feature_id_to_check
        ]:
            # get ID of feature that may contain a trigger value for feature being inspected
            # (produce "A-1" from "A-1-1")
            trigger_feature_id = ID_SEPARATOR.join(n_a_trigger_value_id.split(ID_SEPARATOR)[:-1])
            value_of_trigger_feature = profile[trigger_feature_id]

            if value_of_trigger_feature.value_id == n_a_trigger_value_id:

                error_message = (
                    f"{file_name_for_error_msg}: Error in feature {feature_id_to_check} "
                    f'"{value_being_inspected.feature_name_ru}". '
                    f"It must be `not_applicable` because feature {trigger_feature_id} "
                    f'"{value_of_trigger_feature.feature_name_ru}" has value '
                    f"{value_of_trigger_feature.value_id} {value_of_trigger_feature.value_ru}."
                    f" However, feature {feature_id_to_check} has value "
                    f'{value_being_inspected.value_id} "{value_being_inspected.value_ru}" '
                    f"of type `{value_type}`."
                )

                # throw fine-grained exceptions for each type of value
                if value_type == "custom":
                    raise CustomInsteadOfNotApplicableError(error_message)

                if value_type == "explicit_gap":
                    raise ExplicitGapInsteadOfNotApplicableError(error_message)

                if value_type == "listed":
                    raise ListedInsteadOfNotApplicableError(error_message)

                if value_type == "not_stated":
                    raise NotStatedInsteadOfNotApplicableError(error_message)

    def _check_listed_value_id_is_valid_and_matches_value_name(
        self,
        feature_id: str,
        value_id: str,
        value_ru: str,
        file_name_for_error_msg: str,
        row_name_for_error_msg: str,
    ) -> None:
        if not re.match(rf"{feature_id}-\d+", value_id):
            raise FeatureProfileValidatorError(
                f"{file_name_for_error_msg} contains "
                f"invalid value ID {value_id} in {row_name_for_error_msg}"
            )

        # Validation of whether value name (here) and feature name (later on) in
        # feature profile match the names in inventories of features and values
        # respectively is only done for the purpose of clarity and readability.
        # Russian names of features and values from feature profiles
        # are not supposed to be used in code. Only IDs really matter.
        # This is why I allow to skip throwing exception in case of mismatch
        # (but prefer throwing it anyway).
        if value_ru != self.value_ru_for_value_id[value_id]:
            message = (
                f"{file_name_for_error_msg}, {row_name_for_error_msg}: value "
                f"{value_ru} for value ID {value_id} in {row_name_for_error_msg} "
                f"does not match name of this value in inventory (value ID {value_id} "
                f"should be {self.value_ru_for_value_id[value_id]})"
            )
            if self.must_throw_error_at_feature_or_value_name_mismatch:
                raise FeatureProfileValidatorError(message)
            else:
                print(message)


if __name__ == "__main__":
    FeatureProfileValidator().validate()  # pragma: no cover
