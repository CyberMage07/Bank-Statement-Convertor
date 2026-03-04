import pytest

pytest.importorskip("pydantic")

from app.schemas.document import DocumentType
from app.services.parsers.pipeline import DocumentPipeline, ParseContext


def test_pipeline_detects_bank_statement_and_category():
    pipeline = DocumentPipeline()
    ctx = ParseContext(
        filename="statement.pdf",
        content_type="application/pdf",
        text="HDFC BANK STATEMENT\nAmazon order payment",
    )

    result = pipeline.run(ctx)

    assert result["document_type"] == DocumentType.BANK_STATEMENT
    assert result["normalized"]["transactions"][1]["Category"] == "Shopping"
    assert result["confidence"] >= 0.8


def test_pipeline_flags_unknown_for_review():
    pipeline = DocumentPipeline()
    ctx = ParseContext(filename="note.txt", content_type="text/plain", text="hello")

    result = pipeline.run(ctx)

    assert result["document_type"] == DocumentType.UNKNOWN
    assert result["needs_human_review"] is True
