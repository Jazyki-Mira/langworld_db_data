from pathlib import Path

MAIN_DIR = Path(__file__).parent.parent.parent
DATA_DIR = MAIN_DIR / 'data'

CLDF_DIR = DATA_DIR / 'cldf'
FILE_WITH_CLDF_DATASET_METADATA = CLDF_DIR / 'StructureDataset-metadata.json'

DISCUSSION_DIR = DATA_DIR / 'discussion'
DISCUSSION_FILE_WITH_CUSTOM_VALUES_BY_DOCULECT = DISCUSSION_DIR / 'custom_values_by_volume_and_doculect.md'
DISCUSSION_FILE_WITH_CUSTOM_VALUES_BY_FEATURE = DISCUSSION_DIR / 'custom_values_by_feature.md'
DISCUSSION_FILE_WITH_LISTED_VALUES = DISCUSSION_DIR / 'listed_values_by_feature.md'

INVENTORIES_DIR = DATA_DIR / 'inventories'
FILE_WITH_CATEGORIES = INVENTORIES_DIR / 'feature_categories.csv'
FILE_WITH_DOCULECTS = INVENTORIES_DIR / 'doculects.csv'
FILE_WITH_NAMES_OF_FEATURES = INVENTORIES_DIR / 'features.csv'
FILE_WITH_LISTED_VALUES = INVENTORIES_DIR / 'features_listed_values.csv'

FEATURE_PROFILES_DIR = DATA_DIR / 'feature_profiles'
SOCIOLINGUISTIC_PROFILES_DIR = DATA_DIR / 'sociolinguistic_profiles'

if __name__ == '__main__':
    pass
