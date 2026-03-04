from __future__ import annotations


class TransactionCategorizer:
    def __init__(self, rules: dict[str, str] | None = None) -> None:
        self.rules = rules or {
            "amazon": "Shopping",
            "swiggy": "Food",
            "fuel": "Travel",
            "salary": "Income",
        }

    def categorize(self, description: str) -> str | None:
        lowered = description.lower()
        for keyword, category in self.rules.items():
            if keyword in lowered:
                return category
        return None
