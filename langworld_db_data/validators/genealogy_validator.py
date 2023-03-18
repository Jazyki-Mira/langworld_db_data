import re
from collections import Counter
from pathlib import Path

from langworld_db_data.constants.paths import (
    FILE_WITH_GENEALOGY_HIERARCHY,
    FILE_WITH_GENEALOGY_NAMES,
)
from langworld_db_data.filetools.csv_xls import (
    check_csv_for_malformed_rows,
    check_csv_for_repetitions_in_column,
)
from langworld_db_data.filetools.json_toml_yaml import check_yaml_file
from langworld_db_data.filetools.txt import read_non_empty_lines_from_txt_file
from langworld_db_data.validators.validator import Validator, ValidatorError


class GenealogyValidatorError(ValidatorError):
    pass


class GenealogyValidator(Validator):
    def __init__(
        self,
        file_with_hierarchy: Path = FILE_WITH_GENEALOGY_HIERARCHY,
        file_with_names: Path = FILE_WITH_GENEALOGY_NAMES,
    ):
        self.file_with_hierarchy = file_with_hierarchy
        self.file_with_names = file_with_names

        self.family_ids_from_file_with_names = self._read_ids(self.file_with_names)

    def validate(self) -> None:
        print("\nChecking genealogy")

        check_yaml_file(self.file_with_hierarchy, verbose=False)

        check_csv_for_malformed_rows(self.file_with_names)
        check_csv_for_repetitions_in_column(self.file_with_names, "id")

        family_ids_from_hierarchy = self._check_and_get_ids_from_hierarchy()
        self._check_ids_in_list_of_names(family_ids_from_hierarchy)

    def _check_and_get_ids_from_hierarchy(self) -> list[str]:
        """
        Checks if IDs in hierarchy are formed correctly and unique,
        and match IDs of families in file with names.

        Returns list of family IDs extracted from hierarchy.

        :raises GenealogyValidatorError
        """

        lines = read_non_empty_lines_from_txt_file(self.file_with_hierarchy)
        pattern = re.compile(r"^-\s*(?P<id>[a-z_]+):?$")

        family_ids = []

        for line in lines:
            if line.strip() == "---":
                continue

            match = pattern.match(line)
            if not match:
                raise GenealogyValidatorError(
                    f"Family ID in line {line} is incorrectly formed. "
                    "It can only contain lowercase letters and underscores"
                )

            family_id = match.group("id")

            if family_id not in self.family_ids_from_file_with_names:
                raise GenealogyValidatorError(
                    f"Family ID {family_id} in hierarchy not found in file with names"
                    " of families"
                )

            family_ids.append(family_id)

        print(
            "OK: All family IDs in the hierarchy are formed correctly and match IDs in"
            " list of families"
        )

        counter = Counter(family_ids)

        for key in counter:
            if counter[key] > 1:
                raise GenealogyValidatorError(
                    f"Family ID {key} was seen {counter[key]} times in the genealogy"
                    " hierarchy. It must be unique."
                )
        print("OK: All family IDs in genealogy hierarchy are unique")

        return family_ids

    def _check_ids_in_list_of_names(self, ids_from_hierarchy: list[str]) -> None:
        """
        Checks if IDs in file with names of families are formed correctly and
        match IDs of families in hierarchy file.

        :raises GenealogyValidatorError
        """

        pattern = re.compile(r"[a-z_]+")

        for family_id in self.family_ids_from_file_with_names:
            if not pattern.match(family_id):
                raise GenealogyValidatorError(
                    f"File with names of families: invalid ID {family_id} (only use"
                    " lowercase letters and underscore)"
                )

            if family_id not in ids_from_hierarchy:
                raise GenealogyValidatorError(
                    f"File with names of families: ID {family_id} not found in file"
                    " with genealogy hierarchy"
                )

        print(
            "OK: All family IDs in file with names of families are formed correctly "
            "and match IDs in the hierarchy"
        )


if __name__ == "__main__":
    GenealogyValidator().validate()
