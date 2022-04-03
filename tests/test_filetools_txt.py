import pytest

from langworld_db_data.filetools.txt import *
from tests.paths import *


def test_check_encoding_of_file():
    for encoding in ('utf-8-sig', 'cp1251'):
        with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode='w+', encoding=encoding) as fh:
            fh.write('что-то по-русски (English characters will not cause failure)')

        assert check_encoding_of_file(PATH_TO_TEST_OUTPUT_TXT_FILE) == encoding
        PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_read_non_empty_lines_from_txt_file():
    lines = [' foo \n', 'bar\n', '\n', 'баз \n']

    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode='w+', encoding='utf-8') as fh:
        fh.writelines(lines)

    assert read_non_empty_lines_from_txt_file(PATH_TO_TEST_OUTPUT_TXT_FILE) == ['foo', 'bar', 'баз']
    PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_read_plain_text_from_file():
    for file in DIR_WITH_FILETOOLS_TEST_FILES.glob('read_plain_text*.txt'):
        print(f'TEST: reading plain content from {file=}')
        assert read_plain_text_from_file(file) == 'foo bar\nфу бар'


@pytest.mark.parametrize(
    'content, expected_output',
    [
        ('foo bar', 'foo bar'),
        (['foo', 'bar'], 'foo\nbar\n'),
    ]
)
def test_write_plain_text_to_file_writes_content_to_file(content, expected_output):

    if PATH_TO_TEST_OUTPUT_TXT_FILE.exists():
        PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()

    write_plain_text_to_file(content, PATH_TO_TEST_OUTPUT_TXT_FILE, False)

    assert PATH_TO_TEST_OUTPUT_TXT_FILE.exists()

    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode='r', encoding='utf-8') as fh:
        assert fh.read() == expected_output

    PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_write_plain_text_to_file_overwrites_content_in_overwrite_mode():
    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode='w+', encoding='utf-8') as fh:
        fh.write('foo')

    write_plain_text_to_file('bar', PATH_TO_TEST_OUTPUT_TXT_FILE, True)

    assert PATH_TO_TEST_OUTPUT_TXT_FILE.exists()

    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode='r', encoding='utf-8') as fh:
        assert fh.read() == 'bar'

    PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_write_plain_text_to_file_throws_exception_when_file_exists_and_overwrite_is_false():
    with PATH_TO_TEST_OUTPUT_TXT_FILE.open(mode='w+', encoding='utf-8') as fh:
        fh.write('')

    with pytest.raises(FileExistsError):
        write_plain_text_to_file('foo', PATH_TO_TEST_OUTPUT_TXT_FILE, False)

    PATH_TO_TEST_OUTPUT_TXT_FILE.unlink()


def test_write_plain_text_to_file_throws_exception_with_wrong_data():
    for content in (5, {'foo': 'bar'}):
        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            write_plain_text_to_file(content, PATH_TO_TEST_OUTPUT_TXT_FILE, False)
