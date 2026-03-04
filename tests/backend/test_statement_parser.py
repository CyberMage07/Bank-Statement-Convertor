from pathlib import Path

import pytest

from parsers.bank_detector import BankDetector
from parsers.pdf_extractor import PDFExtractor
from services.statement_parser import StatementParser


def _create_sample_pdf(path: Path) -> None:
    fixture = Path("tests/fixtures/sample_statement.pdf")
    path.write_bytes(fixture.read_bytes())


def test_pdf_extractor_extracts_text(tmp_path: Path):
    pytest.importorskip("pdfplumber")
    pdf_path = tmp_path / "sample_statement.pdf"
    _create_sample_pdf(pdf_path)

    extracted = PDFExtractor().extract(pdf_path)

    assert "HDFC" in extracted.text


def test_bank_detector_detects_hdfc():
    detector = BankDetector()
    bank = detector.detect("HDFC BANK STATEMENT", ["Date", "Narration", "Debit", "Credit", "Balance"])
    assert bank == "HDFC"


def test_transaction_hash_is_stable_for_duplicate_transactions():
    parser = StatementParser()
    hash1 = parser._transaction_hash("2026-01-01", "Amazon Purchase", 500.0)
    hash2 = parser._transaction_hash("2026-01-01", "Amazon Purchase", 500.0)
    assert hash1 == hash2


def test_confidence_scoring_penalizes_missing_fields():
    parser = StatementParser()
    low_quality_transactions = [
        {
            "date": "",
            "description": "Unclear row",
            "debit": 0.0,
            "credit": 0.0,
            "balance": None,
        }
    ]
    score = parser._confidence_score(low_quality_transactions)
    assert score < 70


def test_parse_pdf_returns_normalized_transactions_with_category(tmp_path: Path):
    pytest.importorskip("pdfplumber")
    pdf_path = tmp_path / "sample_statement.pdf"
    _create_sample_pdf(pdf_path)

    parser = StatementParser()
    result = parser.parse_pdf(pdf_path)

    assert result.bank_name == "HDFC"
    assert len(result.transactions) >= 1
    assert result.transactions[0]["currency"] == "INR"
    assert result.transactions[0]["transaction_hash"]
