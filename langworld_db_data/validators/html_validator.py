from bs4 import BeautifulSoup, Tag

from langworld_db_data.validators.validator import Validator


class HTMLValidatorError(ValueError):
    """Raised when HTML doesn't conform to the required format."""

    pass


class HTMLValidator(Validator):
    """Validator for ensuring HTML content adheres to specific formatting rules.

    This validator enforces the following rules:
    - Only allows <p>, <ul>, <ol>, and <li> tags
    - Ensures proper nesting and structure of lists
    - Validates against empty or whitespace-only paragraphs
    - Prevents nested paragraphs
    - Optionally allows/disallows text at the root level

    Args:
        html: The HTML string to validate
        is_text_at_root_level_allowed: If True, allows text nodes at the root level.
            If False (default), all text must be wrapped in block elements.
    """

    def __init__(self, html: str, is_text_at_root_level_allowed: bool = False):
        self.html = html
        self.is_text_at_root_level_allowed = is_text_at_root_level_allowed

    def validate(self) -> None:
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
            HTMLValidationError: If the HTML doesn't conform to the requirements
        """
        if not self.html:
            return  # Empty string is valid

        soup = BeautifulSoup(self.html, "html.parser")

        # Check for disallowed tags
        allowed_tags = {"p", "ul", "ol", "li"}
        for tag in soup.find_all(True):
            if tag.name not in allowed_tags:
                raise HTMLValidatorError(
                    f"Tag '{tag.name}' is not allowed. "
                    f"Only {', '.join(f'<{t}>' for t in sorted(allowed_tags))} are allowed."
                )

        # Check for <br> tags (should have been converted to paragraphs)
        for _ in soup.find_all("br"):
            raise HTMLValidatorError("<br> tags are not allowed. Use paragraphs instead.")

        # Check list structure
        for list_tag in soup.find_all(["ul", "ol"]):
            for child in list_tag.children:
                if isinstance(child, Tag) and child.name != "li":
                    raise HTMLValidatorError(
                        f"<{list_tag.name}> can only contain <li> elements, "
                        f"found <{child.name}>"
                    )

        # Check that <li> elements are direct children of <ul> or <ol>
        for li in soup.find_all("li"):
            parent = li.parent
            if parent.name not in ["ul", "ol"]:
                raise HTMLValidatorError(
                    f"<li> must be a direct child of <ul> or <ol>, "
                    f"found inside <{parent.name}>"
                )

        # Check for empty paragraphs
        for p in soup.find_all("p"):
            if not p.get_text(strip=True):
                raise HTMLValidatorError("Empty <p> tags are not allowed")

        # Check for nested paragraphs
        for p in soup.find_all("p"):
            if p.find("p"):
                raise HTMLValidatorError("Nested <p> tags are not allowed")

        # Check for text nodes at root level
        if not self.is_text_at_root_level_allowed:
            for child in soup.children:
                if isinstance(child, str) and child.strip():
                    raise HTMLValidatorError(
                        f"Text must be wrapped in a block element, found: {child[:50]}..."
                    )

        # Check for unescaped HTML in text nodes
        for text in soup.find_all(string=True):
            if not isinstance(text, str):
                continue

            # Skip whitespace-only text nodes
            if not text.strip():
                continue

            # Check for unescaped &, < or > that aren't part of an HTML entity
            if ("<" in text and not text.lstrip().startswith("<")) or ">" in text or "&" in text:
                raise HTMLValidatorError(f"Text contains unescaped HTML: {text[:50]}...")
