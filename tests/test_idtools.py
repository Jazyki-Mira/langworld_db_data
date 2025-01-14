from langworld_db_data.idtools.value_id_tools import (extract_feature_id,
                                                      extract_value_index_as_int,
                                                      extract_value_index_as_str,
                                                      )


ID_FOR_EXTRACTION = 'A-12-6'


def test_extract_feature_id():
    assert extract_feature_id(ID_FOR_EXTRACTION) == 'A-12'


def test_extract_value_index_as_str():
    assert extract_value_index_as_str(ID_FOR_EXTRACTION) == '6'


def test_extract_value_index_as_int():
    assert extract_value_index_as_int(ID_FOR_EXTRACTION) == 6
