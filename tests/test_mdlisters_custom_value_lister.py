from langworld_db_data.mdlisters.custom_value_lister import CustomValueLister
from tests.paths import DIR_WITH_TEST_FEATURE_PROFILES, DIR_WITH_VALIDATORS_TEST_FILES

# Note that 'agul.csv' does not contain any custom values.
# It is there to make sure there are no errors with files that have no custom values.
cvl = CustomValueLister(dir_with_feature_profiles=DIR_WITH_TEST_FEATURE_PROFILES)


def test_write_grouped_by_volume_and_doculect():
    output_file = DIR_WITH_VALIDATORS_TEST_FILES / "custom_values_by_volume_and_doculect_sample.md"
    gold_standard_file = (
        DIR_WITH_VALIDATORS_TEST_FILES / "custom_values_by_volume_and_doculect_sample.md"
    )

    cvl.write_grouped_by_volume_and_doculect(output_file=output_file)
    assert output_file.exists()

    with gold_standard_file.open(encoding="utf-8") as fh:
        gold_content = fh.read()
    with output_file.open(encoding="utf-8") as fh:
        test_content = fh.read()

    assert gold_content == test_content
    output_file.unlink()


def test_write_grouped_by_feature():
    output_file = DIR_WITH_VALIDATORS_TEST_FILES / "custom_values_by_feature.md"
    gold_standard_file = DIR_WITH_VALIDATORS_TEST_FILES / "custom_values_by_feature_sample.md"

    cvl.write_grouped_by_feature(output_file=output_file)
    assert output_file.exists()

    with gold_standard_file.open(encoding="utf-8") as fh:
        gold_content = fh.read()
    with output_file.open(encoding="utf-8") as fh:
        test_content = fh.read()

    assert gold_content == test_content
    output_file.unlink()
