import pytest

from langworld_db_data.validators.asset_validator import AssetValidator, AssetValidatorError
from tests.paths import DIR_WITH_VALIDATORS_TEST_FILES

FILE_WITH_DOCULECTS = DIR_WITH_VALIDATORS_TEST_FILES / 'doculects_for_asset_validator.csv'
FILE_WITH_MAPS = DIR_WITH_VALIDATORS_TEST_FILES / 'encyclopedia_maps_for_asset_validator.csv'
GOOD_FILE_MATCHING_MAPS_TO_DOCULECTS = DIR_WITH_VALIDATORS_TEST_FILES / 'encyclopedia_map_to_doculect_OK.csv'


def test__validate_file_matching_maps_to_doculects_fails_with_repeating_rows():
    with pytest.raises(AssetValidatorError, match=r"has a repeating row: \('5-1', 'dari'\)"):
        AssetValidator(
            file_with_doculects=FILE_WITH_DOCULECTS,
            file_with_encyclopedia_maps=FILE_WITH_MAPS,
            file_matching_maps_to_doculects=(
                DIR_WITH_VALIDATORS_TEST_FILES /
                'encyclopedia_map_to_doculect_bad_repeating_row.csv'))._validate_file_matching_maps_to_doculects()


def test__validate_file_matching_maps_to_doculects_fails_with_bad_map_id():
    with pytest.raises(AssetValidatorError,
                       match="Row 2 in file encyclopedia_map_to_doculect_bad_map_id.csv: Map ID 99-9 not found"):
        AssetValidator(file_with_doculects=FILE_WITH_DOCULECTS,
                       file_with_encyclopedia_maps=FILE_WITH_MAPS,
                       file_matching_maps_to_doculects=(
                           DIR_WITH_VALIDATORS_TEST_FILES /
                           'encyclopedia_map_to_doculect_bad_map_id.csv'))._validate_file_matching_maps_to_doculects()


def test__validate_file_matching_maps_to_doculects_fails_with_bad_doculect_id():
    with pytest.raises(AssetValidatorError,
                       match="Row 4 in file encyclopedia_map_to_doculect_bad_doculect_id.csv: Doculect ID foo"):
        AssetValidator(
            file_with_doculects=FILE_WITH_DOCULECTS,
            file_with_encyclopedia_maps=FILE_WITH_MAPS,
            file_matching_maps_to_doculects=(
                DIR_WITH_VALIDATORS_TEST_FILES /
                'encyclopedia_map_to_doculect_bad_doculect_id.csv'))._validate_file_matching_maps_to_doculects()


def test_validate_fails_with_bad_test_data():
    for file in DIR_WITH_VALIDATORS_TEST_FILES.glob('encyclopedia_map_to_doculect_bad*.csv'):
        print(f'TEST: file {file.name}')

        with pytest.raises(AssetValidatorError):
            AssetValidator(
                file_with_doculects=FILE_WITH_DOCULECTS,
                file_with_encyclopedia_maps=FILE_WITH_MAPS,
                file_matching_maps_to_doculects=file,
            ).validate()


def test_validate_passes_with_good_test_data():
    AssetValidator(file_with_doculects=FILE_WITH_DOCULECTS,
                   file_with_encyclopedia_maps=FILE_WITH_MAPS,
                   file_matching_maps_to_doculects=GOOD_FILE_MATCHING_MAPS_TO_DOCULECTS).validate()


def test_validate_passes_with_real_data():
    AssetValidator().validate()
