from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BankRule:
    name: str
    keywords: tuple[str, ...] = field(default_factory=tuple)
    header_tokens: tuple[str, ...] = field(default_factory=tuple)
    column_tokens: tuple[str, ...] = field(default_factory=tuple)

    def score(self, text: str) -> int:
        lowered = text.lower()
        points = 0
        for kw in self.keywords:
            if kw.lower() in lowered:
                points += 50
        for token in self.header_tokens:
            if token.lower() in lowered:
                points += 20
        for col in self.column_tokens:
            if col.lower() in lowered:
                points += 10
        return points


class BankDetector:
    """Rule-driven bank detector with extensible registry."""

    def __init__(self, rules: list[BankRule] | None = None) -> None:
        self.rules = rules or self._default_rules()

    @staticmethod
    def _default_rules() -> list[BankRule]:
        common_columns = ("date", "narration", "debit", "credit", "balance")
        return [
            BankRule("HDFC", keywords=("hdfc bank",), header_tokens=("hdfc",), column_tokens=common_columns),
            BankRule("ICICI", keywords=("icici bank",), header_tokens=("icici",), column_tokens=common_columns),
            BankRule("SBI", keywords=("state bank of india", "sbi"), header_tokens=("sbi",), column_tokens=common_columns),
            BankRule("AXIS", keywords=("axis bank",), header_tokens=("axis",), column_tokens=common_columns),
        ]

    def detect(self, text: str, columns: list[str] | None = None) -> str | None:
        column_blob = " ".join(columns or [])
        composite = f"{text}\n{column_blob}".strip()
        scored = sorted(((rule.name, rule.score(composite)) for rule in self.rules), key=lambda x: x[1], reverse=True)
        if not scored or scored[0][1] <= 0:
            return None
        return scored[0][0]
