import pytest

from langworld_db_data.filetools.txt import (
    check_encoding_of_file,
    move_line,
    read_non_empty_lines_from_txt_file,
    read_plain_text_from_file,
    remove_extra_space,
    write_plain_text_to_file,
)
from tests.helpers import check_existence_of_output_txt_file_and_compare_with_benchmark
from tests.paths import DIR_WITH_FILETOOLS_TEST_FILES, PATH_TO_TEST_OUTPUT_TXT_FILE


def test_check_encoding_of_file():
    for encoding in ("utf-8-sig", "cp1251"):
        with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode="w+", encoding=encoding) as fh:
            fh.write("что-то по-русски (English characters will not cause failure)")

        assert check_encoding_of_file(PATH_TO_TEST_OUTPUT_TXT_FILE) == encoding
        PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()

@pytest.mark.parametrize(
    "file_stem, line_number_to_cut, line_number_to_insert_before",
    [
        ("tc1-2", 1, 2),
        ("tc1-2", 2, 2),
        ("tc3-4", 3, 2),
        ("tc3-4", 2, 4),
        ("tc5", 1, 5),
        ("tc6", 4, 1),
        ("tc7", 3, "END"),
        ("tc8", 3, 0),
        ("tc9-11", 0, "END"),
        ("tc9-11", 0, "end"),
        ("tc9-11", 0, "FINISH"),
        ("tc12", 5, 0),
    ],
)
def test_move_line(file_stem, line_number_to_cut, line_number_to_insert_before):
    dir_with_test_files = DIR_WITH_FILETOOLS_TEST_FILES / "move_line"
    tmp_output_file = dir_with_test_files / "output_tmp.txt"
    move_line(
        file=dir_with_test_files / f"{file_stem}.txt",
        line_number_to_cut=line_number_to_cut,
        line_number_to_insert_before=line_number_to_insert_before,
        output_file=tmp_output_file,
    )
    check_existence_of_output_txt_file_and_compare_with_benchmark(
        output_file=tmp_output_file,
        benchmark_file=dir_with_test_files / "benchmark.txt"
    )


def test_read_non_empty_lines_from_txt_file():
    lines = [" foo \n", "bar\n", "\n", "баз \n"]

    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode="w+", encoding="utf-8") as fh:
        fh.writelines(lines)

    assert read_non_empty_lines_from_txt_file(PATH_TO_TEST_OUTPUT_TXT_FILE) == [
        "foo",
        "bar",
        "баз",
    ]
    PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_read_plain_text_from_file():
    for file in DIR_WITH_FILETOOLS_TEST_FILES.glob("read_plain_text*.txt"):
        print(f"TEST: reading plain content from {file=}")
        assert read_plain_text_from_file(file) == "foo bar\nфу бар"


def test_remove_extra_space():
    for str_ in (
        "foo bar",
        " foo bar",
        "foo bar ",
        " foo bar  ",
        "foo  bar",
        " foo   bar ",
    ):
        assert remove_extra_space(str_) == "foo bar"


@pytest.mark.parametrize(
    "content, expected_output",
    [
        ("foo bar", "foo bar"),
        (["foo", "bar"], "foo\nbar\n"),
    ],
)
def test_write_plain_text_to_file_writes_content_to_file(content, expected_output):
    if PATH_TO_TEST_OUTPUT_TXT_FILE.exists():
        PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()

    write_plain_text_to_file(content, PATH_TO_TEST_OUTPUT_TXT_FILE, False)

    assert PATH_TO_TEST_OUTPUT_TXT_FILE.exists()

    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(encoding="utf-8") as fh:
        assert fh.read() == expected_output

    PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_write_plain_text_to_file_overwrites_content_in_overwrite_mode():
    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode="w+", encoding="utf-8") as fh:
        fh.write("foo")

    write_plain_text_to_file("bar", PATH_TO_TEST_OUTPUT_TXT_FILE, True)

    assert PATH_TO_TEST_OUTPUT_TXT_FILE.exists()

    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(encoding="utf-8") as fh:
        assert fh.read() == "bar"

    PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_write_plain_text_to_file_throws_exception_when_file_exists_and_overwrite_is_false():  # noqa E501
    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode="w+", encoding="utf-8") as fh:
        fh.write("")

    with pytest.raises(FileExistsError):
        write_plain_text_to_file("foo", PATH_TO_TEST_OUTPUT_TXT_FILE, False)

    PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_write_plain_text_to_file_throws_exception_with_wrong_data():
    for content in (5, {"foo": "bar"}):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            write_plain_text_to_file(content, PATH_TO_TEST_OUTPUT_TXT_FILE, False)
