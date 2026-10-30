import pytest


def test_pipe_sanitization_in_table_titles():
    from src.utils.sanitizer import sanitize_table_pipes
    raw_table = "| Title | Author |\n| IFHUB | Special | Dr. Z |"
    clean = sanitize_table_pipes(raw_table)
    lines = clean.strip().split("\n")
    assert len(lines[1].split("|")) == 4  # empty, Title, Author, empty
    assert "IFHUB — Special" in lines[1]


def test_pipe_sanitization_multi_column_table():
    from src.utils.sanitizer import sanitize_table_pipes
    raw_table = (
        "| Document | Title | Focus |\n"
        "|---|---|---|\n"
        "| IFHUB | Special | Report | FinTech |\n"
        "| IRP 5 | Sukuk | Challenges | Maqasid |\n"
    )
    clean = sanitize_table_pipes(raw_table)
    lines = [line for line in clean.strip().split("\n") if line.strip()]
    # Each row must have 5 parts when split on | (empty, col1, col2, col3, empty)
    for line in lines:
        assert len(line.split("|")) == 5


def test_url_restoration_arabic_percent_encoding():
    from src.utils.sanitizer import restore_verbatim_catalog_urls
    lookup = {"shariah-perspective": "https://ifikr.my/resources/shari%ca%bfah-perspective-و/"}
    raw = "[Link](https://ifikr.my/resources/shariah-perspective)"
    restored = restore_verbatim_catalog_urls(raw, lookup)
    assert "https://ifikr.my/resources/shari%ca%bfah-perspective-و/" in restored


def test_build_final_response():
    from src.utils.sanitizer import build_final_response
    raw = "| Title | Author |\n| IFHUB | Special | Dr. Z |"
    chunks = [
        {
            "document_name": "IRP 5",
            "header_path": "/INTRODUCTION",
            "chunk_id": "c1",
            "chunk_content": "intro text",
        }
    ]
    response = build_final_response(raw, observed_chunks=chunks)
    assert "IFHUB — Special" in response.result
    assert len(response.references) == 1
    assert response.references[0].document_name == "IRP 5"
    assert response.references[0].source_url == "https://ifikr.my/resources/irp-5-challenges-maqasid-sukuk/"
