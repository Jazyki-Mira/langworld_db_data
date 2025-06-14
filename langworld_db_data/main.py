from pycldf import Dataset

from langworld_db_data.constants.paths import DATA_DIR, FILE_WITH_CLDF_DATASET_METADATA
from langworld_db_data.export.cldf_dataset_writer import CLDFDatasetWriter
from langworld_db_data.mdlisters.custom_value_lister import CustomValueLister
from langworld_db_data.mdlisters.listed_value_lister import ListedValueLister
from langworld_db_data.tools.common.files.csv_xls import check_csv_for_malformed_rows
from langworld_db_data.tools.common.files.json_toml_yaml import check_yaml_file
from langworld_db_data.validators.asset_validator import AssetValidator
from langworld_db_data.validators.doculect_inventory_validator import DoculectInventoryValidator
from langworld_db_data.validators.feature_profile_validator import FeatureProfileValidator
from langworld_db_data.validators.feature_value_inventory_validator import (
    FeatureValueInventoryValidator,
)
from langworld_db_data.validators.genealogy_validator import GenealogyValidator
from langworld_db_data.validators.html_validator import HTMLValidator


def main() -> None:
    print("\nRunning general checks of CSV and YAML files")

    print("Checking YAML files")
    for file in DATA_DIR.rglob("*.yaml"):
        check_yaml_file(file, verbose=False)

    print("Checking CSV files for malformed rows")
    for file in DATA_DIR.rglob("*.csv"):
        check_csv_for_malformed_rows(file)
    # Check for uniqueness in columns cannot be done universally, it depends on a
    # specific file

    print("OK: General checks passed")

    # These will also run during testing, but it doesn't hurt to check again
    AssetValidator().validate()
    DoculectInventoryValidator().validate()
    GenealogyValidator().validate()
    FeatureValueInventoryValidator().validate()
    HTMLValidator().validate()
    FeatureProfileValidator().validate()
    # In this last validator, exception will be thrown if value name does not match
    # value name in an inventory for given value ID.
    # Value name in feature profile is only there for readability, so this behavior
    # is not required, but for now it seems OK for the exception to be thrown.
    # In an opposite way, rules for `not_applicable` are not strictly enforced yet.
    # Argument `must_throw_error_at_not_applicable_rule_breach`
    # can be set to True at a later stage.

    print("\nWriting Markdown files")
    CustomValueLister().write_grouped_by_feature()
    CustomValueLister().write_grouped_by_volume_and_doculect()
    ListedValueLister().write_grouped_by_feature()

    print("\nWriting CLDF")
    CLDFDatasetWriter().write()

    print("\nValidating CLDF")
    Dataset.from_metadata(FILE_WITH_CLDF_DATASET_METADATA).validate()


if __name__ == "__main__":
    main()
