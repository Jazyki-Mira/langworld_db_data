from typing import NamedTuple

import pytest

from langworld_db_data.filetools.csv_xls import *
from langworld_db_data.filetools.txt import read_plain_text_from_file
from tests.paths import *


def test_convert_xls_to_csv():
    path_to_excel_file = DIR_WITH_FILETOOLS_TEST_FILES / 'feature_profile_belarusian.xlsx'
    path_to_output_csv_file = DIR_WITH_FILETOOLS_TEST_FILES / 'test_convert_excel_to_csv.csv'
    path_to_gold_standard_csv_file = DIR_WITH_FILETOOLS_TEST_FILES / 'test_convert_excel_to_csv_gold_standard.csv'

    if path_to_output_csv_file.exists():
        path_to_output_csv_file.unlink()

    convert_xls_to_csv(
        path_to_input_excel_file=path_to_excel_file,
        sheet_name='Лист1',
        path_to_output_csv_file=path_to_output_csv_file,
    )

    assert path_to_output_csv_file.exists()

    with path_to_output_csv_file.open(mode='r', encoding='utf-8') as fh:
        output_content = fh.read()

    with path_to_gold_standard_csv_file.open(mode='r', encoding='utf-8') as fh:
        gold_standard = fh.read()

    assert output_content == gold_standard
    path_to_output_csv_file.unlink()


def test_read_csv():
    lines_to_write = ['col1,col2,col3\n', 'foo,bar,baz\n', 'фу,бар,баз']
    expected_rows = [['col1', 'col2', 'col3'], ['foo', 'bar', 'baz'], ['фу', 'бар', 'баз']]
    expected_list_of_dicts = [
        {'col1': 'foo', 'col2': 'bar', 'col3': 'baz'},
        {'col1': 'фу', 'col2': 'бар', 'col3': 'баз'},
    ]

    path_to_auto_test_file = Path('test_csv.csv')

    with path_to_auto_test_file.open(mode='w+', encoding='utf-8') as fh:
        fh.writelines(lines_to_write)

    path_to_manual_file_from_excel = DIR_WITH_FILETOOLS_TEST_FILES / 'csv_manually_created_in_excel.csv'

    for path_ in (path_to_auto_test_file, path_to_manual_file_from_excel):

        delimiter: CSVDelimiter = ','
        if 'excel' in path_.name:
            delimiter = ';'

        rows = read_csv(path_, read_as='plain_rows', delimiter=delimiter)
        assert rows == expected_rows

        rows_without_header = read_csv(path_, read_as='plain_rows_no_header', delimiter=delimiter)
        assert rows_without_header == expected_rows[1:]

        list_of_dicts = read_csv(path_, read_as='dicts', delimiter=delimiter)
        assert list_of_dicts == expected_list_of_dicts

    path_to_auto_test_file.unlink()


def test_check_csv_passes_for_good_file():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'doculects_output_gold_standard.csv'
    check_csv_for_malformed_rows(file)


def test_check_csv_throws_exception_for_malformed_rows():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'csv_doculects_with_incomplete_rows.csv'
    with pytest.raises(IndexError) as e:
        check_csv_for_malformed_rows(file)
    assert 'Following rows have abnormal number of columns: 3, 5' in str(e)


def test_read_csv_raises_exception_with_wrong_read_as():
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        read_csv(Path(DIR_WITH_FILETOOLS_TEST_FILES / 'csv_manually_created_in_excel.csv'), read_as='foo')


def test_read_dict_from_2_csv_columns():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'read_dict_from_2_csv_columns.csv'

    dict1 = read_dict_from_2_csv_columns(file, 'col3', 'col1')
    assert len(dict1) == 3
    assert dict1['baz1'] == 'foo1'
    assert dict1['baz3'] == 'foo3'

    dict2 = read_dict_from_2_csv_columns(file, 'col1', 'col2')
    assert len(dict2) == 3
    assert dict2['foo1'] == 'bar1'
    assert dict2['foo2'] == 'bar2!'
    assert dict2['foo3'] == 'bar2!'

    with pytest.raises(ValueError) as e:
        read_dict_from_2_csv_columns(file, 'col2', 'col2')
    assert 'same name for both key and value' in str(e.value)

    with pytest.raises(ValueError) as e:
        read_dict_from_2_csv_columns(file, 'col2', 'col3')
    assert 'are not unique' in str(e.value)

    with pytest.raises(KeyError) as e:
        read_dict_from_2_csv_columns(file, 'col5!!', 'col3')
    assert 'not found in' in str(e.value)

    with pytest.raises(ValueError) as e:
        read_dict_from_2_csv_columns(file, 'col4!', 'col2')
    assert 'more than once' in str(e.value)


def test_write_csv_throws_exception_when_file_exists_and_overwrite_is_false():
    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode='w+', encoding='utf-8') as fh:
        fh.write('')

    with pytest.raises(FileExistsError):
        write_csv(['foo'], PATH_TO_TEST_OUTPUT_TXT_FILE, False, ',')

    PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_write_csv_throws_exception_when_rows_are_of_different_types():
    rows = [['foo', 'bar'], {'bar': 'baz'}]
    with pytest.raises(TypeError) as e:
        write_csv(rows, PATH_TO_TEST_OUTPUT_CSV_FILE, overwrite=False, delimiter=',')

    print('TEST: exception raised:', e)


def test_write_csv_throws_exception_when_rows_are_of_wrong_type():
    rows = [1, 2]
    with pytest.raises(TypeError) as e:
        write_csv(rows, PATH_TO_TEST_OUTPUT_CSV_FILE, overwrite=False, delimiter=',')

    print('TEST: exception raised:', e)


class SomeNamedTuple(NamedTuple):
    foo1: str
    foo2: str


@pytest.mark.parametrize(
    'rows, expected_file_content',
    [
        (
            [['foo', 'bar'], ['bar', 'baz']],
            'foo,bar\nbar,baz\n'
        ),
        (
            [{'foo1': 'bar1.1', 'foo2': 'bar2.1'}, {'foo1': 'b1.2', 'foo2': 'b2.2'}, {'foo1': 'b1.3', 'foo2': 'b2.3'}],
            'foo1,foo2\nbar1.1,bar2.1\nb1.2,b2.2\nb1.3,b2.3\n'
        ),
        (
            [SomeNamedTuple(foo1='bar1', foo2='bar2'), SomeNamedTuple(foo2='bar2.2', foo1='bar1.2')],
            'foo1,foo2\nbar1,bar2\nbar1.2,bar2.2\n'
        ),
    ]
)
def test_write_csv(rows, expected_file_content):
    if PATH_TO_TEST_OUTPUT_CSV_FILE.exists():
        PATH_TO_TEST_OUTPUT_CSV_FILE.unlink()

    write_csv(rows, PATH_TO_TEST_OUTPUT_CSV_FILE, overwrite=False, delimiter=',')
    assert PATH_TO_TEST_OUTPUT_CSV_FILE.exists()

    content = read_plain_text_from_file(PATH_TO_TEST_OUTPUT_CSV_FILE)
    assert content == expected_file_content

    PATH_TO_TEST_OUTPUT_CSV_FILE.unlink()
