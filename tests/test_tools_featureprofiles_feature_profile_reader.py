import pytest

from langworld_db_data.tools.featureprofiles.data_structures import (
    ValueForFeatureProfileDictionary,
)
from langworld_db_data.tools.featureprofiles.feature_profile_reader import FeatureProfileReader
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES


@pytest.fixture(scope="function")
def test_reader():
    return FeatureProfileReader()


benchmark_dict = {
    "A-1": ValueForFeatureProfileDictionary(
        feature_name_ru="Количество степеней подъема",
        value_type="listed",
        value_id="A-1-2",
        value_ru="Три",
        comment_ru="",
        comment_en="",
        page_numbers="",
    ),
    "A-2": ValueForFeatureProfileDictionary(
        feature_name_ru="Подъемы гласных",
        value_type="custom",
        value_id="",
        value_ru="Верхний, средний (закрытые и открытые) и нижний",
        comment_ru="",
        comment_en="",
        page_numbers="",
    ),
    "A-3": ValueForFeatureProfileDictionary(
        feature_name_ru="Ряды гласных",
        value_type="listed",
        value_id="A-3-4",
        value_ru="Передний, средний и задний",
        comment_ru="",
        comment_en="",
        page_numbers="",
    ),
}


def test_read_feature_profile_as_dict_from_doculect_id(test_reader):
    dict_ = test_reader.read_feature_profile_as_dict_from_doculect_id(
        doculect_id="catalan_short",
        dir_with_feature_profiles=DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES,
    )

    assert dict_ == benchmark_dict


def test_read_feature_profile_as_dict_from_file(test_reader):
    dict_ = test_reader.read_feature_profile_as_dict_from_file(
        DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / "catalan_short.csv"
    )

    assert dict_ == benchmark_dict


def test_read_feature_profile_as_dict_from_file_fails_with_bad_file(test_reader):
    with pytest.raises(ValueError, match="does not contain feature ID in row 4"):
        test_reader.read_feature_profile_as_dict_from_file(
            DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / "corsican_bad_no_feature_ID.csv"
        )


@pytest.mark.parametrize(
    "doculect_id, feature_id, expected_output",
    [
        (
            "catalan",
            "A-1",
            {
                "value_type": "listed",
                "value_id": "A-1-2",
                "value_ru": "Три",
                "comment_ru": "",
            },
        ),
        (
            "catalan",
            "D-6",
            {
                "value_type": "not_stated",
                "value_id": "",
                "value_ru": "",
                "comment_ru": "Систематизированных данных нет.",
            },
        ),
    ],
)
def test_read_value_for_doculect_and_feature(
    test_reader, doculect_id, feature_id, expected_output
):
    dict_ = test_reader.read_value_for_doculect_and_feature(
        doculect_id=doculect_id,
        feature_id=feature_id,
        dir_with_feature_profiles=DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES,
        copy_to_clipboard=False,
        verbose=True,
    )
    assert dict_ == expected_output


def test_read_value_for_doculect_and_feature_fails_with_wrong_feature_id(test_reader):
    with pytest.raises(KeyError, match="'X-99' not found for doculect_id='catalan'"):
        test_reader.read_value_for_doculect_and_feature(
            "catalan", "X-99", DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES
        )
