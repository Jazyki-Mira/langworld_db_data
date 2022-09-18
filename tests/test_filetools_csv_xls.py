from pathlib import Path
from typing import NamedTuple

import pytest

# noinspection PyProtectedMember
from langworld_db_data.filetools.csv_xls import (CSVDelimiter, check_csv_for_malformed_rows,
                                                 append_empty_column_to_csv, check_csv_for_repetitions_in_column,
                                                 convert_xls_to_csv, read_column_from_csv, read_dicts_from_csv,
                                                 read_plain_rows_from_csv, read_dict_from_2_csv_columns,
                                                 read_dicts_from_xls, write_csv)
from langworld_db_data.filetools.txt import read_plain_text_from_file
from tests.paths import DIR_WITH_FILETOOLS_TEST_FILES, PATH_TO_TEST_OUTPUT_TXT_FILE, PATH_TO_TEST_OUTPUT_CSV_FILE
from tests.test_helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard


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

    with path_to_output_csv_file.open(encoding='utf-8') as fh:
        output_content = fh.read()

    with path_to_gold_standard_csv_file.open(encoding='utf-8') as fh:
        gold_standard = fh.read()

    assert output_content == gold_standard
    path_to_output_csv_file.unlink()


def test_read_dicts_from_csv_read_plain_rows_from_csv():
    lines_to_write = ['col1,col2,col3\n', 'foo,bar,baz\n', 'фу,бар,баз']
    expected_rows = [['col1', 'col2', 'col3'], ['foo', 'bar', 'baz'], ['фу', 'бар', 'баз']]
    expected_list_of_dicts = [
        {
            'col1': 'foo',
            'col2': 'bar',
            'col3': 'baz'
        },
        {
            'col1': 'фу',
            'col2': 'бар',
            'col3': 'баз'
        },
    ]

    path_to_auto_test_file = Path('test_csv.csv')

    with path_to_auto_test_file.open(mode='w+', encoding='utf-8') as fh:
        fh.writelines(lines_to_write)

    path_to_manual_file_from_excel = DIR_WITH_FILETOOLS_TEST_FILES / 'csv_manually_created_in_excel.csv'

    for path_ in (path_to_auto_test_file, path_to_manual_file_from_excel):

        delimiter: CSVDelimiter = ','
        if 'excel' in path_.name:
            delimiter = ';'

        rows = read_plain_rows_from_csv(path_, delimiter=delimiter)
        assert rows == expected_rows

        rows_without_header = read_plain_rows_from_csv(path_, delimiter=delimiter, remove_1st_row=True)
        assert rows_without_header == expected_rows[1:]

        list_of_dicts = read_dicts_from_csv(path_, delimiter=delimiter)
        assert list_of_dicts == expected_list_of_dicts

    path_to_auto_test_file.unlink()


def test_read_column_from_csv():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'doculects_output_gold_standard.csv'
    values = read_column_from_csv(file, 'id')
    assert len(values) == 408
    assert values[0] == 'aragonese'
    assert values[-1] == 'yukaghir'


def test_read_column_from_csv_raises_key_error():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'doculects_output_gold_standard.csv'
    with pytest.raises(KeyError):
        read_column_from_csv(file, 'foo')


def test_check_csv_for_malformed_rows_passes_for_good_file():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'doculects_output_gold_standard.csv'
    check_csv_for_malformed_rows(file)


def test_check_csv_for_malformed_rows_throws_exception_for_malformed_rows():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'csv_doculects_with_incomplete_rows.csv'
    with pytest.raises(IndexError) as e:
        check_csv_for_malformed_rows(file)
    assert 'Following rows have abnormal number of columns: 3, 5' in str(e)


def test_check_csv_for_repetitions_in_column_passes_for_good_file():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'doculects_output_gold_standard.csv'
    check_csv_for_repetitions_in_column(path_to_file=file, column_name='id')


def test_check_csv_for_repetitions_in_column_throws_exception_with_wrong_column_name():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'doculects_output_gold_standard.csv'
    with pytest.raises(KeyError) as e:
        check_csv_for_repetitions_in_column(path_to_file=file, column_name='foo')
    assert 'column <foo> because it does not exist' in str(e)


def test_check_csv_for_repetitions_in_column_throws_exception_with_repetition_in_column():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'csv_doculects_with_duplicate_values.csv'
    with pytest.raises(ValueError) as e:
        check_csv_for_repetitions_in_column(path_to_file=file, column_name='id')
    assert 'repeating values in column <id>: asturian, catalan' in str(e)


def test_check_csv_for_repetitions_in_column_passes_for_file_with_repetition_in_column_if_different_column_is_checked():
    file = DIR_WITH_FILETOOLS_TEST_FILES / 'csv_doculects_with_duplicate_values.csv'
    check_csv_for_repetitions_in_column(path_to_file=file, column_name='name_ru')


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


def test_read_dicts_from_xls_reads_good_file():
    dicts = read_dicts_from_xls(DIR_WITH_FILETOOLS_TEST_FILES / 'feature_profile_belarusian.xlsx', 'Лист1')

    dicts_from_gold_standard_csv = read_dicts_from_csv(
        DIR_WITH_FILETOOLS_TEST_FILES / 'test_convert_excel_to_csv_gold_standard.csv'
    )

    for xls_row, csv_row in zip(dicts, dicts_from_gold_standard_csv):
        assert xls_row == csv_row


def test_read_dicts_from_xls_raises_exception_with_bad_sheet_name():
    with pytest.raises(KeyError):
        read_dicts_from_xls(DIR_WITH_FILETOOLS_TEST_FILES / 'feature_profile_belarusian.xlsx', 'foo')


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


@pytest.mark.parametrize('rows, expected_file_content', [
    ([['foo', 'bar'], ['bar', 'baz']], 'foo,bar\nbar,baz\n'),
    ([{
        'foo1': 'bar1.1',
        'foo2': 'bar2.1'
    }, {
        'foo1': 'b1.2',
        'foo2': 'b2.2'
    }, {
        'foo1': 'b1.3',
        'foo2': 'b2.3'
    }], 'foo1,foo2\nbar1.1,bar2.1\nb1.2,b2.2\nb1.3,b2.3\n'),
    ([SomeNamedTuple(foo1='bar1', foo2='bar2'),
      SomeNamedTuple(foo2='bar2.2', foo1='bar1.2')], 'foo1,foo2\nbar1,bar2\nbar1.2,bar2.2\n'),
])
def test_write_csv(rows, expected_file_content):
    if PATH_TO_TEST_OUTPUT_CSV_FILE.exists():
        PATH_TO_TEST_OUTPUT_CSV_FILE.unlink()

    write_csv(rows, PATH_TO_TEST_OUTPUT_CSV_FILE, overwrite=False, delimiter=',')
    assert PATH_TO_TEST_OUTPUT_CSV_FILE.exists()

    content = read_plain_text_from_file(PATH_TO_TEST_OUTPUT_CSV_FILE)
    assert content == expected_file_content

    PATH_TO_TEST_OUTPUT_CSV_FILE.unlink()


def test_append_empty_column_to_csv_adds_new_column():
    input_file = DIR_WITH_FILETOOLS_TEST_FILES / 'doculects_output_gold_standard.csv'
    output_file = DIR_WITH_FILETOOLS_TEST_FILES / 'append_empty_column_doculects_output.csv'
    gold_standard_file_after_append = DIR_WITH_FILETOOLS_TEST_FILES / 'append_empty_column_doculects_gold_standard.csv'

    append_empty_column_to_csv(
        path_to_file=input_file, name_of_new_column='new_column', custom_path_to_output_file=output_file)
    check_existence_of_output_csv_file_and_compare_with_gold_standard(output_file, gold_standard_file_after_append)


def test_append_empty_column_to_csv_raises_exception_with_existing_custom_output_file():
    input_file = DIR_WITH_FILETOOLS_TEST_FILES / 'doculects_output_gold_standard.csv'
    existing_file = DIR_WITH_FILETOOLS_TEST_FILES / 'append_empty_column_doculects_gold_standard.csv'
    with pytest.raises(FileExistsError):
        append_empty_column_to_csv(
            path_to_file=input_file, custom_path_to_output_file=existing_file, name_of_new_column='foo')


def test_append_empty_column_to_csv_raises_exception_with_existing_column():
    input_file = DIR_WITH_FILETOOLS_TEST_FILES / 'doculects_output_gold_standard.csv'
    output_file = DIR_WITH_FILETOOLS_TEST_FILES / 'append_empty_column_doculects_output.csv'
    with pytest.raises(ValueError):
        append_empty_column_to_csv(
            path_to_file=input_file, custom_path_to_output_file=output_file, name_of_new_column='type')

    assert not output_file.exists()
