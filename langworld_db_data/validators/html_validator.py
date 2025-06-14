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
        - <ul> and <ol> must only contain <li> elements
        - <li> elements must be direct children of <ul> or <ol>
        - No empty <p> tags
        - No nested <p> tags
        - No text nodes at the root level (must be wrapped in a block element)
        - No <br> tags (should be converted to paragraphs)
        - No `<` or `>` signs that aren't HTML entities
        - No unescaped & characters

        Raises:
            HTMLValidatorError: If the HTML doesn't conform to the requirements
        """
        if not html:
            return  # Empty string is valid

        soup = BeautifulSoup(html, "html.parser")
        self._validate_tags(soup)
        self._validate_br_tags(soup)
        self._validate_list_structure(soup)
        self._validate_paragraphs(soup)

        if not is_text_at_root_level_allowed:
            self._validate_root_level_text(soup)

        self._validate_absence_of_unescaped_html(html)

    def _validate_tags(self, soup: BeautifulSoup) -> None:
        """Validate that only allowed tags are present in the HTML."""
        allowed_tags = {"p", "ul", "ol", "li", "a", "i", "b", "em", "strong", "u", "sup", "sub"}
        for tag in soup.find_all(True):
            if tag.name not in allowed_tags:
                raise HTMLValidatorError(
                    f"Tag '{tag.name}' is not allowed. "
                    f"Only {', '.join(f'<{t}>' for t in sorted(allowed_tags))} are allowed."
                )

    def _validate_br_tags(self, soup: BeautifulSoup) -> None:
        """Validate that no <br> tags are present."""
        if soup.find("br"):
            raise HTMLValidatorError("<br> tags are not allowed. Use paragraphs instead.")

    def _validate_list_structure(self, soup: BeautifulSoup) -> None:
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

    def _validate_paragraphs(self, soup: BeautifulSoup) -> None:
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

    def _validate_root_level_text(self, soup: BeautifulSoup) -> None:
        """Validate that there's no text at the root level."""
        for child in soup.children:
            if isinstance(child, str) and child.strip():
                raise HTMLValidatorError(
                    f"Text must be wrapped in a block element, found: {child[:50]}..."
                )

    def _validate_absence_of_unescaped_html(self, html: str) -> None:
        """
        Validate that there are no unescaped HTML special characters.

        We need to check the original string because BeautifulSoup converts entities.
        """
        position = 0
        n = len(html)
        in_tag = False

        while position < n:
            if html[position] == "<":
                # Skip until the end of the tag
                in_tag = True
                position = html.find(">", position) + 1
                if position == 0:  # No closing '>' found
                    position = n
                in_tag = False
            elif html[position] == "&":
                self._validate_html_entity_with_ampersand(html, position)
                position = html.find(";", position + 1) + 1
                if position == 0:  # Shouldn't happen as _validate_html_entity would have raised
                    position = n
            elif html[position] in (">", '"', "'") and not in_tag:
                # These characters should be escaped outside of tags
                raise HTMLValidatorError(
                    f"Text contains unescaped {html[position]}: {html[position-20:position+30]}..."
                )
            else:
                position += 1

    @staticmethod
    def _validate_html_entity_with_ampersand(html: str, position: int) -> None:
        """Validate that an HTML entity is properly formatted."""
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


if __name__ == "__main__":
    HTMLValidator().validate()  # pragma: no cover
