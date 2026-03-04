from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExtractedPDF:
    text: str
    rows: list[dict[str, str]]
    columns: list[str]


class PDFExtractor:
    TABLE_HEADER_KEYWORDS = {"date", "narration", "description", "debit", "credit", "balance"}

    def extract(self, file_path: str | Path) -> ExtractedPDF:
        try:
            import pdfplumber
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise RuntimeError("pdfplumber is required for PDF extraction") from exc

        text_chunks: list[str] = []
        table_rows: list[list[str]] = []

        with pdfplumber.open(str(file_path)) as pdf:
            for page in pdf.pages:
                text_chunks.append(page.extract_text() or "")
                for table in page.extract_tables() or []:
                    table_rows.extend(table)

        text = "\n".join(chunk for chunk in text_chunks if chunk).strip()
        rows, columns = self._parse_rows(table_rows, text)
        return ExtractedPDF(text=text, rows=rows, columns=columns)

    def has_low_text_density(self, text: str, threshold: int = 40) -> bool:
        return len(re.sub(r"\s+", "", text or "")) < threshold

    def _parse_rows(self, tables: list[list[str]], text: str) -> tuple[list[dict[str, str]], list[str]]:
        columns: list[str] = []
        parsed_rows: list[dict[str, str]] = []

        for row in tables:
            normalized = [self._clean(cell) for cell in row]
            lowered = [cell.lower() for cell in normalized]
            if not columns and self._is_header(lowered):
                columns = lowered
                continue
            if columns and any(normalized):
                parsed_rows.append(self._row_to_dict(columns, normalized))

        if parsed_rows:
            return parsed_rows, columns

        for line in text.splitlines():
            parts = [p.strip() for p in re.split(r"\s{2,}", line.strip()) if p.strip()]
            if len(parts) < 4:
                continue
            if not columns and self._looks_like_header(parts):
                columns = [p.lower() for p in parts]
                continue
            if not columns:
                columns = ["date", "narration", "debit", "credit", "balance"][: len(parts)]
            parsed_rows.append(self._row_to_dict(columns, parts))

        return parsed_rows, columns

    def _is_header(self, row: list[str]) -> bool:
        matched = len(self.TABLE_HEADER_KEYWORDS.intersection(set(row)))
        return matched >= 3

    def _looks_like_header(self, parts: list[str]) -> bool:
        lowered = [p.lower() for p in parts]
        return self._is_header(lowered)

    @staticmethod
    def _clean(value: str | None) -> str:
        return (value or "").replace("\n", " ").strip()

    def _row_to_dict(self, columns: list[str], values: list[str]) -> dict[str, str]:
        row: dict[str, str] = {}
        for idx, col in enumerate(columns):
            if idx < len(values):
                row[col] = values[idx]
        return row
