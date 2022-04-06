from langworld_db_data.markdown_generators.custom_value_lister import CustomValueLister
from langworld_db_data.markdown_generators.listed_value_lister import ListedValueLister
from langworld_db_data.validators.doculect_inventory_validator import DoculectInventoryValidator
from langworld_db_data.validators.feature_value_inventory_validator import FeatureValueInventoryValidator


def main():
    # These will also run during testing, but it doesn't hurt to check again
    DoculectInventoryValidator().validate()
    FeatureValueInventoryValidator().validate()

    print('\nWriting Markdown files')
    CustomValueLister().write_grouped_by_feature()
    CustomValueLister().write_grouped_by_volume_and_doculect()
    ListedValueLister().write_grouped_by_feature()


if __name__ == '__main__':
    main()
