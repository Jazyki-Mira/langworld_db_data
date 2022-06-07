from langworld_db_data.featureprofiletools.getters import *
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES


def test_get_feature_profile_as_dict():
    dict_ = get_feature_profile_as_dict(
        doculect_id='catalan_short',
        dir_with_feature_profiles=DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES
    )

    assert dict_ == {
        'A-1': {
            'feature_name_ru': 'Количество степеней подъема',
            'value_type': 'listed', 'value_id': 'A-1-2', 'value_ru': 'Три',
            'comment_ru': '', 'comment_en': ''
        },
        'A-2': {
            'feature_name_ru': 'Подъемы гласных',
            'value_type': 'custom', 'value_id': '', 'value_ru': 'Верхний, средний (закрытые и открытые) и нижний',
            'comment_ru': '', 'comment_en': ''
        },
        'A-3': {
            'feature_name_ru': 'Ряды гласных',
            'value_type': 'listed', 'value_id': 'A-3-4', 'value_ru': 'Передний, средний и задний',
            'comment_ru': '', 'comment_en': ''
        },
    }
