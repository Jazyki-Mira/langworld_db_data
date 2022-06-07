import pytest

from langworld_db_data.featureprofiletools.getters import *
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES


def test_get_feature_profile_as_dict():
    dict_ = get_feature_profile_as_dict(
        doculect_id='catalan_short',
        dir_with_feature_profiles=DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES
    )

    assert dict_ == {
        'A-1': ValueForFeatureProfileDictionary(
            feature_name_ru='Количество степеней подъема',
            value_type='listed',
            value_id='A-1-2',
            value_ru='Три',
            comment_ru='',
            comment_en='',
        ),
        'A-2': ValueForFeatureProfileDictionary(
            feature_name_ru='Подъемы гласных',
            value_type='custom',
            value_id='',
            value_ru='Верхний, средний (закрытые и открытые) и нижний',
            comment_ru='',
            comment_en='',
        ),
        'A-3': ValueForFeatureProfileDictionary(
            feature_name_ru='Ряды гласных',
            value_type='listed',
            value_id='A-3-4',
            value_ru='Передний, средний и задний',
            comment_ru='',
            comment_en='',
        ),
    }


@pytest.mark.parametrize(
    'doculect_id, feature_id, expected_output',
    [
        ('catalan', 'A-1', {
            'value_type': 'listed', 'value_id': 'A-1-2', 'value_ru': 'Три', 'comment_ru': ''
        }),
        ('catalan', 'D-6', {
            'value_type': 'not_stated', 'value_id': '', 'value_ru': '', 'comment_ru': 'Систематизированных данных нет.'
        }),
    ]
)
def test_get_value_for_doculect_and_feature(doculect_id, feature_id, expected_output):
    dict_ = get_value_for_doculect_and_feature(
        doculect_id=doculect_id,
        feature_id=feature_id,
        dir_with_feature_profiles=DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES,
        copy_to_clipboard=False,
        verbose=True,
    )
    assert dict_ == expected_output


def test_get_value_for_doculect_and_feature_fails_with_wrong_feature_id():
    with pytest.raises(KeyError) as e:
        get_value_for_doculect_and_feature('catalan', 'X-99', DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES)

    assert "'X-99' not found for doculect_id='catalan'" in str(e)
