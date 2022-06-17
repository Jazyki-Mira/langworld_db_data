from pathlib import Path

MAIN_DIR = Path(__file__).parent.parent.parent
DATA_DIR = MAIN_DIR / 'data'

CLDF_DIR = DATA_DIR / 'cldf'
FILE_WITH_CLDF_DATASET_METADATA = CLDF_DIR / 'StructureDataset-metadata.json'

DISCUSSION_DIR = DATA_DIR / 'discussion'
DISCUSSION_FILE_WITH_CUSTOM_VALUES_BY_DOCULECT = DISCUSSION_DIR / 'custom_values_by_volume_and_doculect.md'
DISCUSSION_FILE_WITH_CUSTOM_VALUES_BY_FEATURE = DISCUSSION_DIR / 'custom_values_by_feature.md'
DISCUSSION_FILE_WITH_LISTED_VALUES = DISCUSSION_DIR / 'listed_values_by_feature.md'

ASSETS_DIR = DATA_DIR / 'assets'
FILE_WITH_MAP_TO_DOCULECT = ASSETS_DIR / 'encyclopedia_map_to_doculect.csv'
FILE_WITH_MAPS = ASSETS_DIR / 'encyclopedia_maps.csv'
FILE_WITH_ENCYCLOPEDIA_VOLUMES = ASSETS_DIR / 'encyclopedia_volumes.csv'

INVENTORIES_DIR = DATA_DIR / 'inventories'
FILE_WITH_COUNTRIES = INVENTORIES_DIR / 'countries.csv'
FILE_WITH_CATEGORIES = INVENTORIES_DIR / 'feature_categories.csv'
FILE_WITH_DOCULECTS = INVENTORIES_DIR / 'doculects.csv'
FILE_WITH_NAMES_OF_FEATURES = INVENTORIES_DIR / 'features.csv'
FILE_WITH_LISTED_VALUES = INVENTORIES_DIR / 'features_listed_values.csv'
FILE_WITH_NOT_APPLICABLE_RULES = INVENTORIES_DIR / 'features_not_applicable_rules.yaml'
FILE_WITH_GENEALOGY_HIERARCHY = INVENTORIES_DIR / 'genealogy_families_hierarchy.yaml'
FILE_WITH_GENEALOGY_NAMES = INVENTORIES_DIR / 'genealogy_families_names.csv'

FEATURE_PROFILES_DIR = DATA_DIR / 'feature_profiles'

SOCIOLINGUISTIC_DIR = DATA_DIR / 'sociolinguistics'
SOCIOLINGUISTIC_PROFILES_DIR = SOCIOLINGUISTIC_DIR / 'sociolinguistic_profiles'
FILE_WITH_COUNTRY_ALIASES = SOCIOLINGUISTIC_DIR / 'country_aliases_for_profile_parsing.csv'
FILE_WITH_DOCULECTS_MATCHED_TO_COUNTRIES = SOCIOLINGUISTIC_DIR / 'doculects_to_countries.csv'


if __name__ == '__main__':
    pass
