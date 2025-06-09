import pytest


@pytest.fixture(scope="function")
def dummy_rows_of_features():
    return (
        {
            "id": "A-1",
            "en": "Subject",
            "ru": "Подлежащее",
        },
        {
            "id": "A-2",
            "en": "Object",
            "ru": "Прямое дополнение",
        },
        {
            "id": "A-3",
            "en": "Predicate",
            "ru": "Сказуемое",
        },
        {
            "id": "B-1",
            "en": "Collocation",
            "ru": "Коллокация",
        },
        {
            "id": "B-2",
            "en": "Grammatical core",
            "ru": "Грамматическая основа",
        },
        {
            "id": "С-1",
            "en": "Sentence",
            "ru": "Предложение",
        },
    )


@pytest.fixture(scope="function")
def dummy_rows_of_listed_values():
    return (
        {
            "id": "A-1-1",
            "feature_id": "A-1",
            "en": "Nominative",
            "ru": "Номинатив",
        },
        {
            "id": "A-1-2",
            "feature_id": "A-1",
            "en": "Ergative",
            "ru": "Эргатив",
        },
        {
            "id": "A-1-3",
            "feature_id": "A-1",
            "en": "DSM",
            "ru": "Дифференцированное маркирование субъекта",
        },
        {
            "id": "B-1-1",
            "feature_id": "B-1",
            "en": "Agreement",
            "ru": "Согласование",
        },
        {
            "id": "B-1-2",
            "feature_id": "B-1",
            "en": "Word order",
            "ru": "Порядок слов",
        },
        {
            "id": "B-2-1",
            "feature_id": "B-2",
            "en": "Coordination",
            "ru": "Координация",
        },
    )


@pytest.fixture(scope="function")
def dummy_rows_of_feature_profile():
    return (
        {
            "feature_id": "A-1",
            "feature_name_ru": "Некий признак",
            "value_type": "listed",
            "value_id": "A-1-1",
        },
        {
            "feature_id": "A-2",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-2-2",
        },
        {
            "feature_id": "A-3",
            "feature_name_ru": "Еще один признак",
            "value_type": "listed",
            "value_id": "A-3-3",
        },
        {
            "feature_id": "B-1",
            "feature_name_ru": "Четвертый признак",
            "value_type": "listed",
            "value_id": "B-1-1",
        },
        {
            "feature_id": "C-1",
            "feature_name_ru": "И еще признак",
            "value_type": "listed",
            "value_id": "C-1-1",
        },
    )


@pytest.fixture(scope="function")
def dummy_rows_with_scattered_values():
    return (
        {
            "id": "17",
            "domain": "morphology",
            "type": "constant",
        },
        {
            "id": "18",
            "domain": "morphology",
            "type": "variable",
        },
        {
            "id": "19",
            "domain": "syntax",
            "type": "constant",
        },
        {
            "id": "20",
            "domain": "syntax",
            "type": "constant",
        },
        {
            "id": "21",
            "domain": "syntax",
            "type": "variable",
        },
        {
            "id": "22",
            "domain": "morphology",
            "type": "constant",
        },
    )
