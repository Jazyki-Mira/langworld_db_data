import pytest

from langworld_db_data.featureprofiletools.data_structures import (
    ValueForFeatureProfileDictionary,
)
from langworld_db_data.featureprofiletools.feature_profile_writer_from_dictionary import (
    FeatureProfileWriterFromDictionary,
)
from tests.helpers import (
    check_existence_of_output_csv_file_and_compare_with_gold_standard,
)
from tests.paths import DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES


@pytest.fixture(scope="function")
def test_writer():
    return FeatureProfileWriterFromDictionary()


def test_write(test_writer):
    output_file = (
        DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES / "catalan_short_writer_output.csv"
    )

    test_writer.write(
        feature_dict={
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
            "_aux": ValueForFeatureProfileDictionary(
                feature_name_ru="",
                value_type="not_applicable",
                value_id="",
                value_ru="",
                comment_ru="И.И.Иванов",
                comment_en="",
                page_numbers="",
            ),
        },
        output_path=output_file,
    )

    check_existence_of_output_csv_file_and_compare_with_gold_standard(
        output_file=output_file,
        gold_standard_file=DIR_WITH_FEATURE_PROFILE_TOOLS_TEST_FILES
        / "catalan_short_benchmark_for_writer.csv",
    )
