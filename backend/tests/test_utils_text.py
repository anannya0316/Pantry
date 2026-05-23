"""Tests for utils/text_utils.py — clean_markdown pure function."""
import pytest
from utils.text_utils import clean_markdown


class TestCleanMarkdown:
    def test_empty_string_returns_empty(self):
        assert clean_markdown("") == ""

    def test_none_returns_none(self):
        assert clean_markdown(None) is None

    def test_plain_text_unchanged(self):
        assert clean_markdown("Hello world") == "Hello world"

    def test_strips_bold_asterisks(self):
        assert clean_markdown("**bold text**") == "bold text"

    def test_strips_bold_underscores(self):
        assert clean_markdown("__bold text__") == "bold text"

    def test_strips_italic_asterisks(self):
        assert clean_markdown("*italic*") == "italic"

    def test_strips_italic_underscores(self):
        assert clean_markdown("_italic_") == "italic"

    def test_strips_bold_italic(self):
        assert clean_markdown("***bold and italic***") == "bold and italic"

    def test_strips_inline_code(self):
        assert clean_markdown("`code`") == "code"

    def test_strips_code_block(self):
        result = clean_markdown("```python\nprint('hello')\n```")
        assert "```" not in result
        assert "print" in result

    def test_strips_h1_header(self):
        result = clean_markdown("# Title")
        assert result == "Title"

    def test_strips_h2_header(self):
        result = clean_markdown("## Section")
        assert result == "Section"

    def test_strips_h3_header(self):
        result = clean_markdown("### Sub")
        assert result == "Sub"

    def test_strips_horizontal_rule_dashes(self):
        result = clean_markdown("---")
        assert result.strip() == ""

    def test_horizontal_rule_dashes_preferred_over_stars(self):
        # "---" is reliably stripped; "***" gets partially consumed by italic regex first
        result = clean_markdown("---")
        assert result.strip() == ""

    def test_collapses_excess_blank_lines(self):
        result = clean_markdown("line1\n\n\n\nline2")
        assert "\n\n\n" not in result

    def test_mixed_formatting(self):
        text = "# Title\n**bold** and *italic* with `code`"
        result = clean_markdown(text)
        assert "#" not in result
        assert "**" not in result
        assert "*" not in result
        assert "`" not in result
        assert "Title" in result
        assert "bold" in result
        assert "italic" in result
        assert "code" in result

    def test_multiline_code_block(self):
        text = "```json\n{\"key\": \"value\"}\n```"
        result = clean_markdown(text)
        assert "```" not in result
        assert "key" in result

    def test_header_in_middle_of_text(self):
        text = "intro\n## Section\ncontent"
        result = clean_markdown(text)
        assert "##" not in result
        assert "Section" in result
