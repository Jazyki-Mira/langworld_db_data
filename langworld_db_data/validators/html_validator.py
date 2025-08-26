from tinybear.csv_xls import read_dicts_from_csv
from tinybear.html import validate_html

from langworld_db_data import ObjectWithPaths
from langworld_db_data.validators.validator import Validator


class HTMLValidator(ObjectWithPaths, Validator):
    """Validator for HTML content in feature and listed value descriptions."""

    def validate(self) -> None:
        print("Validating HTML descriptions of features")
        features_data = read_dicts_from_csv(self.input_file_with_features)
        for row in features_data:
            # Feature descriptions are often multi-paragraph and contain lists,
            # so text at root level is not allowed.
            for locale in ("en", "ru"):
                validate_html(
                    row[f"description_formatted_{locale}"], is_text_at_root_level_allowed=False
                )

        print("Validating HTML descriptions of listed values")
        values_data = read_dicts_from_csv(self.input_file_with_listed_values)
        for row in values_data:
            # Value descriptions can have text at root level.
            for locale in ("en", "ru"):
                validate_html(
                    row[f"description_formatted_{locale}"], is_text_at_root_level_allowed=True
                )


if __name__ == "__main__":
    HTMLValidator().validate()  # pragma: no cover
