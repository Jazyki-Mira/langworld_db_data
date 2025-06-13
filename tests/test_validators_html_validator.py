"""Tests for the HTML validator."""

import pytest

from langworld_db_data.validators.html_validator import HTMLValidator, HTMLValidatorError

# Valid HTML test cases
VALID_HTML_CASES = [
    # Empty string is valid
    "",
    # Simple paragraph
    "<p>Valid paragraph</p>",
    # Multiple paragraphs
    "<p>First paragraph</p><p>Second paragraph</p>",
    # Simple list
    "<ul><li>Item 1</li><li>Item 2</li></ul>",
    # Ordered list
    "<ol><li>First</li><li>Second</li></ol>",
    # Nested lists
    """<ul>
        <li>Item 1</li>
        <li>Item 2
            <ul>
                <li>Subitem 1</li>
                <li>Subitem 2</li>
            </ul>
        </li>
        <li>Item 3</li>
    </ul>""",
    # Mixed content
    "<p>Text before</p><ul><li>Item</li></ul><p>Text after</p>",
]

# Invalid HTML test cases with expected error messages
INVALID_HTML_CASES = [
    # Disallowed tags
    ("<div>Not allowed</div>", "Tag 'div' is not allowed"),
    ("<p><span>Span not allowed</span></p>", "Tag 'span' is not allowed"),
    # BR tags
    ("<p>Line 1<br>Line 2</p>", "Tag 'br' is not allowed"),
    # Invalid list structure
    ("<ul><p>Not an li</p></ul>", "<ul> can only contain <li> elements"),
    ("<li>Not in a list</li>", "<li> must be a direct child of <ul> or <ol>"),
    # Empty paragraphs
    ("<p></p>", "Empty <p> tags are not allowed"),
    ("<p>   </p>", "Empty <p> tags are not allowed"),
    # Nested paragraphs
    ("<p><p>Nested</p></p>", "Nested <p> tags are not allowed"),
    # Text at root level
    ("Text not in paragraph", "Text must be wrapped in a block element"),
    ("<p>Paragraph</p>And some text", "Text must be wrapped in a block element"),
    # Unescaped HTML
    ("<p>1 < 2</p>", "Text contains unescaped HTML"),
    ("<p>AT&T</p>", "Text contains unescaped HTML"),
]


@pytest.mark.parametrize("html", VALID_HTML_CASES)
def test_validate_html_valid(html):
    """Test that valid HTML passes validation."""
    HTMLValidator(html).validate()


@pytest.mark.parametrize("html,expected_error", INVALID_HTML_CASES)
def test_validate_html_invalid(html, expected_error):
    """Test that invalid HTML raises the expected error."""
    with pytest.raises(HTMLValidatorError) as excinfo:
        HTMLValidator(html).validate()
    assert expected_error in str(excinfo.value)


def test_validate_html_with_allowed_text_at_root_level():
    # Text at root level
    HTMLValidator(html="Text not in paragraph", is_text_at_root_level_allowed=True).validate()


def test_html_validation_error():
    """Test the HTMLValidationError exception."""
    error = HTMLValidatorError("Test error")
    assert str(error) == "Test error"
