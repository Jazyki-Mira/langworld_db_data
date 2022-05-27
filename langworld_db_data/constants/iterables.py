from langworld_db_data.constants.paths import FEATURE_PROFILES_DIR

# tuple to make it immutable and hence suitable for a constant
FEATURE_PROFILES = tuple(sorted(list(FEATURE_PROFILES_DIR.glob('*.csv'))))
