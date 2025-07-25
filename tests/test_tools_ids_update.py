from tinybear.csv_xls import (
    remove_rows_with_given_content_in_lookup_column,
)

from langworld_db_data.tools.common.ids import decrement_indices_after_deletion


def test_decrement_indices_after_deletion_in_features_update_is_necessary(
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
            "id": "C-1",
            "en": "Sentence",
            "ru": "Предложение",
        },
    ]

    rows_without_A_2, (line_number_of_removed_row,) = (
        remove_rows_with_given_content_in_lookup_column(
            lookup_column="id",
            match_value="A-2",
            rows=dummy_rows_of_features,
        )
    )

    rows_without_A_2_with_updated_feature_indices = decrement_indices_after_deletion(
        lookup_column="id",
        match_value="A",
        type_of_id="feature",
        line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
        type_of_index="feature",
        rows=rows_without_A_2,
    )

    assert rows_without_A_2_with_updated_feature_indices == GOLD_STANDARD_DUMMY_ROWS


def test_decrement_indices_after_deletion_in_features_update_is_not_necessary(
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
            "id": "C-1",
            "en": "Sentence",
            "ru": "Предложение",
        },
    ]

    rows_without_last_feature_in_category_A, (line_number_of_removed_row,) = (
        remove_rows_with_given_content_in_lookup_column(
            lookup_column="id",
            match_value="A-3",
            rows=dummy_rows_of_features,
        )
    )

    rows_without_last_feature_in_category_A_with_updated_feature_indices = (
        decrement_indices_after_deletion(
            lookup_column="id",
            match_value="A",
            type_of_id="feature",
            line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
            type_of_index="feature",
            rows=rows_without_last_feature_in_category_A,
        )
    )

    assert (
        rows_without_last_feature_in_category_A_with_updated_feature_indices
        == GOLD_STANDARD_DUMMY_ROWS
    )


def test_decrement_indices_after_deletion_of_feature_in_listed_values_update_is_necessary(
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

    rows_without_B_1, range_of_line_numbers_of_removed_rows = (
        remove_rows_with_given_content_in_lookup_column(
            lookup_column="feature_id",
            match_value="B-1",
            rows=dummy_rows_of_listed_values,
        )
    )

    line_number_of_first_removed_value = range_of_line_numbers_of_removed_rows[0]

    rows_without_B_1_with_updated_value_indices = decrement_indices_after_deletion(
        lookup_column="id",
        match_value="B",
        type_of_id="value",
        type_of_index="feature",
        line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
        rows=rows_without_B_1,
    )

    rows_without_B_1_with_updated_feature_and_value_indices = decrement_indices_after_deletion(
        lookup_column="feature_id",
        match_value="B",
        type_of_id="feature",
        type_of_index="feature",
        line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
        rows=rows_without_B_1_with_updated_value_indices,
    )

    assert rows_without_B_1_with_updated_feature_and_value_indices == GOLD_STANDARD_DUMMY_ROWS


def test_decrement_indices_after_deletion_of_feature_in_listed_values_update_is_not_necessary(
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

    rows_without_B_2, range_of_line_numbers_of_removed_rows = (
        remove_rows_with_given_content_in_lookup_column(
            lookup_column="feature_id",
            match_value="B-2",
            rows=dummy_rows_of_listed_values,
        )
    )

    line_number_of_first_removed_value = range_of_line_numbers_of_removed_rows[0]

    rows_without_B_2_with_updated_value_indices = decrement_indices_after_deletion(
        lookup_column="id",
        match_value="B",
        type_of_id="value",
        type_of_index="feature",
        line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
        rows=rows_without_B_2,
    )

    rows_without_B_2_with_updated_feature_and_value_indices = decrement_indices_after_deletion(
        lookup_column="feature_id",
        match_value="B",
        type_of_id="feature",
        type_of_index="feature",
        line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
        rows=rows_without_B_2_with_updated_value_indices,
    )

    assert rows_without_B_2_with_updated_feature_and_value_indices == GOLD_STANDARD_DUMMY_ROWS


def test_decrement_indices_after_deletion_of_value_in_listed_values_update_is_necessary(
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
    ]

    rows_without_A_1_2, range_of_line_numbers_of_removed_rows = (
        remove_rows_with_given_content_in_lookup_column(
            lookup_column="id",
            match_value="A-1-2",
            rows=dummy_rows_of_listed_values,
        )
    )

    line_number_of_first_removed_value = range_of_line_numbers_of_removed_rows[0]

    rows_without_A_1_2_with_updated_value_indices = decrement_indices_after_deletion(
        lookup_column="id",
        match_value="A-1",
        type_of_id="value",
        type_of_index="value",
        line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
        rows=rows_without_A_1_2,
    )

    assert rows_without_A_1_2_with_updated_value_indices == GOLD_STANDARD_DUMMY_ROWS


def test_decrement_indices_after_deletion_of_value_in_listed_values_update_is_not_necessary(
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
    ]

    rows_without_A_1_3, range_of_line_numbers_of_removed_rows = (
        remove_rows_with_given_content_in_lookup_column(
            lookup_column="id",
            match_value="A-1-3",
            rows=dummy_rows_of_listed_values,
        )
    )

    line_number_of_first_removed_value = range_of_line_numbers_of_removed_rows[0]

    rows_without_A_1_3_with_updated_value_indices = decrement_indices_after_deletion(
        lookup_column="id",
        match_value="A-1",
        type_of_id="value",
        type_of_index="value",
        line_number_after_which_rows_must_be_updated=line_number_of_first_removed_value,
        rows=rows_without_A_1_3,
    )

    assert rows_without_A_1_3_with_updated_value_indices == GOLD_STANDARD_DUMMY_ROWS


def test_decrement_indices_after_deletion_in_feature_profile_update_is_necessary(
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

    rows_without_A_2, (line_number_of_removed_row,) = (
        remove_rows_with_given_content_in_lookup_column(
            lookup_column="feature_id",
            match_value="A-2",
            rows=dummy_rows_of_feature_profile,
        )
    )

    rows_without_A_2_with_updated_feature_indices = decrement_indices_after_deletion(
        lookup_column="feature_id",
        match_value="A",
        type_of_id="feature",
        line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
        type_of_index="feature",
        rows=rows_without_A_2,
        rows_are_a_feature_profile=True,
    )

    for row in rows_without_A_2_with_updated_feature_indices:
        print(row)

    assert rows_without_A_2_with_updated_feature_indices == GOLD_STANDARD_DUMMY_ROWS


def test_decrement_indices_after_deletion_in_feature_profile_update_is_not_necessary(
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

    rows_without_last_feature_in_category_A, (line_number_of_removed_row,) = (
        remove_rows_with_given_content_in_lookup_column(
            lookup_column="feature_id",
            match_value="A-3",
            rows=dummy_rows_of_feature_profile,
        )
    )

    rows_without_last_feature_in_category_A_with_updated_feature_indices = (
        decrement_indices_after_deletion(
            lookup_column="feature_id",
            match_value="A",
            type_of_id="feature",
            line_number_after_which_rows_must_be_updated=line_number_of_removed_row,
            type_of_index="feature",
            rows=rows_without_last_feature_in_category_A,
            rows_are_a_feature_profile=True,
        )
    )

    assert (
        rows_without_last_feature_in_category_A_with_updated_feature_indices
        == GOLD_STANDARD_DUMMY_ROWS
    )
