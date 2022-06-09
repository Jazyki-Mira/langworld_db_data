from pycldf import Dataset

from langworld_db_data.cldfwriters.cldf_dataset_writer import CLDFDatasetWriter
from langworld_db_data.filetools.csv_xls import check_csv_for_malformed_rows
from langworld_db_data.filetools.json_toml_yaml import check_yaml_file
from langworld_db_data.constants.paths import DATA_DIR, FILE_WITH_CLDF_DATASET_METADATA
from langworld_db_data.mdlisters.custom_value_lister import CustomValueLister
from langworld_db_data.mdlisters.listed_value_lister import ListedValueLister
from langworld_db_data.validators.asset_validator import AssetValidator
from langworld_db_data.validators.doculect_inventory_validator import DoculectInventoryValidator
from langworld_db_data.validators.feature_profile_validator import FeatureProfileValidator
from langworld_db_data.validators.feature_value_inventory_validator import FeatureValueInventoryValidator
from langworld_db_data.validators.genealogy_validator import GenealogyValidator


def main():
    print('\nRunning general checks of CSV and YAML files')

    print('Checking YAML files')
    for file in DATA_DIR.rglob('*.yaml'):
        check_yaml_file(file, verbose=False)

    print('Checking CSV files for malformed rows')
    for file in DATA_DIR.rglob('*.csv'):
        check_csv_for_malformed_rows(file)
    # Check for uniqueness in columns cannot be done universally, it depends on a specific file

    print('OK: General checks passed')

    # These will also run during testing, but it doesn't hurt to check again
    AssetValidator().validate()
    DoculectInventoryValidator().validate()
    GenealogyValidator().validate()
    FeatureValueInventoryValidator().validate()
    # Strict mode triggers exception if value name does not match value name in an inventory for given value ID.
    # Since value name in feature profile is only there for readability, I could disable strict mode
    # at later stages of the project (when I am sure that a mismatch can only be caused by planned renaming
    # of a value  in the inventory).
    FeatureProfileValidator(
        must_raise_exception_at_value_name_mismatch=True,
        must_raise_exception_at_not_applicable_rule_breach=False,  # can set to True when existing profiles are amended
    ).validate()

    print('\nWriting Markdown files')
    CustomValueLister().write_grouped_by_feature()
    CustomValueLister().write_grouped_by_volume_and_doculect()
    ListedValueLister().write_grouped_by_feature()

    print('\nWriting CLDF')
    CLDFDatasetWriter().write()

    print('\nValidating CLDF')
    Dataset.from_metadata(FILE_WITH_CLDF_DATASET_METADATA).validate()


if __name__ == '__main__':
    main()
