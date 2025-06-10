from langworld_db_data.tools.common.ids import (
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
        ["A", "1", "2"],
        ["B", "7", "22"],
        ["C", "12", "6"],
        ["K", "14", "26"],
    )
    for id_to_gold_standard in zip(IDS_FOR_EXTRACTION, gold_standard):
        assert _split_value_id(id_to_gold_standard[0]) == id_to_gold_standard[1]


def test_extract_feature_id():
    gold_standard = (
        "A-1",
        "B-7",
        "C-12",
        "K-14",
    )
    for value_id_to_gold_standard in zip(IDS_FOR_EXTRACTION, gold_standard):
        assert extract_feature_id(value_id_to_gold_standard[0]) == value_id_to_gold_standard[1]


def test_extract_value_index():
    gold_standard = (2, 22, 6, 26)
    for value_id_to_gold_standard in zip(IDS_FOR_EXTRACTION, gold_standard):
        assert extract_value_index(value_id_to_gold_standard[0]) == value_id_to_gold_standard[1]


def test_extract_category_id():
    gold_standard = ("A", "B", "C", "K")
    for value_id_to_gold_standard in zip(IDS_FOR_EXTRACTION, gold_standard):
        assert extract_category_id(value_id_to_gold_standard[0]) == value_id_to_gold_standard[1]


def test_extract_feature_index():
    gold_standard = (1, 7, 12, 14)
    for value_id_to_gold_standard in zip(IDS_FOR_EXTRACTION, gold_standard):
        assert extract_feature_index(value_id_to_gold_standard[0]) == value_id_to_gold_standard[1]
