import pytest

from langworld_db_data.adders.listed_value_adder import *
from langworld_db_data.filetools.csv_xls import read_csv
from langworld_db_data.filetools.txt import read_non_empty_lines_from_txt_file
from tests.paths import DIR_WITH_TEST_FILES

DIR_WITH_ADDERS_TEST_FILES = DIR_WITH_TEST_FILES / 'adders'
DIR_WITH_ADDERS_FEATURE_PROFILES = DIR_WITH_ADDERS_TEST_FILES / 'feature_profiles'
OUTPUT_DIR_WITH_ADDERS_FEATURE_PROFILES = DIR_WITH_ADDERS_FEATURE_PROFILES / 'output'
INPUT_FILE_WITH_LISTED_VALUES = DIR_WITH_ADDERS_TEST_FILES / 'features_listed_values.csv'

GS_FILE_WITH_LISTED_VALUES_AFTER_ADDITION = (
        DIR_WITH_ADDERS_TEST_FILES / 'features_listed_values_gold_standard_after_addition.csv'
)
GS_DIR_WITH_FEATURE_PROFILES_AFTER_ADDITION = OUTPUT_DIR_WITH_ADDERS_FEATURE_PROFILES / 'gold_standard'


@pytest.fixture(scope='function')
def test_adder():
    output_file = DIR_WITH_ADDERS_TEST_FILES / 'features_listed_values_output.csv'
    return ListedValueAdder(
        input_file_with_listed_values=INPUT_FILE_WITH_LISTED_VALUES,
        output_file_with_listed_values=output_file,
        input_dir_with_feature_profiles=DIR_WITH_ADDERS_FEATURE_PROFILES,
        output_dir_with_feature_profiles=OUTPUT_DIR_WITH_ADDERS_FEATURE_PROFILES,
    )


def test__add_to_inventory_of_listed_values_throws_exception_with_invalid_feature_id(test_adder):
    with pytest.raises(ListedValueAdderError) as e:
        test_adder.add_listed_value('X-1', 'Value', 'значение')

    assert 'Feature ID X-1 not found' in str(e)


def test__add_to_inventory_of_listed_values_throws_exception_with_existing_value(test_adder):
    for bad_args in [
        {'feature_id': 'A-3', 'new_value_en': 'Central and back', 'new_value_ru': 'Средний и задний'},
        {'feature_id': 'A-3', 'new_value_en': 'Some different value', 'new_value_ru': 'Средний и задний'},
        {'feature_id': 'A-3', 'new_value_en': 'Central and back', 'new_value_ru': 'Что-то новое'},
    ]:
        with pytest.raises(ListedValueAdderError) as e:
            test_adder.add_listed_value(**bad_args)
        assert 'already contains value you are trying to add' in str(e)


def test__add_to_inventory_of_listed_values_adds_good_value(test_adder):
    new_value_id = test_adder._add_to_inventory_of_listed_values(
        feature_id='A-11',
        new_value_en='New value, listed with a comma',
        new_value_ru='Первые, вторые и третьи',
    )
    assert new_value_id == 'A-11-15'

    assert test_adder.output_file_with_listed_values.exists()
    output_rows = read_csv(test_adder.output_file_with_listed_values, read_as='plain_rows')
    gold_standard_rows = read_csv(GS_FILE_WITH_LISTED_VALUES_AFTER_ADDITION, read_as='plain_rows')

    for output_row, gold_standard_row in zip(output_rows, gold_standard_rows):
        assert output_row == gold_standard_row

    test_adder.output_file_with_listed_values.unlink()


def test__mark_value_as_listed_in_feature_profiles(test_adder):
    test_adder._mark_value_as_listed_in_feature_profiles(
        feature_id='A-11',
        new_value_id='A-11-15',
        new_value_ru='Первые, вторые и третьи',
        custom_values_to_rename=[
            'Третьи, вторые и первые',
            'Первые, третьи и вторые'
        ]
    )

    for file in OUTPUT_DIR_WITH_ADDERS_FEATURE_PROFILES.glob('*.csv'):
        assert file.stem not in ('pashto', 'ukrainian'), f"File {file.name} is not supposed to be changed"

        print(f'TEST: checking amended feature profile {file.name}')
        gold_standard_file = GS_DIR_WITH_FEATURE_PROFILES_AFTER_ADDITION / file.name

        output_lines = read_non_empty_lines_from_txt_file(file)
        gold_standard_lines = read_non_empty_lines_from_txt_file(gold_standard_file)

        for output_line, gold_standard_line in zip(output_lines, gold_standard_lines):
            assert output_line == gold_standard_line, \
                f"File {file.name}: output line {output_line} does not match gold standard line {gold_standard_line}"

        file.unlink()


def test_add_listed_value_throws_exception_with_empty_args(test_adder):
    for bad_set_of_values in [
        {'feature_id': '', 'new_value_en': 'Value', 'new_value_ru': 'Значение'},
        {'feature_id': 'A-1', 'new_value_en': '', 'new_value_ru': 'Значение'},
        {'feature_id': 'A-1', 'new_value_en': 'Value', 'new_value_ru': ''},
    ]:
        with pytest.raises(ListedValueAdderError) as e:
            test_adder.add_listed_value(**bad_set_of_values)

        assert 'None of the passed strings can be empty' in str(e)


def test_add_listed_value(test_adder):
    test_adder.add_listed_value(
        feature_id='A-11',
        new_value_en='New value, listed with a comma',
        new_value_ru='Первые, вторые и третьи',
        custom_values_to_rename=[
            'Третьи, вторые и первые',
            'Первые, третьи и вторые'
        ]
    )

    assert test_adder.output_file_with_listed_values.exists()
    output_rows = read_csv(test_adder.output_file_with_listed_values, read_as='plain_rows')
    gold_standard_rows = read_csv(GS_FILE_WITH_LISTED_VALUES_AFTER_ADDITION, read_as='plain_rows')

    for output_row, gold_standard_row in zip(output_rows, gold_standard_rows):
        assert output_row == gold_standard_row

    test_adder.output_file_with_listed_values.unlink()

    for file in OUTPUT_DIR_WITH_ADDERS_FEATURE_PROFILES.glob('*.csv'):
        assert file.stem not in ('pashto', 'ukrainian'), f"File {file.name} is not supposed to be changed"

        print(f'TEST: checking amended feature profile {file.name}')
        gold_standard_file = GS_DIR_WITH_FEATURE_PROFILES_AFTER_ADDITION / file.name

        output_lines = read_non_empty_lines_from_txt_file(file)
        gold_standard_lines = read_non_empty_lines_from_txt_file(gold_standard_file)

        for output_line, gold_standard_line in zip(output_lines, gold_standard_lines):
            assert output_line == gold_standard_line, \
                f"File {file.name}: output line {output_line} does not match gold standard line {gold_standard_line}"

        file.unlink()
