import re
from dataclasses import dataclass


class UnsafeInputError(ValueError):
    """Raised when input matches a high-confidence injection pattern."""


@dataclass(frozen=True)
class RedactionResult:
    text: str
    count: int


class SafetyGuard:
    _injection_patterns = (
        re.compile(r"ignore (all |any )?(previous|prior|above) instructions", re.I),
        re.compile(r"reveal (the )?(system|developer) prompt", re.I),
        re.compile(r"show (me )?(your )?(hidden|system) instructions", re.I),
        re.compile(r"bypass (the )?(safety|security|guardrail)", re.I),
    )
    _pii_patterns = (
        (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I), "[EMAIL]"),
        (re.compile(r"(?<!\w)(?:\+?44\s?7\d{3}|07\d{3})[\s-]?\d{3}[\s-]?\d{3}(?!\w)"), "[PHONE]"),
        (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[NATIONAL_ID]"),
        (re.compile(r"\b(?:\d[ -]*?){13,16}\b"), "[PAYMENT_CARD]"),
    )

    def validate_question(self, question: str) -> None:
        normalized = " ".join(question.split())
        if any(pattern.search(normalized) for pattern in self._injection_patterns):
            raise UnsafeInputError("The question contains a suspected prompt-injection pattern.")

    def redact_pii(self, text: str) -> RedactionResult:
        redacted = text
        count = 0
        for pattern, replacement in self._pii_patterns:
            redacted, substitutions = pattern.subn(replacement, redacted)
            count += substitutions
        return RedactionResult(text=redacted, count=count)
