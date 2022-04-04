from pathlib import Path

from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR, FILE_WITH_DOCULECTS
from langworld_db_data.filetools.csv_xls import read_csv
from langworld_db_data.validators.exceptions import ValidatorError


class DoculectListValidatorError(ValidatorError):
    pass


class DoculectListValidator:
    def __init__(
            self,
            dir_with_feature_profiles: Path = FEATURE_PROFILES_DIR,
            file_with_doculects: Path = FILE_WITH_DOCULECTS,
    ):
        self.feature_profiles: list[Path] = sorted(list(dir_with_feature_profiles.glob('*.csv')))
        self.names_of_feature_profiles: set[str] = {
            f.stem for f in self.feature_profiles
        }

        self.doculects: list[dict] = read_csv(file_with_doculects, read_as='dicts')
        self.doculect_ids = {d['id'] for d in self.doculects}

        if len(self.doculect_ids) != len(self.doculects):
            raise DoculectListValidatorError(f'Some IDs in list of doculects are not unique')

        self.has_feature_profile_for_doculect_id = {
            d['id']: d['has_feature_profile'] for d in self.doculects
        }

    def validate(self):
        print('\nValidating doculects')
        self._match_doculects_to_files()
        self._match_files_to_doculects()

    def _match_doculects_to_files(self):
        """Checks that each doculect in list of doculects
        that is marked with '1' in 'has_feature_profile'
        actually has a feature profile.
        """
        for doculect in self.doculects:
            if doculect['has_feature_profile'] == '1' and  doculect['id'] not in self.names_of_feature_profiles:
                raise ValidatorError(f'Doculect {doculect["id"]} has no file with feature profile.')
        else:
            print(f'OK: Every doculect that is marked as having a feature profile has a matching .csv file.')

    def _match_files_to_doculects(self):
        """Checks that each feature profile matches a line
        in the file with doculects and that line has '1'
        in 'has_feature_profile' field.
        """
        for name in self.names_of_feature_profiles:
            if name not in self.doculect_ids:
                raise DoculectListValidatorError(
                    f'Feature profile {name} has no match in file with doculects.'
                )
            if self.has_feature_profile_for_doculect_id[name] != '1':
                raise DoculectListValidatorError(
                    f'Feature profile {name} is not marked with "1" in file with doculects.'
                )
        else:
            print(f'OK: Every feature profile is marked correspondingly in file with doculects.')


if __name__ == '__main__':
    dlv = DoculectListValidator()
    dlv.validate()
