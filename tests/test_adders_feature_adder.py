import pytest

from langworld_db_data.adders.feature_adder import FeatureAdder, FeatureAdderError
from tests.helpers import (
    check_existence_of_output_csv_file_and_compare_with_gold_standard,
)
from tests.paths import (
    DIR_WITH_ADDERS_TEST_FILES,
    DIR_WITH_ADDERS_FEATURE_PROFILES,
    INPUT_FILE_WITH_LISTED_VALUES,
    OUTPUT_DIR_FOR_FEATURE_ADDER_FEATURE_PROFILES,
)

dummy_values_to_add = [
    {"ru": "Одно явление", "en": "One thing"},
    {"ru": "Одно, два и третье", "en": "One thing, second thing, and third thing"},
]


@pytest.fixture(scope="function")
def test_feature_adder():
    return FeatureAdder(
        file_with_categories=DIR_WITH_ADDERS_TEST_FILES / "feature_categories.csv",
        input_file_with_features=DIR_WITH_ADDERS_TEST_FILES / "features.csv",
        output_file_with_features=DIR_WITH_ADDERS_TEST_FILES / "features_output.csv",
        input_file_with_listed_values=INPUT_FILE_WITH_LISTED_VALUES,
        output_file_with_listed_values=DIR_WITH_ADDERS_TEST_FILES
        / "features_listed_values_output_feature_adder.csv",
        input_dir_with_feature_profiles=DIR_WITH_ADDERS_FEATURE_PROFILES,
        output_dir_with_feature_profiles=OUTPUT_DIR_FOR_FEATURE_ADDER_FEATURE_PROFILES,
    )


def test_add_feature_fails_with_empty_arg(test_feature_adder):
    for incomplete_set_of_args in (
        {
            "category_id": "",
            "feature_ru": "раз",
            "feature_en": "one",
            "listed_values_to_add": dummy_values_to_add,
        },
        {
            "category_id": "A",
            "feature_ru": "",
            "feature_en": "one",
            "listed_values_to_add": dummy_values_to_add,
        },
        {
            "category_id": "A",
            "feature_ru": "раз",
            "feature_en": "",
            "listed_values_to_add": dummy_values_to_add,
        },
        {
            "category_id": "A",
            "feature_ru": "раз",
            "feature_en": "one",
            "listed_values_to_add": [],
        },
    ):
        with pytest.raises(
            FeatureAdderError, match="Some of the values passed are empty"
        ):
            test_feature_adder.add_feature(**incomplete_set_of_args)


def test_add_feature_fails_with_wrong_new_listed_values(test_feature_adder):
    args = {
        "category_id": "A",
        "feature_ru": "раз",
        "feature_en": "one",
        "listed_values_to_add": [
            {"ru": "раз", "en": "this is fine"},
            {"this": "should fail", "en": "this is fine"},
        ],
    }
    with pytest.raises(
        FeatureAdderError,
        match=(
            "must have keys 'en' and 'ru'. Your value: {'this': 'should fail', 'en':"
            " 'this is fine'}"
        ),
    ):
        test_feature_adder.add_feature(**args)


def test_add_feature_fails_with_wrong_category_id(test_feature_adder):
    with pytest.raises(
        FeatureAdderError,
        match=(
            "Category ID <X> not found in file"
            f" {test_feature_adder.file_with_categories.name}"
        ),
    ):
        test_feature_adder.add_feature(
            category_id="X",
            feature_ru="имя",
            feature_en="name",
            listed_values_to_add=dummy_values_to_add,
        )


def test_add_feature_fails_with_existing_feature_name(test_feature_adder):
    for en, ru in (
        ("Stress character ", "Новый признак"),
        ("New  feature", "Типы фонации"),
    ):
        with pytest.raises(
            FeatureAdderError, match="English or Russian feature name is already"
        ):
            test_feature_adder.add_feature(
                category_id="A",
                feature_en=en,
                feature_ru=ru,
                listed_values_to_add=dummy_values_to_add,
            )


def test_add_feature_fails_with_non_existent_index_of_feature_to_insert_after(
    test_feature_adder,
):
    for number in (0, 22, 250):
        with pytest.raises(
            FeatureAdderError, match=f"Cannot add feature after A-{number}"
        ):
            test_feature_adder.add_feature(
                category_id="A",
                feature_en="Foo",
                feature_ru="Фу",
                listed_values_to_add=dummy_values_to_add,
                insert_after_index=number,
            )


def test__build_feature_id_fails_with_existing_index(test_feature_adder):
    with pytest.raises(
        FeatureAdderError, match="Feature index 211 already in use in category A"
    ):
        test_feature_adder._generate_feature_id(
            category_id="A", custom_index_of_new_feature=211
        )


def test__build_feature_id_fails_with_small_index(test_feature_adder):
    with pytest.raises(FeatureAdderError, match="must be greater than 100"):
        test_feature_adder._generate_feature_id(
            category_id="A", custom_index_of_new_feature=99
        )


def test__build_feature_id_works_with_good_custom_index(test_feature_adder):
    feature_id = test_feature_adder._generate_feature_id(
        category_id="A", custom_index_of_new_feature=130
    )
    assert feature_id == "A-130"


def test__build_feature_id_generates_auto_index(test_feature_adder):
    feature_id = test_feature_adder._generate_feature_id(
        category_id="A", custom_index_of_new_feature=None
    )
    # note that there is a feature with ID A-211 in test file with features. Code must ignore this ID.
    assert feature_id == "A-22"


def test_add_feature_writes_good_output_files(test_feature_adder):
    features_to_add = (
        {
            "category_id": "A",
            "feature_en": "New feature in A",
            "feature_ru": "Новый признак в A",
        },
        {
            "category_id": "C",
            "feature_en": "New feature in C",
            "feature_ru": "Новый признак в C",
        },
        {
            "category_id": "D",
            "feature_en": "New feature in D with custom index",
            "feature_ru": "Новый признак в D",
            "index_of_new_feature": 415,
        },
        {
            "category_id": "N",
            "feature_en": "New feature in N with custom index in custom place",
            "feature_ru": "Новый признак в N в указанной строке",
            "index_of_new_feature": 201,
            "insert_after_index": 2,
        },
        # adding to the very end of file (with custom index):
        {
            "category_id": "N",
            "feature_en": "New feature in N inserted after 5",
            "feature_ru": "Новый признак N после 5",
            "insert_after_index": 5,
        },
        # adding to the very end of file:
        {
            "category_id": "N",
            "feature_en": "New feature in N (in the very end)",
            "feature_ru": "Новый признак N конец",
        },
    )

    for kwargs in features_to_add:
        test_feature_adder.add_feature(
            **kwargs, listed_values_to_add=dummy_values_to_add
        )

        # Re-wire output to input after addition of first feature,
        # otherwise the adder will just take the input file again
        # and only last feature will be added in the end:
        test_feature_adder.input_file_with_features = (
            test_feature_adder.output_file_with_features
        )
        test_feature_adder.input_file_with_listed_values = (
            test_feature_adder.output_file_with_listed_values
        )
        test_feature_adder.input_feature_profiles = (
            test_feature_adder.output_dir_with_feature_profiles.glob("*.csv")
        )
        # This is justified in test because in normal use output file is same as input file
        # and features will be added one by one.

    assert test_feature_adder.output_file_with_features.exists()
    assert test_feature_adder.input_file_with_listed_values.exists()

    gold_standard_feature_profiles = list(
        (OUTPUT_DIR_FOR_FEATURE_ADDER_FEATURE_PROFILES / "gold_standard").glob("*.csv")
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_features,
        gold_standard_file=DIR_WITH_ADDERS_TEST_FILES
        / "features_gold_standard_after_addition.csv",
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=test_feature_adder.output_file_with_listed_values,
        gold_standard_file=DIR_WITH_ADDERS_TEST_FILES
        / "features_listed_values_gold_standard_for_feature_adder.csv",
    )

    for file in gold_standard_feature_profiles:
        test_output_file = (
            test_feature_adder.output_dir_with_feature_profiles / file.name
        )

        check_existence_of_output_csv_file_and_compare_with_gold_standard(
            output_file=test_output_file,
            gold_standard_file=file,
        )
