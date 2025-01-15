from langworld_db_data.idtools.value_id_tools import (
    _split_value_id,
    extract_category_id,
    extract_feature_id,
    extract_feature_index,
    extract_value_index,
)

IDS_FOR_EXTRACTION = (
    "A-1-2",
    "B-7-22",
    "C-12-6",
    "K-14-26",
)


def test__split_value_id():
    gold_standard = (
        ("A", "1", "2"),
        ("B", "7", "22"),
        ("C", "12", "6"),
        ("K", "14", "26"),
    )
    for i in range(len(IDS_FOR_EXTRACTION)):
        assert _split_value_id(IDS_FOR_EXTRACTION[i]) == gold_standard[i]


def test_extract_feature_id():
    gold_standard = (
        "A-1",
        "B-7",
        "C-12",
        "K-14",
    )
    for i in range(len(IDS_FOR_EXTRACTION)):
        assert extract_feature_id(IDS_FOR_EXTRACTION[i]) == gold_standard[i]


def test_extract_value_index():
    gold_standard = (2, 22, 6, 26)
    for i in range(len(IDS_FOR_EXTRACTION)):
        assert extract_value_index(IDS_FOR_EXTRACTION[i]) == gold_standard[i]


def test_extract_category_id():
    gold_standard = ("A", "B", "C", "K")
    for i in range(len(IDS_FOR_EXTRACTION)):
        assert extract_category_id(IDS_FOR_EXTRACTION[i]) == gold_standard[i]


def test_extract_feature_index():
    gold_standard = (1, 7, 12, 14)
    for i in range(len(IDS_FOR_EXTRACTION)):
        assert extract_feature_index(IDS_FOR_EXTRACTION[i]) == gold_standard[i]
