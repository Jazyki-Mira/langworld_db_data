import pytest

from langworld_db_data.featureprofiletools.feature_profile_writer_from_dictionary import *
from langworld_db_data.filetools.csv_xls import read_csv
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES


@pytest.fixture(scope='function')
def test_writer():
    return FeatureProfileWriterFromDictionary()


def test_write(test_writer):
    output_file = DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / 'catalan_short_writer_output.csv'
    benchmark_file = DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / 'catalan_short_benchmark_for_writer.csv'

    test_writer.write(
        feature_dict={
            'A-1': ValueForFeatureProfileDictionary(
                feature_name_ru='Количество степеней подъема',
                value_type='listed',
                value_id='A-1-2',
                value_ru='Три',
                comment_ru='',
                comment_en='',
            ),
            'A-2': ValueForFeatureProfileDictionary(
                feature_name_ru='Подъемы гласных',
                value_type='custom',
                value_id='',
                value_ru='Верхний, средний (закрытые и открытые) и нижний',
                comment_ru='',
                comment_en='',
            ),
            'A-3': ValueForFeatureProfileDictionary(
                feature_name_ru='Ряды гласных',
                value_type='listed',
                value_id='A-3-4',
                value_ru='Передний, средний и задний',
                comment_ru='',
                comment_en='',
            ),
            '_aux': ValueForFeatureProfileDictionary(
                feature_name_ru='',
                value_type='not_applicable',
                value_id='',
                value_ru='',
                comment_ru='И.И.Иванов',
                comment_en='',
            ),
        },
        output_path=output_file,
    )

    assert output_file.exists()

    output_lines = read_csv(output_file, read_as='plain_rows')
    benchmark_lines = read_csv(benchmark_file, read_as='plain_rows')

    for output_line, benchmark_line in zip(output_lines, benchmark_lines):
        assert output_line == benchmark_line

    output_file.unlink()
