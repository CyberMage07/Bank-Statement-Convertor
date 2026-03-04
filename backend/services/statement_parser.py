from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from parsers.bank_detector import BankDetector
from parsers.ocr_extractor import OCRExtractor
from parsers.pdf_extractor import PDFExtractor
from services.categorizer import TransactionCategorizer


@dataclass
class ParseResult:
    document_id: str
    bank_name: str | None
    confidence_score: int
    transactions: list[dict]
    needs_review: bool


class StatementParser:
    def __init__(
        self,
        pdf_extractor: PDFExtractor | None = None,
        ocr_extractor: OCRExtractor | None = None,
        bank_detector: BankDetector | None = None,
        categorizer: TransactionCategorizer | None = None,
    ) -> None:
        self.pdf_extractor = pdf_extractor or PDFExtractor()
        self.ocr_extractor = ocr_extractor or OCRExtractor()
        self.bank_detector = bank_detector or BankDetector()
        self.categorizer = categorizer or TransactionCategorizer()

    def parse_pdf(self, file_path: str | Path, currency: str = "INR") -> ParseResult:
        extracted = self.pdf_extractor.extract(file_path)
        text = extracted.text

        if self.pdf_extractor.has_low_text_density(text):
            ocr_text = self.ocr_extractor.extract_pdf(file_path)
            if ocr_text:
                text = ocr_text
                if not extracted.rows:
                    extracted.rows, extracted.columns = self.pdf_extractor._parse_rows([], ocr_text)

        bank_name = self.bank_detector.detect(text=text, columns=extracted.columns)
        transactions = [self._normalize_row(row, bank_name, currency) for row in extracted.rows]
        transactions = [txn for txn in transactions if txn["description"] or txn["debit"] or txn["credit"]]

        confidence = self._confidence_score(transactions)
        return ParseResult(
            document_id=str(uuid4()),
            bank_name=bank_name,
            confidence_score=confidence,
            transactions=transactions,
            needs_review=confidence < 70,
        )

    def _normalize_row(self, row: dict[str, str], bank_name: str | None, currency: str) -> dict:
        description = row.get("narration") or row.get("description") or row.get("particulars") or ""
        debit = self._to_amount(row.get("debit"))
        credit = self._to_amount(row.get("credit"))
        date = row.get("date") or row.get("txn date") or ""
        balance = self._to_amount(row.get("balance"))
        reference_id = row.get("ref") or row.get("reference") or row.get("reference_id")
        amount_for_hash = debit if debit > 0 else credit

        return {
            "date": date,
            "description": description,
            "debit": debit,
            "credit": credit,
            "balance": balance,
            "currency": currency,
            "reference_id": reference_id,
            "bank_name": bank_name,
            "category": self.categorizer.categorize(description),
            "transaction_hash": self._transaction_hash(date, description, amount_for_hash),
        }

    def _confidence_score(self, transactions: list[dict]) -> int:
        if not transactions:
            return 0
        total = len(transactions)
        penalty = 0
        for txn in transactions:
            if not txn.get("date"):
                penalty += 15
            if (txn.get("debit", 0) <= 0) and (txn.get("credit", 0) <= 0):
                penalty += 20
            if txn.get("balance") is None:
                penalty += 10
        raw = 100 - int(penalty / total)
        return max(min(raw, 100), 0)

    @staticmethod
    def _to_amount(value: str | None) -> float:
        if value is None:
            return 0.0
        cleaned = re.sub(r"[^\d.\-]", "", value)
        if not cleaned or cleaned in {"-", "."}:
            return 0.0
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @staticmethod
    def _transaction_hash(date: str, description: str, amount: float) -> str:
        payload = f"{date}|{description.strip().lower()}|{amount:.2f}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
