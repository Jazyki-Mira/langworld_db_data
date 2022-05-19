import pytest

from langworld_db_data.adders.feature_adder import *
from tests.paths import (
    DIR_WITH_ADDERS_TEST_FILES,
    DIR_WITH_ADDERS_FEATURE_PROFILES,
    INPUT_FILE_WITH_LISTED_VALUES,
    OUTPUT_DIR_WITH_ADDERS_FEATURE_PROFILES,
)


dummy_values_to_add = [
    {'ru': 'Одно явление', 'en': 'One thing'},
    {'ru': 'Одно, два и третье', 'en': 'One thing, second thing, and third thing'}
]


@pytest.fixture(scope='function')
def test_feature_adder():
    return FeatureAdder(
        file_with_categories=DIR_WITH_ADDERS_TEST_FILES / 'feature_categories.csv',
        input_file_with_features=DIR_WITH_ADDERS_TEST_FILES / 'features.csv',
        output_file_with_features=DIR_WITH_ADDERS_TEST_FILES / 'features_output.csv',
        input_file_with_listed_values=INPUT_FILE_WITH_LISTED_VALUES,
        output_file_with_listed_values=DIR_WITH_ADDERS_TEST_FILES / 'features_listed_values_output.csv',
        input_dir_with_feature_profiles=DIR_WITH_ADDERS_FEATURE_PROFILES,
        output_dir_with_feature_profiles=OUTPUT_DIR_WITH_ADDERS_FEATURE_PROFILES,
    )


def test_add_feature_fails_with_empty_arg(test_feature_adder):
    for incomplete_set_of_args in (
        {'category_id': '', 'feature_ru': 'раз', 'feature_en': 'one', 'listed_values_to_add': dummy_values_to_add},
        {'category_id': 'A', 'feature_ru': '', 'feature_en': 'one', 'listed_values_to_add': dummy_values_to_add},
        {'category_id': 'A', 'feature_ru': 'раз', 'feature_en': '', 'listed_values_to_add': dummy_values_to_add},
        {'category_id': 'A', 'feature_ru': 'раз', 'feature_en': 'one', 'listed_values_to_add': []},
    ):
        with pytest.raises(FeatureAdderError) as e:
            test_feature_adder.add_feature(**incomplete_set_of_args)

        assert 'Some of the values passed are empty' in str(e)


def test_add_feature_fails_with_wrong_new_listed_values(test_feature_adder):
    args = {'category_id': 'A', 'feature_ru': 'раз', 'feature_en': 'one',
            'listed_values_to_add': [
                {'ru': 'раз', 'en': 'this is fine'},
                {'this': 'should fail', 'en': 'this is fine'},
            ]}
    with pytest.raises(FeatureAdderError) as e:
        test_feature_adder.add_feature(**args)

    assert "must have keys 'en' and 'ru'. Your value: {'this': 'should fail', 'en': 'this is fine'}" in str(e)


def test_add_feature_fails_with_wrong_category_id(test_feature_adder):
    with pytest.raises(FeatureAdderError) as e:
        test_feature_adder.add_feature(
            category_id='X',
            feature_ru='имя',
            feature_en='name',
            listed_values_to_add=dummy_values_to_add
        )

    assert f'Category ID <X> not found in file {test_feature_adder.file_with_categories.name}' in str(e)


def test_add_feature_fails_with_existing_feature_name(test_feature_adder):
    for en, ru in (('Stress character ', 'Новый признак'), ('New  feature', 'Типы фонации')):
        with pytest.raises(FeatureAdderError) as e:
            test_feature_adder.add_feature(
                category_id='A',
                feature_en=en,
                feature_ru=ru,
                listed_values_to_add=dummy_values_to_add,
            )

        assert 'English or Russian feature name is already' in str(e)


def test_add_feature_fails_with_non_existent_index_of_feature_to_insert_after(test_feature_adder):
    for number in [0, 22, 250]:
        with pytest.raises(FeatureAdderError) as e:
            test_feature_adder.add_feature(
                category_id='A',
                feature_en='Foo',
                feature_ru='Фу',
                listed_values_to_add=dummy_values_to_add,
                index_to_add_after=number,
            )

        assert f'Cannot add feature after A-{number}' in str(e)


def test__build_feature_id_fails_with_existing_index(test_feature_adder):
    with pytest.raises(FeatureAdderError) as e:
        test_feature_adder._generate_feature_id(category_id='A', custom_index_of_new_feature=211)

    assert 'Feature index 211 already in use in category A' in str(e)


def test__build_feature_id_fails_with_small_index(test_feature_adder):
    with pytest.raises(FeatureAdderError) as e:
        test_feature_adder._generate_feature_id(category_id='A', custom_index_of_new_feature=99)

    assert 'must be greater than 100 (you gave 99)' in str(e)


def test__build_feature_id_works_with_good_custom_index(test_feature_adder):
    feature_id = test_feature_adder._generate_feature_id(category_id='A', custom_index_of_new_feature=130)
    assert feature_id == 'A-130'


def test__build_feature_id_generates_auto_index(test_feature_adder):
    feature_id = test_feature_adder._generate_feature_id(category_id='A', custom_index_of_new_feature=None)
    # note that there is a feature with ID A-211 in test file with features. Code must ignore this ID.
    assert feature_id == 'A-22'


def test_add_feature_writes_good_output_file(test_feature_adder):
    features_to_add = (
        {'category_id': 'A', 'feature_en': 'New feature in A', 'feature_ru': 'Новый признак в A'},
        {'category_id': 'C', 'feature_en': 'New feature in C', 'feature_ru': 'Новый признак в C'},
        {'category_id': 'D', 'feature_en': 'New feature in D with custom index', 'feature_ru': 'Новый признак в D',
         'index_of_new_feature': 415},
        {'category_id': 'N', 'feature_en': 'New feature in N with custom index in custom place',
         'feature_ru': 'Новый признак в N в указанной строке', 'index_of_new_feature': 201, 'index_to_add_after': 2},
    )

    for kwargs in features_to_add:
        test_feature_adder.add_feature(**kwargs, listed_values_to_add=dummy_values_to_add)

        # Re-wire output to input, otherwise the adder will just take the input file again
        # and only last feature will be added in the end:
        test_feature_adder.input_file_with_features = test_feature_adder.output_file_with_features
        # This is justified in test because in normal use output file is same as input file.

    assert test_feature_adder.output_file_with_features.exists()

    output_lines = read_csv(test_feature_adder.output_file_with_features, read_as='plain_rows')
    gold_standard_lines = read_csv(
        DIR_WITH_ADDERS_TEST_FILES / 'features_output_gold_standard.csv', read_as='plain_rows'
    )

    for output_line, gold_standard_line in zip(output_lines, gold_standard_lines):
        assert output_line == gold_standard_line

    test_feature_adder.output_file_with_features.unlink()
