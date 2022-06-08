import pytest

from langworld_db_data.writers.doculect_in_country_writer import *
from tests.helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard
from tests.paths import DIR_WITH_WRITERS_TEST_FILES

TEST_DIR_FOR_DOCULECT_IN_COUNTRY_WRITER = DIR_WITH_WRITERS_TEST_FILES / 'doculect_in_country_writer'

TEST_PROFILES_DIR = TEST_DIR_FOR_DOCULECT_IN_COUNTRY_WRITER / 'sociolinguistic_profiles'
TEST_COUNTRIES_FILE = TEST_DIR_FOR_DOCULECT_IN_COUNTRY_WRITER / 'countries.csv'
TEST_ALIASES_FILE = TEST_DIR_FOR_DOCULECT_IN_COUNTRY_WRITER / 'country_aliases_for_profile_parsing.csv'
TEST_DOCULECTS_FILE = TEST_DIR_FOR_DOCULECT_IN_COUNTRY_WRITER / 'doculects.csv'

TEST_OUTPUT_FILE = TEST_DIR_FOR_DOCULECT_IN_COUNTRY_WRITER / 'output.csv'


@pytest.fixture(scope='function')
def test_writer():
    return DoculectInCountryWriter(
        dir_with_sociolinguistic_profiles=TEST_PROFILES_DIR,
        file_with_countries=TEST_COUNTRIES_FILE,
        file_with_country_aliases=TEST_ALIASES_FILE,
        file_with_doculects=TEST_DOCULECTS_FILE,
        output_file=TEST_OUTPUT_FILE,
        verbose=True,
    )


def test__init__raises_exception_with_empty_profiles_dir():
    with pytest.raises(DoculectInCountryWriterError) as e:
        DoculectInCountryWriter(
            dir_with_sociolinguistic_profiles=TEST_DIR_FOR_DOCULECT_IN_COUNTRY_WRITER / 'dir_with_no_profiles',
            file_with_countries=TEST_COUNTRIES_FILE,
            file_with_country_aliases=TEST_ALIASES_FILE,
            file_with_doculects=TEST_DOCULECTS_FILE,
            output_file=TEST_OUTPUT_FILE,
            verbose=True,
        )
    assert 'No sociolinguistic profiles found' in str(e)


def test__add_aliases(test_writer):
    test_writer._add_aliases()


def test_write(test_writer):
    test_writer.write()

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=TEST_OUTPUT_FILE,
        gold_standard_file=TEST_DIR_FOR_DOCULECT_IN_COUNTRY_WRITER / 'output_benchmark.csv',
    )
