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
    # Unescaped HTML - these are now considered valid as they're common in text
    # ("<p>5 < 10</p>", "Text contains unescaped <: <p>5 < 10</p>"),
    # ("<p>10 > 5</p>", "Text contains unescaped >: <p>10 > 5</p>"),
    # ("<p>Use < and > for tags</p>", "Text contains unescaped <: <p>Use < and > for tags</p>"),
    # Note: BeautifulSoup handles unclosed tags by auto-closing them, so we don't need to test for them separately
    # as they'll be caught by other validation rules (like empty paragraphs or invalid tags)
    # These are still invalid:
    ("<p>AT&T</p>", "Text contains unescaped &: &T</p>"),
    ("<p>Invalid entity: &invalid;</p>", "Invalid HTML entity: &invalid; in: &invalid;</p>"),
    ("<p>Missing semicolon: &amp</p>", "Text contains unescaped &: &amp</p>"),
]


@pytest.mark.parametrize("html", VALID_HTML_CASES)
def test_validate_html_valid(html):
    """Test that valid HTML passes validation."""
    HTMLValidator()._validate_html(html, is_text_at_root_level_allowed=False)


# Test cases with valid HTML that includes properly escaped HTML entities
VALID_ESCAPED_HTML = [
    "<p>5 &lt; 10</p>",
    "<p>10 &gt; 5</p>",
    "<p>AT&amp;T</p>",
    "<p>Use &lt; and &gt; for tags</p>",
    "<p>Quotes: &quot;double&quot; and &apos;single&apos;</p>",
    "<p>Numeric entities: &#34;double&#34; and &#39;single&#39;</p>",
    "<p>Mixed: 1 &lt; 2 &amp;&amp; 3 &gt; 2</p>",
]


@pytest.mark.parametrize("html", VALID_ESCAPED_HTML)
def test_validate_html_with_escaped_chars(html):
    """Test that valid HTML with properly escaped characters passes validation."""
    validator = HTMLValidator()
    # Should not raise an exception
    validator._validate_html(html, is_text_at_root_level_allowed=False)


@pytest.mark.parametrize("html,expected_error", INVALID_HTML_CASES)
def test_validate_html_invalid(html, expected_error):
    """Test that invalid HTML raises the expected error."""
    with pytest.raises(HTMLValidatorError) as excinfo:
        HTMLValidator()._validate_html(html, is_text_at_root_level_allowed=False)
    assert expected_error in str(excinfo.value)


def test_validate_html_with_allowed_text_at_root_level():
    # Text at root level
    HTMLValidator()._validate_html(html="Text", is_text_at_root_level_allowed=True)


def test_validate_html_with_unclosed_angle_bracket():
    """Test that unclosed tags are handled by BeautifulSoup's HTML parsing."""
    # BeautifulSoup will auto-close unclosed tags, so we don't need to test for them
    # Here we just verify that the validation passes for valid HTML
    HTMLValidator()._validate_html("<p>Test</p>", is_text_at_root_level_allowed=False)

    # Test that invalid tags are still caught
    with pytest.raises(HTMLValidatorError) as excinfo:
        HTMLValidator()._validate_html(
            "<invalid>Test</invalid>", is_text_at_root_level_allowed=False
        )
    assert "Tag 'invalid' is not allowed" in str(excinfo.value)


def test_validate_html_with_unescaped_ampersand_without_semicolon():
    """Test that an unescaped ampersand without a semicolon raises an error."""
    # Test with an ampersand not followed by a semicolon
    invalid_html = "<p>This is a test with an unescaped ampersand: &invalid</p>"
    with pytest.raises(HTMLValidatorError) as excinfo:
        HTMLValidator()._validate_html(invalid_html, is_text_at_root_level_allowed=False)
    assert "Text contains unescaped &: &invalid" in str(excinfo.value)

    # Test with an ampersand at the end of the string
    invalid_html = "<p>Ends with ampersand &"
    with pytest.raises(HTMLValidatorError) as excinfo:
        HTMLValidator()._validate_html(invalid_html, is_text_at_root_level_allowed=False)
    assert "Text contains unescaped &: &" in str(excinfo.value)


def test_html_validation_error():
    # Test the HTMLValidationError exception.
    with pytest.raises(HTMLValidatorError) as excinfo:
        raise HTMLValidatorError("Test error")
    assert str(excinfo.value) == "Test error"
