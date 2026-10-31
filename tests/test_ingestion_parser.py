import pytest
from src.skills.ingestion.parser import clean_markdown_text, parse_pdf_to_clean_markdown


def test_clean_markdown_removes_page_numbers_and_noise():
    raw_md = (
        "# Introduction\n\n"
        "Page 1 of 12\n\n"
        "This is the opening argument.\n\n"
        "--- 1 ---\n\n"
        "Second paragraph discussing financial stability.\n\n"
        "Copyright © 2024 INCEIF All rights reserved\n\n"
        "| Document | Mechanism |\n"
        "|---|---|\n"
        "| IRP 5 | True sale |\n\n"
        "12\n"
    )
    cleaned = clean_markdown_text(raw_md)
    assert "Page 1 of 12" not in cleaned
    assert "--- 1 ---" not in cleaned
    assert "Copyright © 2024" not in cleaned
    assert "This is the opening argument." in cleaned
    assert "| Document | Mechanism |" in cleaned
    assert "| IRP 5 | True sale |" in cleaned


def test_clean_markdown_handles_empty_or_whitespace():
    assert clean_markdown_text("") == ""
    assert clean_markdown_text("   \n\n  ") == ""


def test_clean_markdown_removes_picture_text_blocks():
    raw_md = (
        "Main text before diagram.\n\n"
        "<!-- Start of picture text -->\n"
        "(a) Diagram coordinate labels: Target Round 2<br>channel<br>token\n"
        "<!-- End of picture text -->\n\n"
        "Main text following the diagram."
    )
    cleaned = clean_markdown_text(raw_md)
    assert "Start of picture text" not in cleaned
    assert "End of picture text" not in cleaned
    assert "Diagram coordinate labels" not in cleaned
    assert "Main text before diagram." in cleaned
    assert "Main text following the diagram." in cleaned


def test_parse_pdf_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_pdf_to_clean_markdown("non_existent_file_xyz_123.pdf")

