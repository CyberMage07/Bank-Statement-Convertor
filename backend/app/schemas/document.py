from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    BANK_STATEMENT = "bank_statement"
    CREDIT_CARD_STATEMENT = "credit_card_statement"
    GST_INVOICE = "gst_invoice"
    PURCHASE_BILL = "purchase_bill"
    EXPENSE_RECEIPT = "expense_receipt"
    SALARY_SLIP = "salary_slip"
    LEDGER_EXPORT = "ledger_export"
    PAYMENT_GATEWAY_REPORT = "payment_gateway_report"
    INVESTMENT_STATEMENT = "investment_statement"
    UNKNOWN = "unknown"


class Transaction(BaseModel):
    TransactionID: str | None = None
    Date: str
    Description: str
    Debit: float | None = 0.0
    Credit: float | None = 0.0
    Balance: float | None = None
    Currency: str = "INR"
    ReferenceID: str | None = None
    AccountNumber: str | None = None
    BankName: str | None = None
    Category: str | None = None


class ParseDocumentResponse(BaseModel):
    document_id: str
    document_type: DocumentType
    confidence_score: float = Field(ge=0.0, le=1.0)
    normalized_data: dict[str, Any]
    needs_human_review: bool


class ExportRequest(BaseModel):
    export_format: str
    columns: list[str] = Field(default_factory=list)
    include_metadata: bool = True
