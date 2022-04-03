from pathlib import Path

DIR_WITH_TEST_FILES = Path(__file__).parent / 'test_data'

DIR_WITH_FILETOOLS_TEST_FILES = DIR_WITH_TEST_FILES / 'filetools'
PATH_TO_TEST_OUTPUT_TXT_FILE = DIR_WITH_FILETOOLS_TEST_FILES / 'test_file_write.txt'
PATH_TO_TEST_OUTPUT_CSV_FILE = DIR_WITH_FILETOOLS_TEST_FILES / 'test_file_write.csv'

DIR_WITH_VALIDATORS_TEST_FILES = DIR_WITH_TEST_FILES / 'validators'
