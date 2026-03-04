from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from app.schemas.document import DocumentType


BANK_KEYWORDS = {
    "sbi": "SBI",
    "hdfc": "HDFC",
    "icici": "ICICI",
    "axis": "AXIS",
    "kotak": "KOTAK",
    "yes bank": "YES BANK",
}

CATEGORY_RULES = {
    "amazon": "Shopping",
    "swiggy": "Food",
    "salary": "Income",
    "fuel": "Travel",
    "electricity": "Utilities",
    "rent": "Housing",
}


@dataclass
class ParseContext:
    filename: str
    content_type: str
    text: str


class DocumentPipeline:
    """Composable pipeline for financial document parsing."""

    def detect_file_type(self, ctx: ParseContext) -> str:
        return ctx.content_type or "application/octet-stream"

    def detect_document_type(self, ctx: ParseContext) -> DocumentType:
        text = ctx.text.lower()
        if "gstin" in text or "invoice" in text:
            return DocumentType.GST_INVOICE
        if "statement" in text and "credit card" in text:
            return DocumentType.CREDIT_CARD_STATEMENT
        if "statement" in text or "account" in text:
            return DocumentType.BANK_STATEMENT
        return DocumentType.UNKNOWN

    def extract_text(self, ctx: ParseContext) -> str:
        # Placeholder: route between pdfplumber/camelot/tabula/tesseract.
        return ctx.text

    def detect_bank(self, text: str) -> str | None:
        lowered = text.lower()
        for key, bank in BANK_KEYWORDS.items():
            if key in lowered:
                return bank
        return None

    def normalize(self, raw_text: str) -> dict[str, Any]:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        txns: list[dict[str, Any]] = []
        for idx, line in enumerate(lines[:10], start=1):
            category = self.categorize(line)
            txns.append(
                {
                    "TransactionID": f"TXN-{idx}",
                    "Date": "2026-01-01",
                    "Description": line,
                    "Debit": 0.0,
                    "Credit": 0.0,
                    "Balance": None,
                    "Currency": "INR",
                    "ReferenceID": None,
                    "AccountNumber": None,
                    "BankName": self.detect_bank(raw_text),
                    "Category": category,
                }
            )
        return {"transactions": txns}

    def categorize(self, description: str) -> str | None:
        lowered = description.lower()
        for key, category in CATEGORY_RULES.items():
            if key in lowered:
                return category
        return None

    def confidence_score(self, normalized: dict[str, Any], doc_type: DocumentType) -> float:
        txns = normalized.get("transactions", [])
        base = 0.5 if doc_type == DocumentType.UNKNOWN else 0.75
        if txns:
            base += 0.15
        if any(txn.get("Category") for txn in txns):
            base += 0.1
        return min(base, 0.99)

    def dedupe_hash(self, text: str) -> str:
        return sha256(text.encode("utf-8")).hexdigest()

    def run(self, ctx: ParseContext) -> dict[str, Any]:
        extracted_text = self.extract_text(ctx)
        doc_type = self.detect_document_type(ctx)
        normalized = self.normalize(extracted_text)
        confidence = self.confidence_score(normalized, doc_type)
        return {
            "document_type": doc_type,
            "normalized": normalized,
            "confidence": confidence,
            "needs_human_review": confidence < 0.8,
            "dedupe_hash": self.dedupe_hash(extracted_text),
        }
