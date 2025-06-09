from langworld_db_data.tools.files.csv_xls import remove_matching_rows
from langworld_db_data.tools.ids.update import update_indices_after_given_line_number_if_necessary


def test_update_indices_after_given_line_number_if_necessary_in_features_update_is_necessary(
    dummy_rows_of_features,
):

    GOLD_STANDARD_DUMMY_ROWS = [
        {
            "id": "A-1",
            "en": "Subject",
            "ru": "Подлежащее",
        },
        {
            "id": "A-2",
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
    ]

    rows_without_A_2, (line_number_of_removed_row,) = remove_matching_rows(
        lookup_column="id",
        match_content="A-2",
        rows=dummy_rows_of_features,
    )

    rows_without_A_2_with_updated_feature_indices = (
        update_indices_after_given_line_number_if_necessary(
            lookup_column="id",
            match_content="A",
            id_type_that_must_be_updated="feature",
            line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
            index_type_that_must_be_updated="feature",
            rows=rows_without_A_2,
        )
    )

    assert rows_without_A_2_with_updated_feature_indices == GOLD_STANDARD_DUMMY_ROWS


def test_update_indices_after_given_line_number_if_necessary_in_features_update_is_not_necessary(
    dummy_rows_of_features,
):

    GOLD_STANDARD_DUMMY_ROWS = [
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
    ]

    rows_without_last_feature_in_category_A, (line_number_of_removed_row,) = remove_matching_rows(
        lookup_column="id",
        match_content="A-3",
        rows=dummy_rows_of_features,
    )

    rows_without_last_feature_in_category_A_with_updated_feature_indices = (
        update_indices_after_given_line_number_if_necessary(
            lookup_column="id",
            match_content="A",
            id_type_that_must_be_updated="feature",
            line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
            index_type_that_must_be_updated="feature",
            rows=rows_without_last_feature_in_category_A,
        )
    )

    assert (
        rows_without_last_feature_in_category_A_with_updated_feature_indices
        == GOLD_STANDARD_DUMMY_ROWS
    )


def test_update_indices_after_given_line_number_if_necessary_in_listed_values_update_is_necessary(
    dummy_rows_of_listed_values,
):

    GOLD_STANDARD_DUMMY_ROWS = [
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
            "en": "Coordination",
            "ru": "Координация",
        },
    ]

    rows_without_B_1, range_of_line_numbers_of_removed_rows = remove_matching_rows(
        lookup_column="feature_id",
        match_content="B-1",
        rows=dummy_rows_of_listed_values,
    )

    line_number_of_first_removed_value = range_of_line_numbers_of_removed_rows[0]

    rows_without_B_1_with_updated_value_indices = (
        update_indices_after_given_line_number_if_necessary(
            lookup_column="id",
            match_content="B",
            id_type_that_must_be_updated="value",
            index_type_that_must_be_updated="feature",
            line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
            rows=rows_without_B_1,
        )
    )

    rows_without_B_1_with_updated_feature_and_value_indices = (
        update_indices_after_given_line_number_if_necessary(
            lookup_column="feature_id",
            match_content="B",
            id_type_that_must_be_updated="feature",
            index_type_that_must_be_updated="feature",
            line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
            rows=rows_without_B_1_with_updated_value_indices,
        )
    )

    assert rows_without_B_1_with_updated_feature_and_value_indices == GOLD_STANDARD_DUMMY_ROWS


def test_update_indices_after_given_line_number_if_necessary_in_listed_values_update_is_not_necessary(
    dummy_rows_of_listed_values,
):

    GOLD_STANDARD_DUMMY_ROWS = [
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
    ]

    rows_without_B_2, range_of_line_numbers_of_removed_rows = remove_matching_rows(
        lookup_column="feature_id",
        match_content="B-2",
        rows=dummy_rows_of_listed_values,
    )

    line_number_of_first_removed_value = range_of_line_numbers_of_removed_rows[0]

    rows_without_B_2_with_updated_value_indices = (
        update_indices_after_given_line_number_if_necessary(
            lookup_column="id",
            match_content="B",
            id_type_that_must_be_updated="value",
            index_type_that_must_be_updated="feature",
            line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
            rows=rows_without_B_2,
        )
    )

    rows_without_B_2_with_updated_feature_and_value_indices = (
        update_indices_after_given_line_number_if_necessary(
            lookup_column="feature_id",
            match_content="B",
            id_type_that_must_be_updated="feature",
            index_type_that_must_be_updated="feature",
            line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
            rows=rows_without_B_2_with_updated_value_indices,
        )
    )

    assert rows_without_B_2_with_updated_feature_and_value_indices == GOLD_STANDARD_DUMMY_ROWS


def test_update_indices_after_given_line_number_if_necessary_in_feature_profile_update_is_necessary(
    dummy_rows_of_feature_profile,
):

    GOLD_STANDARD_DUMMY_ROWS = [
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
            "value_id": "A-2-3",
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
    ]

    rows_without_A_2, (line_number_of_removed_row,) = remove_matching_rows(
        lookup_column="feature_id",
        match_content="A-2",
        rows=dummy_rows_of_feature_profile,
    )

    rows_without_A_2_with_updated_feature_indices = (
        update_indices_after_given_line_number_if_necessary(
            lookup_column="feature_id",
            match_content="A",
            id_type_that_must_be_updated="feature",
            line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
            index_type_that_must_be_updated="feature",
            rows=rows_without_A_2,
            rows_are_a_feature_profile=True,
        )
    )

    for row in rows_without_A_2_with_updated_feature_indices:
        print(row)

    assert rows_without_A_2_with_updated_feature_indices == GOLD_STANDARD_DUMMY_ROWS


def test_update_indices_after_given_line_number_if_necessary_in_feature_profile_update_is_not_necessary(
    dummy_rows_of_feature_profile,
):

    GOLD_STANDARD_DUMMY_ROWS = [
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
    ]

    rows_without_last_feature_in_category_A, (line_number_of_removed_row,) = remove_matching_rows(
        lookup_column="feature_id",
        match_content="A-3",
        rows=dummy_rows_of_feature_profile,
    )

    rows_without_last_feature_in_category_A_with_updated_feature_indices = (
        update_indices_after_given_line_number_if_necessary(
            lookup_column="feature_id",
            match_content="A",
            id_type_that_must_be_updated="feature",
            line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
            index_type_that_must_be_updated="feature",
            rows=rows_without_last_feature_in_category_A,
            rows_are_a_feature_profile=True,
        )
    )

    assert (
        rows_without_last_feature_in_category_A_with_updated_feature_indices
        == GOLD_STANDARD_DUMMY_ROWS
    )
