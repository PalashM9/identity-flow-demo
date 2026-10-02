from dataclasses import dataclass
from datetime import date


@dataclass
class Decision:
    status: str
    reason: str


def normalise(value: str) -> str:
    return " ".join(value.upper().split())


def evaluate_identity(
    full_name: str,
    document_number: str,
    expires_on: date,
    ocr_text: str,
    today: date | None = None,
) -> Decision:
    today = today or date.today()
    text = normalise(ocr_text)

    name_ok = normalise(full_name) in text
    doc_ok = normalise(document_number) in text
    not_expired = expires_on >= today

    if not not_expired:
        return Decision("REJECTED", "Document is expired.")

    if not name_ok and not doc_ok:
        return Decision("REVIEW_REQUIRED", "OCR did not match name or document number.")

    if not name_ok:
        return Decision("REVIEW_REQUIRED", "OCR did not match the expected full name.")

    if not doc_ok:
        return Decision("REVIEW_REQUIRED", "OCR did not match the expected document number.")

    return Decision("VERIFIED", "Demo document fields matched and document is not expired.")