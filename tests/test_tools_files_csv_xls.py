from pathlib import Path
from typing import NamedTuple

import pytest

# noinspection PyProtectedMember
from langworld_db_data.tools.files.csv_xls import (
    CSVDelimiter,
    append_empty_column_to_csv,
    check_csv_for_malformed_rows,
    check_csv_for_repetitions_in_column,
    convert_xls_to_csv,
    read_column_from_csv,
    read_dict_from_2_csv_columns,
    read_dicts_from_csv,
    read_dicts_from_xls,
    read_plain_rows_from_csv,
    remove_matching_rows,
    remove_multiple_matching_rows,
    remove_one_matching_row,
    write_csv,
)
from langworld_db_data.tools.files.txt import read_plain_text_from_file
from tests.paths import (
    DIR_WITH_FILETOOLS_TEST_FILES,
    PATH_TO_TEST_OUTPUT_CSV_FILE,
    PATH_TO_TEST_OUTPUT_TXT_FILE,
)
from tests.test_helpers import check_existence_of_output_csv_file_and_compare_with_gold_standard


def test_convert_xls_to_csv():
    path_to_excel_file = DIR_WITH_FILETOOLS_TEST_FILES / "feature_profile_belarusian.xlsx"
    path_to_output_csv_file = DIR_WITH_FILETOOLS_TEST_FILES / "test_convert_excel_to_csv.csv"
    path_to_gold_standard_csv_file = (
        DIR_WITH_FILETOOLS_TEST_FILES / "test_convert_excel_to_csv_gold_standard.csv"
    )

    if path_to_output_csv_file.exists():
        path_to_output_csv_file.unlink()

    convert_xls_to_csv(
        path_to_input_excel_file=path_to_excel_file,
        sheet_name="Лист1",
        path_to_output_csv_file=path_to_output_csv_file,
    )

    assert path_to_output_csv_file.exists()

    with path_to_output_csv_file.open(encoding="utf-8") as fh:
        output_content = fh.read()

    with path_to_gold_standard_csv_file.open(encoding="utf-8") as fh:
        gold_standard = fh.read()

    assert output_content == gold_standard
    path_to_output_csv_file.unlink()


def test_read_dicts_from_csv_read_plain_rows_from_csv():
    lines_to_write = ["col1,col2,col3\n", "foo,bar,baz\n", "фу,бар,баз"]
    expected_rows = [
        ["col1", "col2", "col3"],
        ["foo", "bar", "baz"],
        ["фу", "бар", "баз"],
    ]
    expected_list_of_dicts = [
        {"col1": "foo", "col2": "bar", "col3": "baz"},
        {"col1": "фу", "col2": "бар", "col3": "баз"},
    ]

    path_to_auto_test_file = Path("test_csv.csv")

    with path_to_auto_test_file.open(mode="w+", encoding="utf-8") as fh:
        fh.writelines(lines_to_write)

    path_to_manual_file_from_excel = (
        DIR_WITH_FILETOOLS_TEST_FILES / "csv_manually_created_in_excel.csv"
    )

    for path_ in (path_to_auto_test_file, path_to_manual_file_from_excel):
        delimiter: CSVDelimiter = ","
        if "excel" in path_.name:
            delimiter = ";"

        rows = read_plain_rows_from_csv(path_, delimiter=delimiter)
        assert rows == expected_rows

        rows_without_header = read_plain_rows_from_csv(
            path_, delimiter=delimiter, remove_1st_row=True
        )
        assert rows_without_header == expected_rows[1:]

        list_of_dicts = read_dicts_from_csv(path_, delimiter=delimiter)
        assert list_of_dicts == expected_list_of_dicts

    path_to_auto_test_file.unlink()


def test_read_column_from_csv():
    file = DIR_WITH_FILETOOLS_TEST_FILES / "doculects_output_gold_standard.csv"
    values = read_column_from_csv(file, "id")
    assert len(values) == 408
    assert values[0] == "aragonese"
    assert values[-1] == "yukaghir"


def test_read_column_from_csv_raises_key_error():
    file = DIR_WITH_FILETOOLS_TEST_FILES / "doculects_output_gold_standard.csv"
    with pytest.raises(KeyError):
        read_column_from_csv(file, "foo")


def test_check_csv_for_malformed_rows_passes_for_good_file():
    file = DIR_WITH_FILETOOLS_TEST_FILES / "doculects_output_gold_standard.csv"
    check_csv_for_malformed_rows(file)


def test_check_csv_for_malformed_rows_throws_exception_for_malformed_rows():
    file = DIR_WITH_FILETOOLS_TEST_FILES / "csv_doculects_with_incomplete_rows.csv"
    with pytest.raises(IndexError, match="Following rows have abnormal number of columns: 3, 5"):
        check_csv_for_malformed_rows(file)


def test_check_csv_for_repetitions_in_column_passes_for_good_file():
    file = DIR_WITH_FILETOOLS_TEST_FILES / "doculects_output_gold_standard.csv"
    check_csv_for_repetitions_in_column(path_to_file=file, column_name="id")


def test_check_csv_for_repetitions_in_column_throws_exception_with_wrong_column_name():
    file = DIR_WITH_FILETOOLS_TEST_FILES / "doculects_output_gold_standard.csv"
    with pytest.raises(KeyError, match="column <foo> because it does not exist"):
        check_csv_for_repetitions_in_column(path_to_file=file, column_name="foo")


def test_check_csv_for_repetitions_in_column_throws_error_with_repetition_in_column():
    file = DIR_WITH_FILETOOLS_TEST_FILES / "csv_doculects_with_duplicate_values.csv"
    with pytest.raises(ValueError, match="repeating values in column <id>: asturian, catalan"):
        check_csv_for_repetitions_in_column(path_to_file=file, column_name="id")


def test_check_csv_for_repetitions_in_column_passes_for_file_with_repetition_in_column_if_different_column_is_checked():  # noqa E501
    file = DIR_WITH_FILETOOLS_TEST_FILES / "csv_doculects_with_duplicate_values.csv"
    check_csv_for_repetitions_in_column(path_to_file=file, column_name="name_ru")


def test_read_dict_from_2_csv_columns():
    file = DIR_WITH_FILETOOLS_TEST_FILES / "read_dict_from_2_csv_columns.csv"

    dict1 = read_dict_from_2_csv_columns(file, "col3", "col1")
    assert len(dict1) == 3
    assert dict1["baz1"] == "foo1"
    assert dict1["baz3"] == "foo3"

    dict2 = read_dict_from_2_csv_columns(file, "col1", "col2")
    assert len(dict2) == 3
    assert dict2["foo1"] == "bar1"
    assert dict2["foo2"] == "bar2!"
    assert dict2["foo3"] == "bar2!"


@pytest.mark.parametrize(
    "key_col, val_col, exception_type, error_message",
    [
        ("col2", "col2", ValueError, "same name for both key and value"),
        ("col2", "col3", ValueError, "are not unique"),
        ("col5!!", "col3", KeyError, "not found in"),
        ("col4!", "col2", ValueError, "more than once"),
    ],
)
def test_read_dict_from_2_csv_columns_throws_exceptions(
    key_col, val_col, exception_type, error_message
):
    file = DIR_WITH_FILETOOLS_TEST_FILES / "read_dict_from_2_csv_columns.csv"
    with pytest.raises(exception_type, match=error_message):
        read_dict_from_2_csv_columns(file, key_col=key_col, val_col=val_col)


def test_read_dicts_from_xls_reads_good_file():
    dicts = read_dicts_from_xls(
        DIR_WITH_FILETOOLS_TEST_FILES / "feature_profile_belarusian.xlsx", "Лист1"
    )

    dicts_from_gold_standard_csv = read_dicts_from_csv(
        DIR_WITH_FILETOOLS_TEST_FILES / "test_convert_excel_to_csv_gold_standard.csv"
    )

    for xls_row, csv_row in zip(dicts, dicts_from_gold_standard_csv):
        assert xls_row == csv_row


def test_read_dicts_from_xls_raises_exception_with_bad_sheet_name():
    with pytest.raises(KeyError):
        read_dicts_from_xls(
            DIR_WITH_FILETOOLS_TEST_FILES / "feature_profile_belarusian.xlsx", "foo"
        )


def test_write_csv_throws_exception_when_file_exists_and_overwrite_is_false():
    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode="w+", encoding="utf-8") as fh:
        fh.write("")

    with pytest.raises(FileExistsError):
        write_csv(["foo"], PATH_TO_TEST_OUTPUT_TXT_FILE, False, ",")

    PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_write_csv_throws_exception_when_rows_are_of_different_types():
    rows = [["foo", "bar"], {"bar": "baz"}]
    with pytest.raises(TypeError, match="Cannot write items of different types") as e:
        write_csv(rows, PATH_TO_TEST_OUTPUT_CSV_FILE, overwrite=False, delimiter=",")

    print("TEST: exception raised:", e)


def test_write_csv_throws_exception_when_rows_are_of_wrong_type():
    rows = [1, 2]
    with pytest.raises(TypeError, match="Supported types are list, tuple, dict, NamedTuple") as e:
        write_csv(rows, PATH_TO_TEST_OUTPUT_CSV_FILE, overwrite=False, delimiter=",")

    print("TEST: exception raised:", e)


class SomeNamedTuple(NamedTuple):
    foo1: str
    foo2: str


@pytest.mark.parametrize(
    "rows, expected_file_content",
    [
        ([["foo", "bar"], ["bar", "baz"]], "foo,bar\nbar,baz\n"),
        (
            [
                {"foo1": "bar1.1", "foo2": "bar2.1"},
                {"foo1": "b1.2", "foo2": "b2.2"},
                {"foo1": "b1.3", "foo2": "b2.3"},
            ],
            "foo1,foo2\nbar1.1,bar2.1\nb1.2,b2.2\nb1.3,b2.3\n",
        ),
        (
            [
                SomeNamedTuple(foo1="bar1", foo2="bar2"),
                SomeNamedTuple(foo2="bar2.2", foo1="bar1.2"),
            ],
            "foo1,foo2\nbar1,bar2\nbar1.2,bar2.2\n",
        ),
    ],
)
def test_write_csv(rows, expected_file_content):
    if PATH_TO_TEST_OUTPUT_CSV_FILE.exists():
        PATH_TO_TEST_OUTPUT_CSV_FILE.unlink()

    write_csv(rows, PATH_TO_TEST_OUTPUT_CSV_FILE, overwrite=False, delimiter=",")
    assert PATH_TO_TEST_OUTPUT_CSV_FILE.exists()

    content = read_plain_text_from_file(PATH_TO_TEST_OUTPUT_CSV_FILE)
    assert content == expected_file_content

    PATH_TO_TEST_OUTPUT_CSV_FILE.unlink()


def test_append_empty_column_to_csv_adds_new_column():
    input_file = DIR_WITH_FILETOOLS_TEST_FILES / "doculects_output_gold_standard.csv"
    output_file = DIR_WITH_FILETOOLS_TEST_FILES / "append_empty_column_doculects_output.csv"
    gold_standard_file_after_append = (
        DIR_WITH_FILETOOLS_TEST_FILES / "append_empty_column_doculects_gold_standard.csv"
    )

    append_empty_column_to_csv(
        path_to_file=input_file,
        name_of_new_column="new_column",
        custom_path_to_output_file=output_file,
    )
    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file, gold_standard_file_after_append
    )


def test_append_empty_column_to_csv_raises_exception_with_existing_custom_output_file():
    input_file = DIR_WITH_FILETOOLS_TEST_FILES / "doculects_output_gold_standard.csv"
    existing_file = (
        DIR_WITH_FILETOOLS_TEST_FILES / "append_empty_column_doculects_gold_standard.csv"
    )
    with pytest.raises(FileExistsError):
        append_empty_column_to_csv(
            path_to_file=input_file,
            custom_path_to_output_file=existing_file,
            name_of_new_column="foo",
        )


def test_append_empty_column_to_csv_raises_exception_with_existing_column():
    input_file = DIR_WITH_FILETOOLS_TEST_FILES / "doculects_output_gold_standard.csv"
    output_file = DIR_WITH_FILETOOLS_TEST_FILES / "append_empty_column_doculects_output.csv"
    with pytest.raises(ValueError):
        append_empty_column_to_csv(
            path_to_file=input_file,
            custom_path_to_output_file=output_file,
            name_of_new_column="type",
        )

    assert not output_file.exists()


def test_remove_one_row_and_return_its_line_number_remove_from_inventory_of_features(
    dummy_rows_of_features,
):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "A-1",
            "en": "Subject",
            "ru": "Подлежащее",
        },
        {
            "id": "A-2",
            "en": "Object",
            "ru": "Прямое дополнение",
        },
        {
            "id": "B-1",
            "en": "Collocation",
            "ru": "Коллокация",
        },
        {
            "id": "B-2",
            "en": "Grammatical core",
            "ru": "Грамматическая основа",
        },
        {
            "id": "С-1",
            "en": "Sentence",
            "ru": "Предложение",
        },
    )

    rows_with_one_line_removed, line_number_of_removed_row = remove_one_matching_row(
        lookup_column="id",
        match_content="A-3",
        rows=dummy_rows_of_features,
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == 2


def test_remove_one_row_from_inventory_of_listed_values(dummy_rows_of_listed_values):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "A-1-1",
            "feature_id": "A-1",
            "en": "Nominative",
            "ru": "Номинатив",
        },
        {
            "id": "A-1-3",
            "feature_id": "A-1",
            "en": "DSM",
            "ru": "Дифференцированное маркирование субъекта",
        },
        {
            "id": "B-1-1",
            "feature_id": "B-1",
            "en": "Agreement",
            "ru": "Согласование",
        },
        {
            "id": "B-1-2",
            "feature_id": "B-1",
            "en": "Word order",
            "ru": "Порядок слов",
        },
        {
            "id": "B-2-1",
            "feature_id": "B-2",
            "en": "Coordination",
            "ru": "Координация",
        },
    )

    rows_with_one_line_removed, line_number_of_removed_row = remove_one_matching_row(
        lookup_column="id",
        match_content="A-1-2",
        rows=dummy_rows_of_listed_values,
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == 1


def test_remove_one_row_from_a_feature_profile(dummy_rows_of_feature_profile):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "feature_id": "A-1",
            "feature_name_ru": "Некий признак",
            "value_type": "listed",
            "value_id": "A-1-1",
        },
        {
            "feature_id": "A-2",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-2-2",
        },
        {
            "feature_id": "A-3",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-3-3",
        },
        {
            "feature_id": "C-1",
            "feature_name_ru": "И еще признак",
            "value_type": "listed",
            "value_id": "C-1-1",
        },
    )

    rows_with_one_line_removed, line_number_of_removed_row = remove_one_matching_row(
        lookup_column="feature_id",
        match_content="B-1",
        rows=dummy_rows_of_feature_profile,
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == 3


def test_remove_one_row_remove_last_row(dummy_rows_of_feature_profile):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "feature_id": "A-1",
            "feature_name_ru": "Некий признак",
            "value_type": "listed",
            "value_id": "A-1-1",
        },
        {
            "feature_id": "A-2",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-2-2",
        },
        {
            "feature_id": "A-3",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-3-3",
        },
        {
            "feature_id": "B-1",
            "feature_name_ru": "Четвертый признак",
            "value_type": "listed",
            "value_id": "B-1-1",
        },
    )

    rows_with_one_line_removed, line_number_of_removed_row = remove_one_matching_row(
        lookup_column="feature_id",
        match_content="C-1",
        rows=dummy_rows_of_feature_profile,
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == 4


def test_remove_one_row_throws_exception_invalid_match_content(
    dummy_rows_of_listed_values,
):

    for bad_arg in (True, [1, 2]):
        with pytest.raises(TypeError, match="match_content must be of type <str> or <int>"):

            _, _ = remove_one_matching_row(
                lookup_column="id",
                match_content=bad_arg,
                rows=dummy_rows_of_listed_values,
            )


def test_remove_multiple_matching_rows_remove_values_of_A_1(
    dummy_rows_of_listed_values,
):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "B-1-1",
            "feature_id": "B-1",
            "en": "Agreement",
            "ru": "Согласование",
        },
        {
            "id": "B-1-2",
            "feature_id": "B-1",
            "en": "Word order",
            "ru": "Порядок слов",
        },
        {
            "id": "B-2-1",
            "feature_id": "B-2",
            "en": "Coordination",
            "ru": "Координация",
        },
    )

    rows_with_multiple_rows_removed, range_of_lin_numbers_of_removed_rows = (
        remove_multiple_matching_rows(
            lookup_column="feature_id",
            match_content="A-1",
            rows=dummy_rows_of_listed_values,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert range_of_lin_numbers_of_removed_rows == (0, 2)


def test_remove_multiple_matching_rows_remove_values_of_B_1(
    dummy_rows_of_listed_values,
):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "A-1-1",
            "feature_id": "A-1",
            "en": "Nominative",
            "ru": "Номинатив",
        },
        {
            "id": "A-1-2",
            "feature_id": "A-1",
            "en": "Ergative",
            "ru": "Эргатив",
        },
        {
            "id": "A-1-3",
            "feature_id": "A-1",
            "en": "DSM",
            "ru": "Дифференцированное маркирование субъекта",
        },
        {
            "id": "B-2-1",
            "feature_id": "B-2",
            "en": "Coordination",
            "ru": "Координация",
        },
    )

    rows_with_multiple_rows_removed, range_of_lin_numbers_of_removed_rows = (
        remove_multiple_matching_rows(
            lookup_column="feature_id",
            match_content="B-1",
            rows=dummy_rows_of_listed_values,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert range_of_lin_numbers_of_removed_rows == (3, 4)


def test_remove_multiple_matching_rows_remove_value_of_B_2(
    dummy_rows_of_listed_values,
):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "A-1-1",
            "feature_id": "A-1",
            "en": "Nominative",
            "ru": "Номинатив",
        },
        {
            "id": "A-1-2",
            "feature_id": "A-1",
            "en": "Ergative",
            "ru": "Эргатив",
        },
        {
            "id": "A-1-3",
            "feature_id": "A-1",
            "en": "DSM",
            "ru": "Дифференцированное маркирование субъекта",
        },
        {
            "id": "B-1-1",
            "feature_id": "B-1",
            "en": "Agreement",
            "ru": "Согласование",
        },
        {
            "id": "B-1-2",
            "feature_id": "B-1",
            "en": "Word order",
            "ru": "Порядок слов",
        },
    )

    rows_with_multiple_rows_removed, range_of_lin_numbers_of_removed_rows = (
        remove_multiple_matching_rows(
            lookup_column="feature_id",
            match_content="B-2",
            rows=dummy_rows_of_listed_values,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert range_of_lin_numbers_of_removed_rows == (5, 5)


def test_remove_multiple_matching_rows_throws_exception_invalid_feature_id(
    dummy_rows_of_listed_values,
):

    with pytest.raises(TypeError, match="match_content must be of type <str> or <int>"):
        remove_multiple_matching_rows(
            lookup_column="feature_id",
            match_content=False,
            rows=dummy_rows_of_listed_values,
        )


def test_remove_matching_rows_remove_one_row_from_inventory_of_features(dummy_rows_of_features):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "A-1",
            "en": "Subject",
            "ru": "Подлежащее",
        },
        {
            "id": "A-2",
            "en": "Object",
            "ru": "Прямое дополнение",
        },
        {
            "id": "B-1",
            "en": "Collocation",
            "ru": "Коллокация",
        },
        {
            "id": "B-2",
            "en": "Grammatical core",
            "ru": "Грамматическая основа",
        },
        {
            "id": "С-1",
            "en": "Sentence",
            "ru": "Предложение",
        },
    )

    rows_with_one_line_removed, line_number_of_removed_row = remove_matching_rows(
        lookup_column="id",
        match_content="A-3",
        rows=dummy_rows_of_features,
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == (2,)


def test_remove_matching_rows_remove_one_row_from_inventory_of_listed_values(dummy_rows_of_listed_values):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "A-1-1",
            "feature_id": "A-1",
            "en": "Nominative",
            "ru": "Номинатив",
        },
        {
            "id": "A-1-3",
            "feature_id": "A-1",
            "en": "DSM",
            "ru": "Дифференцированное маркирование субъекта",
        },
        {
            "id": "B-1-1",
            "feature_id": "B-1",
            "en": "Agreement",
            "ru": "Согласование",
        },
        {
            "id": "B-1-2",
            "feature_id": "B-1",
            "en": "Word order",
            "ru": "Порядок слов",
        },
        {
            "id": "B-2-1",
            "feature_id": "B-2",
            "en": "Coordination",
            "ru": "Координация",
        },
    )

    rows_with_one_line_removed, line_number_of_removed_row = remove_matching_rows(
        lookup_column="id",
        match_content="A-1-2",
        rows=dummy_rows_of_listed_values,
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == (1,)


def test_remove_matching_rows_remove_one_row_from_a_feature_profile(dummy_rows_of_feature_profile):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "feature_id": "A-1",
            "feature_name_ru": "Некий признак",
            "value_type": "listed",
            "value_id": "A-1-1",
        },
        {
            "feature_id": "A-2",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-2-2",
        },
        {
            "feature_id": "A-3",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-3-3",
        },
        {
            "feature_id": "C-1",
            "feature_name_ru": "И еще признак",
            "value_type": "listed",
            "value_id": "C-1-1",
        },
    )

    rows_with_one_line_removed, line_number_of_removed_row = remove_matching_rows(
        lookup_column="feature_id",
        match_content="B-1",
        rows=dummy_rows_of_feature_profile,
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == (3,)


def test_remove_matching_rows_remove_last_row(dummy_rows_of_feature_profile):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "feature_id": "A-1",
            "feature_name_ru": "Некий признак",
            "value_type": "listed",
            "value_id": "A-1-1",
        },
        {
            "feature_id": "A-2",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-2-2",
        },
        {
            "feature_id": "A-3",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-3-3",
        },
        {
            "feature_id": "B-1",
            "feature_name_ru": "Четвертый признак",
            "value_type": "listed",
            "value_id": "B-1-1",
        },
    )

    rows_with_one_line_removed, line_number_of_removed_row = remove_matching_rows(
        lookup_column="feature_id",
        match_content="C-1",
        rows=dummy_rows_of_feature_profile,
    )

    assert rows_with_one_line_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_number_of_removed_row == (4,)


def test_remove_matching_rows_remove_multiple_subsequent_values_of_A_1(
    dummy_rows_of_listed_values,
):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "B-1-1",
            "feature_id": "B-1",
            "en": "Agreement",
            "ru": "Согласование",
        },
        {
            "id": "B-1-2",
            "feature_id": "B-1",
            "en": "Word order",
            "ru": "Порядок слов",
        },
        {
            "id": "B-2-1",
            "feature_id": "B-2",
            "en": "Coordination",
            "ru": "Координация",
        },
    )

    rows_with_multiple_rows_removed, line_numbers_of_removed_rows = (
        remove_matching_rows(
            lookup_column="feature_id",
            match_content="A-1",
            rows=dummy_rows_of_listed_values,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_numbers_of_removed_rows == (0, 1, 2)


def test_remove_matching_rows_remove_multiple_subsequent_values_of_B_1(
    dummy_rows_of_listed_values,
):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "A-1-1",
            "feature_id": "A-1",
            "en": "Nominative",
            "ru": "Номинатив",
        },
        {
            "id": "A-1-2",
            "feature_id": "A-1",
            "en": "Ergative",
            "ru": "Эргатив",
        },
        {
            "id": "A-1-3",
            "feature_id": "A-1",
            "en": "DSM",
            "ru": "Дифференцированное маркирование субъекта",
        },
        {
            "id": "B-2-1",
            "feature_id": "B-2",
            "en": "Coordination",
            "ru": "Координация",
        },
    )

    rows_with_multiple_rows_removed, line_numbers_of_removed_rows = (
        remove_matching_rows(
            lookup_column="feature_id",
            match_content="B-1",
            rows=dummy_rows_of_listed_values,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_numbers_of_removed_rows == (3, 4)


def test_remove_matching_rows_remove_multiple_subsequent_values_of_B_2(
    dummy_rows_of_listed_values,
):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "A-1-1",
            "feature_id": "A-1",
            "en": "Nominative",
            "ru": "Номинатив",
        },
        {
            "id": "A-1-2",
            "feature_id": "A-1",
            "en": "Ergative",
            "ru": "Эргатив",
        },
        {
            "id": "A-1-3",
            "feature_id": "A-1",
            "en": "DSM",
            "ru": "Дифференцированное маркирование субъекта",
        },
        {
            "id": "B-1-1",
            "feature_id": "B-1",
            "en": "Agreement",
            "ru": "Согласование",
        },
        {
            "id": "B-1-2",
            "feature_id": "B-1",
            "en": "Word order",
            "ru": "Порядок слов",
        },
    )

    rows_with_multiple_rows_removed, line_numbers_of_removed_rows = (
        remove_matching_rows(
            lookup_column="feature_id",
            match_content="B-2",
            rows=dummy_rows_of_listed_values,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_numbers_of_removed_rows == (5,)


def test_remove_matching_rows_remove_multiple_scattered_rows_with_type_variable(dummy_rows_with_scattered_values):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "17",
            "domain": "morphology",
            "type": "constant",
        },
        {
            "id": "19",
            "domain": "syntax",
            "type": "constant",
        },
        {
            "id": "20",
            "domain": "syntax",
            "type": "constant",
        },
        {
            "id": "22",
            "domain": "morphology",
            "type": "constant",
        },
    )

    rows_with_multiple_rows_removed, line_numbers_of_removed_rows = (
        remove_matching_rows(
            lookup_column="type",
            match_content="variable",
            rows=dummy_rows_with_scattered_values,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_numbers_of_removed_rows == (1, 4)


def test_remove_matching_rows_remove_multiple_scattered_rows_with_domain_morphology(dummy_rows_with_scattered_values):

    GOLD_STANDARD_DUMMY_ROWS = (
        {
            "id": "19",
            "domain": "syntax",
            "type": "constant",
        },
        {
            "id": "20",
            "domain": "syntax",
            "type": "constant",
        },
        {
            "id": "21",
            "domain": "syntax",
            "type": "variable",
        },
    )

    rows_with_multiple_rows_removed, line_numbers_of_removed_rows = (
        remove_matching_rows(
            lookup_column="domain",
            match_content="morphology",
            rows=dummy_rows_with_scattered_values,
        )
    )

    assert rows_with_multiple_rows_removed == GOLD_STANDARD_DUMMY_ROWS

    assert line_numbers_of_removed_rows == (0, 1, 5)
