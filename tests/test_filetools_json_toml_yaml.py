import pytest

from langworld_db_data.filetools.json_toml_yaml import check_yaml_file, ParserError, read_json_toml_yaml
from tests.paths import DIR_WITH_FILETOOLS_TEST_FILES


def test_check_yaml_file_passes_with_valid_data():
    for file in DIR_WITH_FILETOOLS_TEST_FILES.glob('yaml_OK*.yaml'):
        # no assert needed because exception will be thrown in function if something is wrong
        check_yaml_file(file)


def test_check_yaml_file_fails_with_invalid_data():
    for file in DIR_WITH_FILETOOLS_TEST_FILES.glob('yaml_bad*.yaml'):
        with pytest.raises(ParserError) as e:
            check_yaml_file(file)

        print('TEST: error message received - ', e)


def test_read_json_toml_yaml():
    # TOML files are not used yet, they are tested in a different project
    for file_name in ('json_OK_language_names_to_new_ids.json', 'socio_aromanian_gold_standard.yaml'):
        data = read_json_toml_yaml(DIR_WITH_FILETOOLS_TEST_FILES / file_name)
        assert isinstance(data, (dict, list))
        assert len(data.keys()) > 0

    for file in DIR_WITH_FILETOOLS_TEST_FILES.glob('yaml_OK*.yaml'):
        print(f'TEST: file {file}')
        assert isinstance(read_json_toml_yaml(file), (dict, list))


def test_read_json_toml_yaml_raises_exception_with_unsupported_file_type():
    for file_name in ('test_convert_excel_to_csv_gold_standard.csv', 'read_plain_text_utf8.txt'):
        with pytest.raises(TypeError):
            read_json_toml_yaml(DIR_WITH_FILETOOLS_TEST_FILES / file_name)


def test_read_json_toml_yaml_raises_exception_with_bad_yaml():
    for file in DIR_WITH_FILETOOLS_TEST_FILES.glob('yaml_bad*.yaml'):
        print(f'TEST: file {file}')
        with pytest.raises(ParserError):
            read_json_toml_yaml(file)
