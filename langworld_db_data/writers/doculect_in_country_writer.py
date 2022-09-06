from pathlib import Path

from langworld_db_data.constants.iterables import LOCALES
from langworld_db_data.constants.paths import (
    FILE_WITH_COUNTRIES,
    FILE_WITH_COUNTRY_ALIASES,
    FILE_WITH_DOCULECTS,
    FILE_WITH_DOCULECTS_MATCHED_TO_COUNTRIES,
    SOCIOLINGUISTIC_PROFILES_DIR,
)
from langworld_db_data.filetools.csv_xls import read_csv, write_csv
from langworld_db_data.filetools.json_toml_yaml import read_json_toml_yaml


class DoculectInCountryWriterError(Exception):
    pass


class DoculectInCountryWriter:
    """Class for writing a CSV file that matches doculects
    to countries where they are present.

    The data are taken from file with doculects (main country)
    and sociolinguistic profiles.
    """

    NOTES_TO_DELETE = (
        'госуд., ист.',
        "госуд.",
        "ист.",
        'state',
        'state language',
        'госуд.,ист.',
        'hist.',
        'state, hist.',
        'я.п.м.',
        'official',
        "Côte d'Ivoire",
        'государственный',
        "modern Syria",
        "совр. Турция",
        "modern-day Iraq",
        "present-day Afghanistan and Tajikistan",
        "modern Turkey",
        "Levant",
        "Asia Minor",
        "Левант",
        "совр. Сирия",
        "Kingdom of Van",
        # this is one long string, missing comma after 1st line is intended:
        "present-day France, Luxembourg, Belgium, most of Switzerland, "
        "and parts of Northern Italy, Netherlands, and Germany",
    )

    def __init__(self,
                 dir_with_sociolinguistic_profiles: Path = SOCIOLINGUISTIC_PROFILES_DIR,
                 file_with_countries: Path = FILE_WITH_COUNTRIES,
                 file_with_country_aliases: Path = FILE_WITH_COUNTRY_ALIASES,
                 file_with_doculects: Path = FILE_WITH_DOCULECTS,
                 output_file: Path = FILE_WITH_DOCULECTS_MATCHED_TO_COUNTRIES,
                 verbose: bool = False):
        self.output_file = output_file
        self.verbose = verbose

        doculect_rows: list[dict[str, str]] = read_csv(file_with_doculects, read_as='dicts')
        self.doculect_ids = [row['id'] for row in doculect_rows]

        self.doculect_id_to_locale_to_file = {}

        for doculect_id in self.doculect_ids:
            for locale in LOCALES:
                file = dir_with_sociolinguistic_profiles / f'{doculect_id}_{locale}.yaml'
                if file.exists():
                    self.doculect_id_to_locale_to_file[(doculect_id, locale)] = file

        self.sociolinguistic_profiles = sorted(list(dir_with_sociolinguistic_profiles.glob('*.yaml')))

        if not self.sociolinguistic_profiles:
            raise DoculectInCountryWriterError(
                f'No sociolinguistic profiles found in {dir_with_sociolinguistic_profiles}')

        # this is the initial version that will have to be amended by reading the file with aliases
        self.doculect_id_to_countries: dict[str, set[str]] = {
            row['id']: {row['main_country_id']} for row in doculect_rows
        }

        if self.verbose:
            print("Doculect ID to countries:", self.doculect_id_to_countries)

        self.country_name_and_locale_to_country_id = {}

        rows_with_countries: list[dict[str, str]] = read_csv(file_with_countries, read_as='dicts')
        for row in rows_with_countries:
            for locale in LOCALES:
                # (row[locale], locale) gives a dictionary key like (Russia, en):
                self.country_name_and_locale_to_country_id[(row[locale], locale)] = row['id']

        rows_with_country_aliases: list[dict[str, str]] = read_csv(file_with_country_aliases, read_as='dicts')
        for row in rows_with_country_aliases:
            tuple_key = (row['alias'], row['locale'])
            if tuple_key not in self.country_name_and_locale_to_country_id:
                self.country_name_and_locale_to_country_id[tuple_key] = row['country_id']

        if self.verbose:
            print('Country name and locale to country ID:', self.country_name_and_locale_to_country_id)

    def write(self, overwrite: bool = True) -> None:
        self._add_aliases()

        rows_to_write = []
        for doculect_id in self.doculect_id_to_countries:
            for country_id in self.doculect_id_to_countries[doculect_id]:
                rows_to_write.append((doculect_id, country_id))

        write_csv(
            # Need sorting because otherwise the set will be written differently each time.
            # `str(item)` will have effect equivalent to sorting by two items doculect ID and then by country ID
            [('doculect_id', 'country_id')] + sorted(rows_to_write, key=lambda tuple_: str(tuple_)),
            path_to_file=self.output_file,
            overwrite=overwrite,
            delimiter=',')

    def _add_aliases(self) -> None:
        """Adds entries with country aliases to the dictionary
        that matches country names and locales to country IDs.
        Initially this dictionary only consists of
        countries listed in file with doculects.
        """

        unrecognized_countries = set()

        for doculect_id_and_locale, file in self.doculect_id_to_locale_to_file.items():
            doculect_id, locale = doculect_id_and_locale
            country_section = read_json_toml_yaml(file)['1.1.3']

            for item in country_section:
                if isinstance(item, str):
                    clean_item = self.cleans_item(item)
                elif isinstance(item, dict):
                    clean_item = self.cleans_item(list(item.keys())[0])
                else:
                    raise TypeError

                if clean_item in ('число говорящих', 'number of speakers', 'NUMBER OF SPEAKERS'):
                    continue

                try:
                    self.doculect_id_to_countries[doculect_id].add(
                        self.country_name_and_locale_to_country_id[(clean_item, locale)])
                except KeyError:
                    unrecognized_countries.add(clean_item)

        if self.verbose:
            print("Doculect ID to countries:", self.doculect_id_to_countries)
            print("Unrecognized countries:\n", "\n".join(sorted(list(unrecognized_countries))))

    def cleans_item(self, str_: str) -> str:
        clean_str = str_
        for note in self.NOTES_TO_DELETE:
            clean_str = clean_str.replace(f'({note})', '')

        return clean_str.strip()


if __name__ == '__main__':
    pass
