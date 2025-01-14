from langworld_db_data.idtools.value_id_tools import (
    extract_feature_id,
    extract_value_index,
)

IDS_FOR_EXTRACTION = [
    'A-1-2',
    'A-1-22',
    'A-12-6',
    'A-12-26',
]
# add cases with different numbers of digits


def test_extract_feature_id():
    gold_standard = [
        'A-1',
        'A-1',
        'A-12',
        'A-12',
    ]
    for i in range(len(IDS_FOR_EXTRACTION)):
        assert extract_feature_id(IDS_FOR_EXTRACTION[i]) == gold_standard[i]


def test_extract_value_index():
    gold_standard = [2, 22, 6, 26]
    for i in range(len(IDS_FOR_EXTRACTION)):
        assert extract_value_index(IDS_FOR_EXTRACTION[i]) == gold_standard[i]
