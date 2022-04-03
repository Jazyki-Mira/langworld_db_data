from langworld_db_data.validators.custom_value_lister import CustomValueLister
from tests.paths import DIR_WITH_TEST_FILES

DIR_WITH_VALIDATOR_TEST_FILES = DIR_WITH_TEST_FILES / 'validators'

# Note that 'agul.csv' does not contain any custom values.  It is just there to make sure
# there are no errors with files that have no custom values.
cvl = CustomValueLister(dir_with_feature_profiles=DIR_WITH_VALIDATOR_TEST_FILES / 'feature_profiles')


def test_write_grouped_by_volume_and_doculect():
    output_file = DIR_WITH_VALIDATOR_TEST_FILES / 'custom_values_by_volume_and_doculect.md'
    gold_standard_file = DIR_WITH_VALIDATOR_TEST_FILES / 'custom_values_by_volume_and_doculect_sample.md'

    cvl.write_grouped_by_volume_and_doculect(output_file=output_file)
    assert output_file.exists()

    with gold_standard_file.open(mode='r', encoding='utf-8') as fh:
        gold_content = fh.read()
    with output_file.open(mode='r', encoding='utf-8') as fh:
        test_content = fh.read()

    assert gold_content == test_content
    output_file.unlink()


def test_write_grouped_by_feature():
    output_file = DIR_WITH_VALIDATOR_TEST_FILES / 'custom_values_by_feature.md'
    gold_standard_file = DIR_WITH_VALIDATOR_TEST_FILES / 'custom_values_by_feature_sample.md'

    cvl.write_grouped_by_feature(output_file=output_file)
    assert output_file.exists()

    with gold_standard_file.open(mode='r', encoding='utf-8') as fh:
        gold_content = fh.read()
    with output_file.open(mode='r', encoding='utf-8') as fh:
        test_content = fh.read()

    assert gold_content == test_content
    output_file.unlink()

