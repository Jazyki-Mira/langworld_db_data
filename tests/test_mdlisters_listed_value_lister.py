from langworld_db_data.mdlisters.listed_value_lister import ListedValueLister
from tests.paths import DIR_WITH_TEST_FEATURE_PROFILES, DIR_WITH_VALIDATORS_TEST_FILES


def test_write_grouped_by_feature():
    lister = ListedValueLister(dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES)

    output_file = DIR_WITH_VALIDATORS_TEST_FILES / 'listed_values_by_feature.md'
    gold_standard_file = DIR_WITH_VALIDATORS_TEST_FILES / 'listed_values_by_feature_sample.md'

    lister.write_grouped_by_feature(output_file=output_file)
    assert output_file.exists()

    with gold_standard_file.open(mode='r', encoding='utf-8') as fh:
        gold_content = fh.read()
    with output_file.open(mode='r', encoding='utf-8') as fh:
        test_content = fh.read()

    assert gold_content == test_content
    output_file.unlink()
