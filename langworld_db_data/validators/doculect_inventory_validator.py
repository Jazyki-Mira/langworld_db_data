from collections import defaultdict
from pathlib import Path

from langworld_db_data.constants.paths import (
    FEATURE_PROFILES_DIR,
    FILE_WITH_DOCULECTS,
    FILE_WITH_GENEALOGY_NAMES,
)
from langworld_db_data.filetools.csv_xls import (
    check_csv_for_malformed_rows,
    check_csv_for_repetitions_in_column,
    read_dicts_from_csv,
)
from langworld_db_data.validators.validator import Validator, ValidatorError


class DoculectInventoryValidatorError(ValidatorError):
    pass


class DoculectInventoryValidator(Validator):
    def __init__(
        self,
        dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
        file_with_doculects: Path = FILE_WITH_DOCULECTS,
        file_with_genealogy_names: Path = FILE_WITH_GENEALOGY_NAMES,
    ):
        self.feature_profiles: list[Path] = sorted(
            list(dir_with_feature_profiles.glob("*.csv"))
        )
        self.names_of_feature_profiles: set[str] = {
            f.stem for f in self.feature_profiles
        }

        check_csv_for_malformed_rows(file_with_doculects)
        try:
            check_csv_for_repetitions_in_column(file_with_doculects, column_name="id")
        except ValueError as e:
            raise DoculectInventoryValidatorError(str(e))

        self.doculects: list[dict] = read_dicts_from_csv(file_with_doculects)
        self.doculect_ids = {d["id"] for d in self.doculects}

        self.genealogy_family_ids = set(self._read_ids(file_with_genealogy_names))

        self.has_feature_profile_for_doculect_id = {
            d["id"]: d["has_feature_profile"] for d in self.doculects
        }

    def validate(self) -> None:
        """
        Runs all checks.

        :raises DoculectInventoryValidatorError
        """
        print("\nValidating inventory of doculects")
        self._check_family_ids_in_genealogy()
        self._check_uniqueness_of_coordinates()
        self._match_doculects_to_files()
        self._match_files_to_doculects()

    def _check_family_ids_in_genealogy(self) -> None:
        """Checks that ID of family for every doculect
        matches ID in file with names of families.

        :raises DoculectInventoryValidatorError
        """
        for doculect in self.doculects:
            if doculect["family_id"] not in self.genealogy_family_ids:
                raise DoculectInventoryValidatorError(
                    f"{doculect['id'].capitalize()}: genealogy family ID {doculect['family_id']} "
                    f"not found in genealogy inventory"
                )
        print(
            "OK: ID of language family for each doculect is present in genealogy inventory"
        )

    def _check_uniqueness_of_coordinates(self) -> None:
        """Checks that all pairs of coordinates are unique.

        :raises DoculectInventoryValidatorError
        """
        coords_to_doculect_ids: dict[tuple[str, str], list[str]] = defaultdict(list)
        for doculect in self.doculects:
            coords_to_doculect_ids[
                (doculect["latitude"], doculect["longitude"])
            ].append(f"{doculect['id']} ({doculect['glottocode']})")

        coords_with_more_than_one_doculect = [
            pair
            for pair in coords_to_doculect_ids
            if len(coords_to_doculect_ids[pair]) > 1
        ]

        if coords_with_more_than_one_doculect:
            print("\nFound doculects with identical coordinates:")
            for pair in coords_with_more_than_one_doculect:
                print(", ".join(coords_to_doculect_ids[pair]), ": ", pair, sep="")
            raise DoculectInventoryValidatorError(
                "Some doculects have identical coordinates"
            )

        print("OK: All pairs of coordinates are unique")

    def _match_doculects_to_files(self) -> None:
        """Checks that each doculect in list of doculects
        that is marked with '1' in 'has_feature_profile'
        actually has a feature profile.

        :raises DoculectInventoryValidatorError
        """
        for doculect in self.doculects:
            if (
                doculect["has_feature_profile"] == "1"
                and doculect["id"] not in self.names_of_feature_profiles
            ):
                raise DoculectInventoryValidatorError(
                    f'Doculect {doculect["id"]} has no file with feature profile.'
                )
        print(
            "OK: Every doculect that is marked as having a feature profile has a matching .csv file."
        )

    def _match_files_to_doculects(self) -> None:
        """Checks that each feature profile matches a line
        in the file with doculects and that line has '1'
        in 'has_feature_profile' field.

        :raises DoculectInventoryValidatorError
        """
        for name in self.names_of_feature_profiles:
            if name not in self.doculect_ids:
                raise DoculectInventoryValidatorError(
                    f"Feature profile {name} has no match in file with doculects."
                )
            if self.has_feature_profile_for_doculect_id[name] != "1":
                raise DoculectInventoryValidatorError(
                    f'Feature profile {name} is not marked with "1" in file with doculects.'
                )
        print(
            "OK: Every feature profile is marked correspondingly in file with doculects."
        )


if __name__ == "__main__":
    # When running the test suite, validation of real data will also be done.
    # It is not necessary to run the validator manually here if the tests were run.
    DoculectInventoryValidator().validate()
