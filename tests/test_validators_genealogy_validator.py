import pytest

from langworld_db_data.validators.genealogy_validator import *
from tests.paths import DIR_WITH_VALIDATORS_TEST_FILES

GOOD_FILE_WITH_HIERARCHY = DIR_WITH_VALIDATORS_TEST_FILES / 'genealogy_families_hierarchy_OK.yaml'
GOOD_FILE_WITH_NAMES = DIR_WITH_VALIDATORS_TEST_FILES / 'genealogy_families_names_OK.csv'


def test___check_and_get_ids_from_hierarchy_fails_for_malformed_family_id():
    with pytest.raises(GenealogyValidatorError) as e:
        GenealogyValidator(file_with_hierarchy=DIR_WITH_VALIDATORS_TEST_FILES /
                           'genealogy_families_hierarchy_bad_malformed_id.yaml',
                           file_with_names=GOOD_FILE_WITH_NAMES)._check_and_get_ids_from_hierarchy()

    assert 'can only contain lowercase letters and underscores' in str(e)


def test___check_and_get_ids_from_hierarchy_fails_for_family_id_that_is_not_in_file_with_names():
    with pytest.raises(GenealogyValidatorError) as e:
        GenealogyValidator(
            file_with_hierarchy=(DIR_WITH_VALIDATORS_TEST_FILES /
                                 'genealogy_families_hierarchy_bad_id_not_found_in_file_with_names.yaml'),
            file_with_names=GOOD_FILE_WITH_NAMES)._check_and_get_ids_from_hierarchy()

    assert 'foobar in hierarchy not found in file with names' in str(e)


def test___check_and_get_ids_from_hierarchy_fails_for_non_unique_family_id():
    with pytest.raises(GenealogyValidatorError) as e:
        GenealogyValidator(
            file_with_hierarchy=(DIR_WITH_VALIDATORS_TEST_FILES /
                                 'genealogy_families_hierarchy_bad_duplicate_id_on_different_levels.yaml'),
            file_with_names=GOOD_FILE_WITH_NAMES)._check_and_get_ids_from_hierarchy()

    assert 'Family ID south_east_tung was seen 3 times' in str(e)


def test__check_ids_in_list_of_names_fails_for_file_with_malformed_family_id():
    validator = GenealogyValidator(file_with_names=DIR_WITH_VALIDATORS_TEST_FILES /
                                   'genealogy_families_names_bad_malformed_id.csv',
                                   file_with_hierarchy=GOOD_FILE_WITH_HIERARCHY)

    # this is not needed for the test but needed for the method being tested to run
    ids_from_hierarchy = validator._check_and_get_ids_from_hierarchy()

    with pytest.raises(GenealogyValidatorError) as e:
        validator._check_ids_in_list_of_names(ids_from_hierarchy)

    assert 'only use lowercase' in str(e)


def test__check_ids_in_list_of_names_fails_for_file_with_family_id_that_does_not_match_any_id_in_hierarchy():
    validator = GenealogyValidator(file_with_names=DIR_WITH_VALIDATORS_TEST_FILES /
                                   'genealogy_families_names_bad_id_is_not_found_in_hierarchy.csv',
                                   file_with_hierarchy=GOOD_FILE_WITH_HIERARCHY)

    ids_from_hierarchy = validator._check_and_get_ids_from_hierarchy()

    with pytest.raises(GenealogyValidatorError) as e:
        validator._check_ids_in_list_of_names(ids_from_hierarchy)

    assert 'ID foobar not found in file with genealogy hierarchy' in str(e)


def test_validate_fails_for_bad_files_with_hierarchy():
    for file in DIR_WITH_VALIDATORS_TEST_FILES.glob('genealogy_families_hierarchy_bad_*.yaml'):
        print(f'TEST: file {file.name}')
        with pytest.raises(GenealogyValidatorError):
            GenealogyValidator(
                file_with_hierarchy=file,
                file_with_names=GOOD_FILE_WITH_NAMES,
            ).validate()


def test_validate_fails_for_bad_files_with_names_of_families():
    for file in DIR_WITH_VALIDATORS_TEST_FILES.glob('genealogy_families_names_bad_*.csv'):
        print(f'TEST: file {file.name}')
        with pytest.raises(GenealogyValidatorError):
            GenealogyValidator(
                file_with_hierarchy=GOOD_FILE_WITH_HIERARCHY,
                file_with_names=file,
            ).validate()


def test_validate_passes_for_good_files():
    GenealogyValidator(
        file_with_hierarchy=GOOD_FILE_WITH_HIERARCHY,
        file_with_names=GOOD_FILE_WITH_NAMES,
    ).validate()


def test_validate_passes_for_real_data():
    GenealogyValidator().validate()
