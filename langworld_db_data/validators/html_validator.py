from bs4 import BeautifulSoup, Tag

from langworld_db_data import ObjectWithPaths
from langworld_db_data.tools.common.files.csv_xls import read_dicts_from_csv
from langworld_db_data.validators.validator import Validator


class HTMLValidatorError(ValueError):
    """Raised when HTML doesn't conform to the required format."""

    pass


class HTMLValidator(ObjectWithPaths, Validator):
    """Validator for ensuring HTML content adheres to specific formatting rules.

    This validator enforces the following rules:
    - Only allows block tags (<p>, <ul>, <ol>, <li>) and inline formatting tags
      (<a>, <i>, <b>, <em>, <strong>, <u>, <sup>, <sub>)
    - Ensures proper nesting and structure of lists
    - Validates against empty or whitespace-only paragraphs
    - Prevents nested paragraphs
    - Depending on file, allows/disallows text at the root level
    """

    def validate(self) -> None:
        print("Validating HTML descriptions of features")
        features_data = read_dicts_from_csv(self.input_file_with_features)
        for row in features_data:
            # Feature descriptions are often multi-paragraph and contain lists,
            # so text at root level is not allowed.
            for locale in ("en", "ru"):
                self._validate_html(
                    row[f"description_formatted_{locale}"], is_text_at_root_level_allowed=False
                )

        print("Validating HTML descriptions of listed values")
        values_data = read_dicts_from_csv(self.input_file_with_listed_values)
        for row in values_data:
            # Value descriptions can have text at root level.
            for locale in ("en", "ru"):
                self._validate_html(
                    row[f"description_formatted_{locale}"], is_text_at_root_level_allowed=True
                )

    def _validate_html(self, html: str, is_text_at_root_level_allowed: bool) -> None:
        """
        Validate that HTML conforms to our requirements.

        Requirements:
        - Only <p>, <ul>, <ol>, and <li> tags are allowed
        - No <br> tags (should be converted to paragraphs)
        - <ul> and <ol> must only contain <li> elements
        - <li> elements must be direct children of <ul> or <ol>
        - No empty <p> tags
        - No nested <p> tags
        - No text nodes at the root level (must be wrapped in a block element)
        - No `<` or `>` signs that aren't HTML entities
        - No unescaped & characters

        Raises:
            HTMLValidatorError: If the HTML doesn't conform to the requirements
        """
        if not html:
            return  # Empty string is valid

        self._check_absence_of_unescaped_ampersand(html)

        soup = BeautifulSoup(html, "html.parser")

        if not is_text_at_root_level_allowed:
            self._check_absence_of_root_level_text(soup)

        self._validate_tags(soup)
        self._validate_list_structure(soup)
        self._validate_paragraphs(soup)

    @staticmethod
    def _check_absence_of_root_level_text(soup: BeautifulSoup) -> None:
        """Validate that there's no text at the root level."""
        for child in soup.children:
            if isinstance(child, str) and child.strip():
                raise HTMLValidatorError(
                    f"Text must be wrapped in a block element, found: {child[:50]}..."
                )

    def _check_absence_of_unescaped_ampersand(self, html: str) -> None:
        """Check that there are no unescaped ampersands."""
        position = 0

        while position < len(html):
            if html[position] == "&":
                semicolon_pos = self._validate_html_entity_with_ampersand(html, position)
                position = semicolon_pos + 1
            else:
                position += 1

    @staticmethod
    def _validate_tags(soup: BeautifulSoup) -> None:
        """Validate that only allowed tags are present in the HTML."""
        allowed_tags = {"p", "ul", "ol", "li", "a", "i", "b", "em", "strong", "u", "sup", "sub"}
        for tag in soup.find_all(True):
            if tag.name not in allowed_tags:
                raise HTMLValidatorError(
                    f"Tag '{tag.name}' is not allowed. "
                    f"Only {', '.join(f'<{t}>' for t in sorted(allowed_tags))} are allowed."
                )

    @staticmethod
    def _validate_list_structure(soup: BeautifulSoup) -> None:
        """Validate the structure of lists and list items."""
        # Check list structure
        for list_tag in soup.find_all(["ul", "ol"]):
            for child in list_tag.children:
                if isinstance(child, Tag) and child.name != "li":
                    raise HTMLValidatorError(
                        f"<{list_tag.name}> can only contain <li> elements, "
                        f"found <{child.name}>: {child}"
                    )

        # Check that <li> elements are direct children of <ul> or <ol>
        for li in soup.find_all("li"):
            parent = li.parent
            if parent.name not in ["ul", "ol"]:
                raise HTMLValidatorError(
                    f"<li> must be a direct child of <ul> or <ol>, "
                    f"found inside <{parent.name}>: {li}"
                )

    @staticmethod
    def _validate_paragraphs(soup: BeautifulSoup) -> None:
        """Validate paragraph structure and content."""
        paragraphs = soup.find_all("p")

        # Check for empty paragraphs
        for p in paragraphs:
            if not p.get_text(strip=True):
                raise HTMLValidatorError("Empty <p> tags are not allowed")

        # Check for nested paragraphs
        for p in paragraphs:
            if p.find_parent("p"):
                raise HTMLValidatorError("Nested <p> tags are not allowed")

    @staticmethod
    def _validate_html_entity_with_ampersand(html: str, position: int) -> int:
        """Validate that an HTML entity is properly formatted.
        Return the position of the semicolon that closes the entity.
        """
        semicolon_pos = html.find(";", position + 1)
        if semicolon_pos == -1:
            raise HTMLValidatorError(
                f"Text contains unescaped &: {html[position:position + 50]}..."
            )

        entity = html[position + 1 : semicolon_pos]
        if not (entity.startswith("#") and entity[1:].isdigit()) and entity not in [
            "amp",
            "lt",
            "gt",
            "quot",
            "apos",
        ]:
            raise HTMLValidatorError(
                f"Invalid HTML entity: &{entity}; in: {html[position:position + 50]}..."
            )

        return semicolon_pos


if __name__ == "__main__":
    HTMLValidator().validate()  # pragma: no cover
